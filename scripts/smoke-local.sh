#!/usr/bin/env bash
# Smoke checks for the local stack (spec: docs/specs/foundation/E1-2-local-stack.md, AC-2, AC-3).
# Expects `make up` to have run. Needs psql and the AWS CLI v2 on PATH. Called by CI (E1-3 local-stack.yml).
# Usage: scripts/smoke-local.sh (from any dir; non-zero on failure). Env overrides: DATABASE_URL, AWS_*.
set -euo pipefail

DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://capsule:capsule@localhost:5432/capsule}"
PSQL_URL="${DATABASE_URL/+asyncpg/}" # SQLAlchemy driver suffix; psql wants plain postgresql://
AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-eu-west-1}}"
export AWS_PAGER=""
BUCKET="${S3_MEDIA_BUCKET:-capsule-media-dev}"
QUEUES=(image-ingest image-ingest-dlq ai-tagging ai-tagging-dlq)
failures=0

for tool in psql aws; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found on PATH (see docs/runbooks/local-stack.md)"; exit 2; }
done

check() { # check <test name> <condition...>
  if "${@:2}"; then echo "PASS $1"; else echo "FAIL $1"; failures=$((failures + 1)); fi
}
awsl() { aws --endpoint-url "$AWS_ENDPOINT_URL" "$@"; }
# has_line <text> <regex>: some line of <text> matches <regex> (herestring avoids pipefail/SIGPIPE issues).
has_line() { grep -qE -- "$2" <<<"$1"; }

test_AC2_create_extension_vector() {
  check "AC-2 psql: create extension if not exists vector" \
    env PGOPTIONS='-c client_min_messages=warning' \
    psql "$PSQL_URL" -X -q -v ON_ERROR_STOP=1 -c 'create extension if not exists vector'
  local ext
  ext="$(psql "$PSQL_URL" -X -tAc "select extname from pg_extension where extname = 'vector'" 2>&1 || true)"
  check "AC-2 vector extension is installed" test "$ext" = "vector"
}

test_AC3_queues_listed() {
  local urls q
  urls="$(awsl sqs list-queues --query 'QueueUrls[]' --output text 2>&1 | tr '\t' '\n' || true)"
  for q in "${QUEUES[@]}"; do
    check "AC-3 sqs list-queues lists $q" has_line "$urls" "/$q\$"
  done
}

test_AC3_redrive_policies() {
  local q policy
  for q in image-ingest ai-tagging; do
    policy="$(awsl sqs get-queue-attributes --queue-url "$AWS_ENDPOINT_URL/000000000000/$q" \
      --attribute-names RedrivePolicy --query Attributes.RedrivePolicy --output text 2>&1 || true)"
    check "AC-3 $q redrives to $q-dlq" has_line "$policy" ":$q-dlq\""
    check "AC-3 $q maxReceiveCount is 5" has_line "$policy" '"maxReceiveCount": ?"?5"?[,}]'
  done
}

test_AC3_bucket_listed() {
  local buckets
  buckets="$(awsl s3 ls 2>&1 || true)"
  check "AC-3 s3 ls lists $BUCKET" has_line "$buckets" " $BUCKET\$"
}

test_AC2_create_extension_vector
test_AC3_queues_listed
test_AC3_redrive_policies
test_AC3_bucket_listed

if [ "$failures" -ne 0 ]; then echo "$failures check(s) failed"; exit 1; fi
echo "all checks passed"
