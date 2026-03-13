from fastapi import FastAPI
from routes.session_routes import router as session_router
from routes.test_routes import router as test_router

app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description="1-Dimensional Adaptive Testing API with AI-powered study plan generation",
    version="1.0.0",
)

from prometheus_fastapi_instrumentator import Instrumentator

app.include_router(session_router)
app.include_router(test_router)

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {
        "service": "Adaptive Diagnostic Engine",
        "version": "1.0.0",
        "docs": "/docs",
    }
