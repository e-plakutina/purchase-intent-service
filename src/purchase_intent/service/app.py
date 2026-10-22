from contextlib import asynccontextmanager

import joblib

from fastapi import FastAPI

from purchase_intent import db
from purchase_intent.config import settings
from purchase_intent.service.middleware import log_predictions
from purchase_intent.service.routes import router


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
app.middleware("http")(log_predictions)
app.include_router(router)
