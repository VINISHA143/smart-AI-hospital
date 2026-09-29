from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.ward import router as ward_router
from app.routes.bed import router as bed_router
from app.routes.emergency_case import router as emergency_case_router
from app.routes.ai import router as ai_router


app = FastAPI(
    title="Smart Hospital AI Backend",
    description="AI-powered Smart Hospital Management System API",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(ward_router)
app.include_router(bed_router)
app.include_router(emergency_case_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "Smart Hospital AI Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "Smart Hospital AI Backend is running"
    }