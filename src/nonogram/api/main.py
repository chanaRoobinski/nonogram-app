from fastapi import FastAPI

from nonogram.api.routers.generator_router import router as generator_router
from nonogram.api.routers.solver_router import router as solver_router

app = FastAPI(title="Nonogram API", version="0.1.0")
app.include_router(generator_router)
app.include_router(solver_router)
