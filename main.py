from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from database import engine, Base

import models

from routers import (
    auth,
    doctors,
    patients,
    appointments
)


# =========================
# DATABASE SETUP
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# LOGGING SETUP
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Doctor Patient Backend API",
    description="Backend application for managing doctors, patients and appointments",
    version="1.0.0"
)


# =========================
# RESPONSE TIME MIDDLEWARE
# =========================

@app.middleware("http")
async def measure_response_time(request, call_next):

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = (
        f"{process_time:.4f}"
    )

    logger.info(
        "%s %s completed in %.4f seconds",
        request.method,
        request.url.path,
        process_time
    )

    return response


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API VERSION 1
# =========================

app.include_router(
    auth.router,
    prefix="/api/v1"
)

app.include_router(
    doctors.router,
    prefix="/api/v1"
)

app.include_router(
    patients.router,
    prefix="/api/v1"
)

app.include_router(
    appointments.router,
    prefix="/api/v1"
)


# =========================
# HOME
# =========================

@app.get("/")
def home():

    logger.info(
        "Home endpoint was called"
    )

    return {
        "message": "Doctor Patient Backend API is running"
    }