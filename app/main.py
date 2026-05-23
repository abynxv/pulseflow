from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import init_db
from app.routers.parse import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ParseFlow",
    description="Convert messy documents into clean structured JSON using AI.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
