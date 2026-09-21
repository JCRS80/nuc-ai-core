from fastapi import FastAPI, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session, init_db
from .models import TelemetryEvent
from .vector_store import init_collection, insert_vector, search_vectors
from pydantic import BaseModel
from typing import Optional
import random

app = FastAPI(title="nuc-ai-core", version="0.2.0")

@app.on_event("startup")
async def on_startup():
    await init_db()
    await init_collection()

@app.get("/health")
async def health():
    return {"status": "online", "service": "nuc-ai-core", "version": "0.2.0", "environment": "nuc-lab"}

@app.post("/telemetry", response_model=TelemetryEvent)
async def post_telemetry(event: TelemetryEvent, session: AsyncSession = Depends(get_session)):
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event

@app.get("/telemetry")
async def get_telemetry(device_id: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    query = select(TelemetryEvent)
    if device_id:
        query = query.where(TelemetryEvent.device_id == device_id)
    result = await session.execute(query)
    return result.scalars().all()

class IndexRequest(BaseModel):
    id: int
    text: str
    payload: dict = {}

class SearchRequest(BaseModel):
    vector: list[float]
    limit: int = 5

@app.post("/index")
async def index_document(req: IndexRequest):
    vector = [random.uniform(-1, 1) for _ in range(384)]
    await insert_vector(req.id, vector, {"text": req.text, **req.payload})
    return {"status": "indexed", "id": req.id}

@app.post("/search")
async def search(req: SearchRequest):
    results = await search_vectors(req.vector, req.limit)
    return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]
