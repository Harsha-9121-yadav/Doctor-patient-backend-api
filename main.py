from fastapi import FastAPI

from database import engine, Base
import models

from routers import auth, doctors, patients


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Doctor Patient Backend API",
    description="Backend application for managing doctors and patients",
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)


@app.get("/")
def home():
    return {
        "message": "Doctor Patient Backend API is running"
    }