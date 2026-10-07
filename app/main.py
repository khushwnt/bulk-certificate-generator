from contextlib import asynccontextmanager

import os

from fastapi import FastAPI

from app.config import OUTPUT_DIR
from app.database import init_db
from app.routers import certificates, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="Bulk Certificate Generator", lifespan=lifespan)
app.include_router(jobs.router)
app.include_router(certificates.router)
