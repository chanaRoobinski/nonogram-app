"""FastAPI application entry point. Run with:

    uvicorn nonogram.api.main:app --reload

Interactive docs are then available at /docs (Swagger UI) and /redoc, and
the raw OpenAPI schema at /openapi.json.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nonogram.api.routers.generator_router import router as generator_router
from nonogram.api.routers.solver_router import router as solver_router

app = FastAPI(title="Nonogram API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generator_router)
app.include_router(solver_router)
