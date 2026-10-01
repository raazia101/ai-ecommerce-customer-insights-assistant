import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger("ml_api")


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "06_ml"
    / "artifacts"
    / "model_pipeline.joblib"
)

MODEL_VERSION = "week5-logistic-regression-v1"


# ============================================================
# MODEL FEATURES
# ============================================================

MODEL_FEATURES = [
    "country",
    "status",
    "customer_tenure_days",
    "completed_order_count",
    "completed_revenue",
    "average_order_value",
    "days_since_last_purchase",
    "has_previous_purchase",
    "total_transaction_count",
    "failed_transaction_count",
    "refunded_transaction_count",
    "unique_products_purchased",
    "unique_categories_purchased",
    "total_event_count",
    "product_view_count",
    "add_to_cart_count",
    "checkout_started_count",
    "search_count",
    "login_count",
    "purchase_count",
    "remove_from_cart_count",
]


# ============================================================
# GLOBAL MODEL
# ============================================================

model = None


# ============================================================
# REQUEST SCHEMA
# ============================================================

class PredictionRequest(BaseModel):
    """
    Strict request schema for repeat-purchase prediction.
    """

    model_config = ConfigDict(extra="forbid")

    customer_id: Optional[str] = None

    country: str = Field(min_length=1)
    status: str = Field(min_length=1)

    customer_tenure_days: float = Field(ge=0)
    completed_order_count: int = Field(ge=0)
    completed_revenue: float = Field(ge=0)
    average_order_value: float = Field(ge=0)

    days_since_last_purchase: Optional[float] = Field(
        default=None,
        ge=0,
    )

    has_previous_purchase: int = Field(
        ge=0,
        le=1,
    )

    total_transaction_count: int = Field(ge=0)
    failed_transaction_count: int = Field(ge=0)
    refunded_transaction_count: int = Field(ge=0)

    unique_products_purchased: int = Field(ge=0)
    unique_categories_purchased: int = Field(ge=0)

    total_event_count: int = Field(ge=0)
    product_view_count: int = Field(ge=0)
    add_to_cart_count: int = Field(ge=0)
    checkout_started_count: int = Field(ge=0)
    search_count: int = Field(ge=0)
    login_count: int = Field(ge=0)
    purchase_count: int = Field(ge=0)
    remove_from_cart_count: int = Field(ge=0)


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class PredictionResponse(BaseModel):
    customer_id: Optional[str] = None
    prediction: int
    probability: float
    model_version: str
    request_id: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ============================================================
# STRUCTURED LOGGING HELPER
# ============================================================

def log_event(
    event: str,
    request_id: str,
    **fields,
):
    """
    Write a structured JSON log entry.
    """

    payload = {
        "event": event,
        "request_id": request_id,
        **fields,
    }

    logger.info(
        json.dumps(
            payload,
            default=str,
        )
    )


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global model

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model artifact not found: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    log_event(
        event="model_loaded",
        request_id="startup",
        model_version=MODEL_VERSION,
        model_path=str(MODEL_PATH),
    )

    yield

    model = None

    log_event(
        event="model_unloaded",
        request_id="shutdown",
        model_version=MODEL_VERSION,
    )


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="E-commerce Customer Insights Assistant",
    description="ML inference API for repeat-purchase prediction.",
    version="0.7.0",
    lifespan=lifespan,
)


# ============================================================
# REQUEST ID MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_event(
            event="request_failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=500,
            latency_ms=round(elapsed_ms, 2),
        )

        raise

    elapsed_ms = (
        time.perf_counter() - start_time
    ) * 1000

    response.headers["X-Request-ID"] = request_id

    log_event(
        event="request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=round(elapsed_ms, 2),
    )

    return response


# ============================================================
# VALIDATION ERROR HANDLER
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(
        request.state,
        "request_id",
        str(uuid.uuid4()),
    )

    log_event(
        event="validation_error",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "request_id": request_id,
            }
        },
        headers={
            "X-Request-ID": request_id,
        },
    )


# ============================================================
# GENERAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        str(uuid.uuid4()),
    )

    logger.exception(
        json.dumps(
            {
                "event": "internal_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
            }
        )
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "request_id": request_id,
            }
        },
        headers={
            "X-Request-ID": request_id,
        },
    )


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health(
    request: Request,
):
    return {
        "status": "ok",
        "request_id": request.state.request_id,
    }


# ============================================================
# READINESS ENDPOINT
# ============================================================

@app.get("/ready")
def ready(
    request: Request,
):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    return {
        "status": "ready",
        "model_version": MODEL_VERSION,
        "request_id": request.state.request_id,
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    request: Request,
    payload: PredictionRequest,
):

    request_id = request.state.request_id

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    customer_id = payload.customer_id

    input_data = pd.DataFrame(
        [
            payload.model_dump(
                exclude={
                    "customer_id",
                }
            )
        ],
        columns=MODEL_FEATURES,
    )

    start_time = time.perf_counter()

    try:

        prediction = int(
            model.predict(input_data)[0]
        )

        probabilities = model.predict_proba(
            input_data
        )[0]

        class_index = list(
            model.classes_
        ).index(1)

        probability = float(
            probabilities[class_index]
        )

    except Exception:

        logger.exception(
            json.dumps(
                {
                    "event": "prediction_error",
                    "request_id": request_id,
                }
            )
        )

        raise HTTPException(
            status_code=500,
            detail="Prediction failed.",
        )

    inference_ms = (
        time.perf_counter() - start_time
    ) * 1000

    log_event(
        event="prediction_completed",
        request_id=request_id,
        model_version=MODEL_VERSION,
        prediction=prediction,
        inference_ms=round(
            inference_ms,
            2,
        ),
    )

    return PredictionResponse(
        customer_id=customer_id,
        prediction=prediction,
        probability=probability,
        model_version=MODEL_VERSION,
        request_id=request_id,
    )