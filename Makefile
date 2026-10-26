.DEFAULT_GOAL := help

IMAGE   ?= purchase-intent-service:1.0
CLUSTER ?= purchase-intent
DEPLOY  := purchase-intent-service
PORT    ?= 8080
REQUEST := examples/request.json
SQL     := SELECT request_id, ts, model_version, score, latency_ms, response_code FROM predictions ORDER BY ts DESC LIMIT 5

.PHONY: help install data lint format test serve up down logs compose kind-up kind-deploy kind kind-down

help: ## Список команд
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Установить зависимости всех групп
	uv sync --all-groups

data: ## Скачать датасет в data/
	uv run --group data python scripts/download_dataset.py

lint: ## Проверить код линтером
	uv run ruff check .
	uv run ruff format --check .

format: ## Отформатировать код
	uv run ruff check --fix .
	uv run ruff format .

test: ## Запустить тесты
	uv run pytest

serve: ## Запустить API локально на :8000 (остановка Ctrl+C)
	uv run uvicorn purchase_intent.service.app:app --reload --port 8000

up: ## Поднять сервис и Postgres в Docker Compose
	docker compose up -d --build --wait

down: ## Остановить Docker Compose
	docker compose down

logs: ## Логи сервиса в Docker Compose (остановка Ctrl+C)
	docker compose logs -f api

compose: up ## Compose: запрос к модели и последние строки таблицы логов
	curl -sf --retry 30 --retry-delay 2 --retry-all-errors -X POST localhost:8000/v1/predict \
		-H "Content-Type: application/json" -d @$(REQUEST)
	@echo
	@sleep 1
	docker compose exec -T db psql -U postgres -d purchase_intent -c "$(SQL)"

kind-up:
	kind get clusters | grep -qx $(CLUSTER) || kind create cluster --name $(CLUSTER)
	kubectl config use-context kind-$(CLUSTER)

kind-deploy: kind-up ## Собрать образ, загрузить в kind и применить манифесты
	docker build -t $(IMAGE) .
	kind load docker-image $(IMAGE) --name $(CLUSTER)
	@if kubectl get deploy/$(DEPLOY) >/dev/null 2>&1; then \
		kubectl apply -f k8s/ && kubectl rollout restart deploy/$(DEPLOY); \
	else \
		kubectl apply -f k8s/; \
	fi
	kubectl rollout status deploy/$(DEPLOY) --timeout=180s
	kubectl get pods -l app=purchase-intent

kind: kind-deploy ## Kubernetes: деплой в kind и запрос к модели через port-forward
	kubectl port-forward svc/$(DEPLOY) $(PORT):80 >/dev/null & PF=$$!; \
	trap "kill $$PF" EXIT; \
	curl -sf --retry 15 --retry-delay 1 --retry-all-errors -X POST localhost:$(PORT)/v1/predict \
		-H "Content-Type: application/json" -d @$(REQUEST); \
	echo

kind-down: ## Удалить кластер kind
	kind delete cluster --name $(CLUSTER)
