#!/bin/bash
# LocalStack ready.d hook: creates the S3 bucket and SQS queues from .env.example.
# Spec: docs/specs/foundation/E1-2-local-stack.md. Idempotent: safe on every container start.
set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-eu-west-1}"
BUCKET="capsule-media-dev"
MAX_RECEIVE_COUNT=5

log() { echo "capsule-init: $*"; }

# create_queue <name> [attributes json] -> prints the queue URL
create_queue() {
  if [ $# -gt 1 ]; then
    awslocal sqs create-queue --queue-name "$1" --attributes "$2" --query QueueUrl --output text
  else
    awslocal sqs create-queue --queue-name "$1" --query QueueUrl --output text
  fi
}

queue_arn() {
  awslocal sqs get-queue-attributes --queue-url "$1" --attribute-names QueueArn \
    --query Attributes.QueueArn --output text
}

for main in image-ingest ai-tagging; do
  dlq_url="$(create_queue "$main-dlq")"
  log "queue $main-dlq ready"
  dlq_arn="$(queue_arn "$dlq_url")"
  # RedrivePolicy is a JSON string inside the attributes JSON, hence the escaped quotes.
  redrive="{\\\"deadLetterTargetArn\\\":\\\"$dlq_arn\\\",\\\"maxReceiveCount\\\":\\\"$MAX_RECEIVE_COUNT\\\"}"
  create_queue "$main" "{\"RedrivePolicy\":\"$redrive\"}" > /dev/null
  log "queue $main ready (redrive -> $main-dlq after $MAX_RECEIVE_COUNT receives)"
done

if awslocal s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  log "bucket $BUCKET already exists"
else
  awslocal s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
    --create-bucket-configuration "LocationConstraint=$REGION" > /dev/null
  log "bucket $BUCKET created in $REGION"
fi

log "done"
