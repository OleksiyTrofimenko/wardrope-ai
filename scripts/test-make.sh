#!/usr/bin/env bash
# Shell tests for the root Makefile (spec: docs/specs/foundation/E1-1-tooling.md, AC-1..AC-4).
# Each test uses a copy of the Makefile in a fresh temp repo, with stub toolchains (pnpm, uv, go, ...)
# first on PATH that log their calls. Usage: scripts/test-make.sh (from any dir; non-zero on failure).
set -euo pipefail
unset MAKEFLAGS MAKELEVEL MFLAGS

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
bin="$work/bin"
calls="$work/calls.log"
mkdir -p "$bin"
export PATH="$bin:$PATH"
failures=0

# stub <tool> <exit code>: fake tool that logs "<cwd>|<tool> <args>" and exits with <exit code>.
stub() {
  printf '#!/usr/bin/env bash\necho "$PWD|%s $*" >> "%s"\nexit %s\n' "$1" "$calls" "$2" > "$bin/$1"
  chmod +x "$bin/$1"
}
for tool in pnpm uv go golangci-lint gofmt; do stub "$tool" 0; done

# new_repo <name>: fake repo containing only a copy of the Makefile; prints its path.
new_repo() {
  mkdir -p "$work/$1"
  cp "$repo_root/Makefile" "$work/$1/Makefile"
  (cd "$work/$1" && pwd -P)
}

# run <out var> <status var> <cmd...>: run cmd, capture combined output and exit status.
run() {
  local __out __rc=0
  __out="$("${@:3}" 2>&1)" || __rc=$?
  printf -v "$1" '%s' "$__out"
  printf -v "$2" '%s' "$__rc"
}

check() { # check <test name> <condition...>
  if "${@:2}"; then echo "PASS $1"; else echo "FAIL $1"; failures=$((failures + 1)); fi
}
has() { grep -qF -- "$2" <<<"$1"; }

test_AC1_empty_repo_lint_typecheck_test_exit_0() {
  local repo out rc
  repo="$(new_repo ac1)"; : > "$calls"; SECONDS=0
  run out rc make -C "$repo" lint typecheck test
  check "AC-1 exits 0 on a repo with no areas" test "$rc" -eq 0
  check "AC-1 prints skip notices for every area" has "$out" "skip: media-worker (no services/media-worker/go.mod)"
  check "AC-1 invokes no toolchain" test ! -s "$calls"
  check "AC-1 NFR completes in < 5 s" test "$SECONDS" -lt 5
}

test_AC2_present_area_runs_and_exit_code_propagates() {
  local repo out rc
  repo="$(new_repo ac2)"
  mkdir -p "$repo/apps/web" "$repo/services/core-api" "$repo/services/media-worker"
  touch "$repo/apps/web/package.json" "$repo/services/core-api/pyproject.toml" "$repo/services/media-worker/go.mod"

  : > "$calls"; stub uv 0
  run out rc make -C "$repo" test
  check "AC-2 passing area: make test exits 0" test "$rc" -eq 0
  check "AC-2 area command runs inside the area dir" has "$(cat "$calls")" "$repo/services/core-api|uv run --frozen pytest"
  : > "$calls"; stub uv 7
  run out rc make -C "$repo" test
  check "AC-2 failing area: make test exits non-zero" test "$rc" -ne 0
  check "AC-2 failing area: exit code 7 is reported" has "$out" "Error 7"
  check "AC-2 fail fast: later area (media-worker) not run" test "$(grep -c '|go ' "$calls" || true)" -eq 0
  stub uv 0
}

test_AC3_help_lists_every_target_with_description() {
  local repo out rc target
  repo="$(new_repo ac3)"
  run out rc make -C "$repo" help
  check "AC-3 make help exits 0" test "$rc" -eq 0
  for target in $(grep -oE '^[a-z][a-z0-9_-]*:' "$repo/Makefile" | tr -d ':'); do
    check "AC-3 help describes '$target'" grep -qE "^  $target +[^ ]" <<<"$out"
  done
  run out rc make -C "$repo"
  check "AC-3 help is the default goal" has "$out" "list every target with a one-line description"
}

test_AC4_targets_work_from_any_cwd() {
  local repo out rc
  repo="$(new_repo ac4)"
  mkdir -p "$repo/services/core-api/app/deep"
  touch "$repo/services/core-api/pyproject.toml"
  : > "$calls"
  run out rc bash -c "cd '$repo/services/core-api/app/deep' && make -f '$repo/Makefile' test"
  check "AC-4 make -f from a subdirectory exits 0" test "$rc" -eq 0
  check "AC-4 make -f runs the area command in the area dir" has "$(cat "$calls")" "$repo/services/core-api|uv run --frozen pytest"

  run out rc bash -c "cd '$repo/services' && make -f '$repo/Makefile' help"
  check "AC-4 make -f help from a subdirectory lists targets" has "$out" "typecheck"

  run out rc bash -c "cd '$work' && make -C '$repo' lint"
  check "AC-4 make -C from outside the repo exits 0" test "$rc" -eq 0
}

test_AC1_empty_repo_lint_typecheck_test_exit_0
test_AC2_present_area_runs_and_exit_code_propagates
test_AC3_help_lists_every_target_with_description
test_AC4_targets_work_from_any_cwd

if [ "$failures" -ne 0 ]; then echo "$failures check(s) failed"; exit 1; fi
echo "all checks passed"
