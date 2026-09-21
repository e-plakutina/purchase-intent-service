import time
import uuid

from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException

from pydantic import BaseModel, Field

from purchase_intent import db
from purchase_intent.config import settings


class Features(BaseModel):
    model_config = {"extra": "forbid"}

    Administrative: int = Field(ge=0, le=30)
    Administrative_Duration: float = Field(ge=0, le=3500)
    Informational: int = Field(ge=0, le=30)
    Informational_Duration: float = Field(ge=0, le=3000)
    ProductRelated: int = Field(ge=0, le=1000)
    ProductRelated_Duration: float = Field(ge=0, le=60000)
    BounceRates: float = Field(ge=0, le=1)
    ExitRates: float = Field(ge=0, le=1)
    PageValues: float | None = Field(default=None, ge=0, le=400)
    SpecialDay: float = Field(ge=0, le=1)
    Month: str
    OperatingSystems: int = Field(ge=1, le=8)
    Browser: int = Field(ge=1, le=13)
    Region: int = Field(ge=1, le=9)
    TrafficType: int = Field(ge=1, le=20)
    VisitorType: str
    Weekend: bool
    # Revenue: bool


class Prediction(BaseModel):
    score: float
    purchase: bool
    model_version: str
    request_id: str
    latency_ms: float
    response_code: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    bundle = joblib.load(settings.model_path)
    app.state.pipeline = bundle["pipeline"]
    app.state.meta = bundle["metadata"]
    app.state.version = bundle["metadata"]["model_version"]

    db.init()
    yield
    app.state.pipeline = None


app = FastAPI(title="purchase-intent-service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": getattr(app.state, "version", "unknown")}


@app.get("/ready")
def ready():
    if getattr(app.state, "pipeline", "None") is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {"status": "ready"}


@app.post("/v1/predict")
def predict(X: Features, bg: BackgroundTasks) -> Prediction:
    t0 = time.perf_counter()
    request_id = str(uuid.uuid4())
    payload = X.model_dump()
    payload["Weekend"] = int(payload["Weekend"])
    frame = pd.DataFrame([payload]).reindex(columns=app.state.meta["features"])

    score = float(app.state.pipeline.predict_proba(frame)[0, 1])

    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    response_code = 200
    bg.add_task(
        db.save_prediction,
        request_id,
        payload,
        score,
        app.state.version,
        latency_ms,
        response_code,
    )

    purchase = score >= app.state.meta["threshold"]

    return Prediction(
        score=score,
        purchase=purchase,
        model_version=app.state.version,
        request_id=request_id,
        latency_ms=latency_ms,
        response_code=response_code,
    )
