# Entry points every human, agent and CI job uses. Spec: docs/specs/foundation/E1-1-tooling.md.
# Each verb delegates to the per-area toolchain (pnpm / uv / go). An area is present when its marker
# file exists; absent areas are skipped with a notice. The first failing command stops the run.
# From a subdirectory: `make -C <repo-root> <target>` or `make -f <repo-root>/Makefile <target>`.
.PHONY: help up down test lint typecheck e2e seed fmt
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
	@awk 'BEGIN {FS = ":.*## "} /^[a-z][a-z0-9_-]*:.*## / {printf "  %-10s %s\n", $$1, $$2}' "$(MAKEFILE_DIR)Makefile"

up:        ## start local stack (postgres+pgvector, redis, localstack)
	docker compose up -d

down:      ## stop local stack and delete its volumes
	docker compose down -v

test:      ## run unit/integration tests in every present area
	$(call area,web,$(WEB),pnpm run test)
	$(call area,core-api,$(CORE_API),uv run --frozen pytest)
	$(call area,media-worker,$(MEDIA),go test ./...)

lint:      ## run linters in every present area, plus shellcheck on scripts/
	$(call area,web,$(WEB),pnpm run lint)
	$(call area,core-api,$(CORE_API),uv run --frozen ruff check . && uv run --frozen lint-imports)
	$(call area,media-worker,$(MEDIA),golangci-lint run)
	@if ! command -v shellcheck >/dev/null 2>&1; then echo "skip: shellcheck (not installed)"; \
	elif [ -z "$(wildcard $(MAKEFILE_DIR)scripts/*.sh)" ]; then echo "skip: shellcheck (no scripts/*.sh)"; \
	else echo "==> shellcheck scripts/*.sh"; shellcheck $(wildcard $(MAKEFILE_DIR)scripts/*.sh); fi

typecheck: ## run type checkers in every present area
	$(call area,web,$(WEB),pnpm run typecheck)
	$(call area,core-api,$(CORE_API),uv run --frozen mypy .)
	$(call area,media-worker,$(MEDIA),go vet ./...)

e2e:       ## run Playwright end-to-end tests (not implemented yet: E5-5)
	@echo "TODO(E5-5): playwright test"; exit 1

seed:      ## seed the local database (not implemented yet: E3-2)
	@echo "TODO(E3-2): seed local db"; exit 1

fmt:       ## format code in every present area
	$(call area,web,$(WEB),pnpm run --if-present format)
	$(call area,core-api,$(CORE_API),uv run --frozen ruff format .)
	$(call area,media-worker,$(MEDIA),gofmt -w .)
