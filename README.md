## Команды для выполнения

```
git clone https://github.com/e-plakutina/purchase-intent-service.git
```

```
uv sync
uv run pytest
uv run uvicorn purchase_intent.service.app:app ‐‐port 8000
```

```
docker build ‐t purchase-intent:1.0 .
docker compose up ‐d ‐‐build
```

```
kind create cluster ‐‐name purchase-intent
kind load docker‐image purchase-intent‐service:1.0 ‐‐name purchase-intent
kubectl apply ‐f k8s/
kubectl rollout status deploy/purchase-intent‐service
kubectl port‐forward svc/purchase-intent‐service 8080:80
curl ‐X POST localhost:8080/v1/predict ‐H "Content‐Type: application/json" ‐d @good.json
```
