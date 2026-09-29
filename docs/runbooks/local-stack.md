# Runbook: local stack (docker-compose)

Spec: `docs/specs/foundation/E1-2-local-stack.md` · Files: `docker-compose.yml`, `infra/local/localstack-init.sh`,
`scripts/smoke-local.sh`.

## What runs

| Service | Image | Host port | Health |
| --- | --- | --- | --- |
| `postgres` (+pgvector) | `pgvector/pgvector:pg16` | `127.0.0.1:5432` | `pg_isready` |
| `redis` | `redis:7-alpine` | `127.0.0.1:6379` | `redis-cli ping` |
| `localstack` (S3, SQS) | `localstack/localstack:4.14.0` | `127.0.0.1:4566` | init script finished without errors |

LocalStack creates bucket `capsule-media-dev` and queues `image-ingest`, `ai-tagging` (each redriving to its
`-dlq` after 5 receives) in `eu-west-1` on every container start. It keeps no state: a restart recreates everything empty.

**One shared stack per machine.** The compose project name is fixed to `capsule`, so every clone and worktree
talks to the same containers. `make down` in any worktree stops the stack for all of them.

## Everyday commands

```bash
make up            # returns once all three services are healthy (fails after 120 s otherwise)
make smoke-local   # pgvector, the four queues + redrive policies, the bucket
make down          # removes containers, network and the postgres volume (all local data)
```

The smoke script needs `psql` and the AWS CLI v2 on PATH. It reads `DATABASE_URL` (the `+asyncpg` suffix is
stripped for psql), `AWS_ENDPOINT_URL`, `AWS_REGION` and defaults to the `.env.example` values.
For ad-hoc AWS CLI calls, LocalStack accepts any credentials:

```bash
export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-1
aws --endpoint-url http://localhost:4566 sqs list-queues
aws --endpoint-url http://localhost:4566 s3 ls
```

## Troubleshooting

**`make up` fails with "port is already allocated" / "address already in use".** Something else holds the port
(often a Homebrew `postgres` or `redis`). Find it with `lsof -nP -iTCP:6379 -sTCP:LISTEN`. Either stop it, or move
the stack: `REDIS_PORT=6380 make up` (also `POSTGRES_PORT`, `LOCALSTACK_PORT`) and point `REDIS_URL` /
`DATABASE_URL` / `AWS_ENDPOINT_URL` in your `.env` at the new port.

**`make up` times out on `localstack`.** The init script failed or is slow. Check:

```bash
docker logs capsule-localstack-1 2>&1 | grep -E 'capsule-init|ERROR'
curl -s http://localhost:4566/_localstack/init/ready
```

A script `"state": "ERROR"` keeps the container unhealthy on purpose, so a broken init script makes `make up`
fail only after the healthcheck retries run out (about 95 s) — expected, not a hang. Fix `infra/local/localstack-init.sh`, then
`make down && make up`. If the log mentions an auth token, the image tag was changed: only the pinned 4.x
community tag runs without one — do not add a token, raise it with the lead.

**Smoke says a queue or the bucket is missing right after a restart.** LocalStack was restarted on its own
(`docker restart`) and the smoke ran before it turned healthy. Wait for `docker compose -p capsule ps` to show
`healthy`, or just `make up` again (it is a no-op when everything is running).

**Database is in a weird state / want a clean slate.** `make down && make up`. This deletes all local Postgres data.

**Docker disk full.** `docker system df`; prune unused images with `docker image prune` (never `-a` on a shared
machine without asking).
