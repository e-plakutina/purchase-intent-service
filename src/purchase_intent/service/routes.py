import time

import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from purchase_intent.service.schemas import (
    BatchFeatures,
    BatchItem,
    BatchPrediction,
    Features,
    Prediction,
)

router = APIRouter()


@router.get("/health")
def health(request: Request):
    return {
        "status": "ok",
        "model_version": getattr(request.app.state, "version", "unknown"),
    }


@router.get("/ready")
def ready(request: Request):
    if getattr(request.app.state, "pipeline", None) is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@router.post("/v1/predict")
def predict(X: Features, request: Request) -> Prediction:
    payload = X.model_dump()
    frame = pd.DataFrame([payload]).reindex(columns=request.app.state.meta["features"])

    score = float(request.app.state.pipeline.predict_proba(frame)[0, 1])

    request.state.score = score

    purchase = score >= request.app.state.meta["threshold"]

    latency_ms = round((time.perf_counter() - request.state.t0) * 1000, 2)

    return Prediction(
        score=score,
        purchase=purchase,
        model_version=request.app.state.version,
        request_id=request.state.request_id,
        latency_ms=latency_ms,
    )


@router.post("/v1/predict/batch")
def predict_batch(batch: BatchFeatures, request: Request) -> BatchPrediction:
    t0 = time.perf_counter()
    frame = pd.DataFrame([row.model_dump() for row in batch.rows]).reindex(
        columns=request.app.state.meta["features"]
    )

    scores = request.app.state.pipeline.predict_proba(frame)[:, 1].tolist()
    threshold = request.app.state.meta["threshold"]

    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    return BatchPrediction(
        predictions=[BatchItem(score=s, purchase=s >= threshold) for s in scores],
        model_version=request.app.state.version,
        latency_ms=latency_ms,
    )
