from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.database import connect_db, disconnect_db
from api.routers import ai, analytics, auth, rag, reports, transactions, user
from api.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_db()
    start_scheduler()
    yield
    stop_scheduler()
    await disconnect_db()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CLIENT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Finora FastAPI server is running"}


app.include_router(auth.router, prefix=f"{settings.API_BASE_PATH}/auth", tags=["auth"])
app.include_router(user.router, prefix=f"{settings.API_BASE_PATH}/user", tags=["user"])
app.include_router(transactions.router, prefix=f"{settings.API_BASE_PATH}/transaction", tags=["transaction"])
app.include_router(analytics.router, prefix=f"{settings.API_BASE_PATH}/analytics", tags=["analytics"])
app.include_router(reports.router, prefix=f"{settings.API_BASE_PATH}/report", tags=["report"])
app.include_router(ai.router, prefix=f"{settings.API_BASE_PATH}/ai", tags=["ai"])
app.include_router(rag.router, prefix=f"{settings.API_BASE_PATH}/rag", tags=["rag"])
