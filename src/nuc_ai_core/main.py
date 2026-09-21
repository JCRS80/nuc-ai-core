from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session, init_db
from .models import TelemetryEvent
from datetime import datetime
from typing import Optional

app = FastAPI(title="nuc-ai-core", version="0.1.0")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/health")
async def health():
    return {
        "status": "online",
        "service": "nuc-ai-core",
        "version": "0.1.0",
        "environment": "nuc-lab"
    }

@app.post("/telemetry", response_model=TelemetryEvent)
async def post_telemetry(event: TelemetryEvent, session: AsyncSession = Depends(get_session)):
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event

@app.get("/telemetry")
async def get_telemetry(
    device_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(TelemetryEvent)
    if device_id:
        query = query.where(TelemetryEvent.device_id == device_id)
    result = await session.execute(query)
    return result.scalars().all()
