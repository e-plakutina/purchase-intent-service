import time
import uuid

from fastapi import BackgroundTasks, Request
from fastapi.responses import JSONResponse

from purchase_intent import db


async def log_predictions(request: Request, call_next):
    if request.url.path != "/v1/predict":
        return await call_next(request)

    request.state.request_id = str(uuid.uuid4())
    t0 = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as e:
        response = JSONResponse({"detail": str(e)}, status_code=500)

    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    response.headers["X-Request-Id"] = request.state.request_id

    tasks = BackgroundTasks()
    tasks.add_task(
        db.save_prediction,
        request.state.request_id,
        getattr(request.state, "features", None),
        getattr(request.state, "score", None),
        request.app.state.version,
        latency_ms,
        response.status_code,
    )
    response.background = tasks

    return response
