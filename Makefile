# Entry points every human and agent uses. Filled in during E1-1; targets must keep these names.
.PHONY: up down test lint typecheck e2e seed fmt

up:        ## start local stack (postgres+pgvector, redis, localstack)
	docker compose up -d

down:
	docker compose down -v

test:      ## run all unit/integration tests (per-area targets added in E1-1)
	@echo "TODO(E1-1): pnpm test && uv run pytest && go test ./..."; exit 1

lint:      ## all linters
	@echo "TODO(E1-1): ruff, eslint, golangci-lint, tflint"; exit 1

typecheck:
	@echo "TODO(E1-1): tsc --noEmit && mypy"; exit 1

e2e:
	@echo "TODO(E5-5): playwright test"; exit 1

seed:
	@echo "TODO(E3-2): seed local db"; exit 1

fmt:
	@echo "TODO(E1-3): ruff format, prettier, gofmt, terraform fmt"; exit 1
