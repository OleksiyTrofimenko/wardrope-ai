# Entry points every human, agent and CI job uses. Spec: docs/specs/foundation/E1-1-tooling.md.
# Each verb delegates to the per-area toolchain (pnpm / uv / go). An area is present when its marker
# file exists; absent areas are skipped with a notice. Each verb depends on one sub-target per area
# (test -> test-web test-core-api test-media-worker); the first failing command stops the run.
# From a subdirectory: `make -C <repo-root> <target>` or `make -f <repo-root>/Makefile <target>`.
.PHONY: help up down smoke-local test lint typecheck e2e seed fmt \
	test-web test-core-api test-media-worker lint-web lint-core-api lint-media-worker \
	typecheck-web typecheck-core-api typecheck-media-worker fmt-web fmt-core-api fmt-media-worker
.DEFAULT_GOAL := help

# Absolute repo root (with trailing slash), so every target works from any CWD.
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Area marker files, relative to the repo root. Commands run inside the marker's directory.
WEB      := apps/web/package.json
CORE_API := services/core-api/pyproject.toml
MEDIA    := services/media-worker/go.mod

# $(call area,<name>,<marker>,<command>) — run <command> in the area dir, or print a skip notice.
# Written as one shell line so a non-zero exit of <command> is the exit of the recipe line.
area = @if [ -f "$(MAKEFILE_DIR)$(2)" ]; then \
	echo "==> $(1): $(3)"; cd "$(MAKEFILE_DIR)$(dir $(2))" && $(3); \
	else echo "skip: $(1) (no $(2))"; fi

help:      ## list every target with a one-line description
	@awk 'BEGIN {FS = ":.*## "} /^[a-z][a-z0-9_-]*:.*## / {printf "  %-24s %s\n", $$1, $$2}' "$(MAKEFILE_DIR)Makefile"

# Local stack (spec: docs/specs/foundation/E1-2-local-stack.md; runbook: docs/runbooks/local-stack.md).
COMPOSE := docker compose -f "$(MAKEFILE_DIR)docker-compose.yml"

up:        ## start local stack (postgres+pgvector, redis, localstack); returns once all are healthy
	$(COMPOSE) up -d --wait --wait-timeout 120

down:      ## stop local stack and delete its containers and volumes
	$(COMPOSE) down -v --remove-orphans

smoke-local: ## check the running local stack (pgvector, SQS queues, S3 bucket)
	"$(MAKEFILE_DIR)scripts/smoke-local.sh"

test: test-web test-core-api test-media-worker ## run unit/integration tests in every present area
test-web:                ## run web tests (pnpm)
	$(call area,web,$(WEB),pnpm run test)
test-core-api:           ## run core-api tests (uv + pytest)
	$(call area,core-api,$(CORE_API),uv run --frozen pytest)
test-media-worker:       ## run media-worker tests (go test)
	$(call area,media-worker,$(MEDIA),go test ./...)

lint: lint-web lint-core-api lint-media-worker ## run linters in every present area, plus shellcheck on scripts/
	@if ! command -v shellcheck >/dev/null 2>&1; then echo "skip: shellcheck (not installed)"; \
	elif [ -z "$(wildcard $(MAKEFILE_DIR)scripts/*.sh)" ]; then echo "skip: shellcheck (no scripts/*.sh)"; \
	else echo "==> shellcheck scripts/*.sh"; shellcheck $(wildcard $(MAKEFILE_DIR)scripts/*.sh); fi
lint-web:                ## run web linters (pnpm run lint)
	$(call area,web,$(WEB),pnpm run lint)
lint-core-api:           ## run core-api linters (ruff, import-linter)
	$(call area,core-api,$(CORE_API),uv run --frozen ruff check . && uv run --frozen lint-imports)
lint-media-worker:       ## run media-worker linters (golangci-lint)
	$(call area,media-worker,$(MEDIA),golangci-lint run)

typecheck: typecheck-web typecheck-core-api typecheck-media-worker ## run type checkers in every present area
typecheck-web:           ## type-check web (pnpm run typecheck)
	$(call area,web,$(WEB),pnpm run typecheck)
typecheck-core-api:      ## type-check core-api (mypy)
	$(call area,core-api,$(CORE_API),uv run --frozen mypy .)
typecheck-media-worker:  ## type-check media-worker (go build)
	$(call area,media-worker,$(MEDIA),go build ./...)

e2e:       ## run Playwright end-to-end tests (not implemented yet: E5-5)
	@echo "TODO(E5-5): playwright test"; exit 1

seed:      ## seed the local database (not implemented yet: E3-2)
	@echo "TODO(E3-2): seed local db"; exit 1

fmt: fmt-web fmt-core-api fmt-media-worker ## format code in every present area
fmt-web:                 ## format web code (pnpm run format)
	$(call area,web,$(WEB),pnpm run --if-present format)
fmt-core-api:            ## format core-api code (ruff format)
	$(call area,core-api,$(CORE_API),uv run --frozen ruff format .)
fmt-media-worker:        ## format media-worker code (gofmt)
	$(call area,media-worker,$(MEDIA),gofmt -w .)
