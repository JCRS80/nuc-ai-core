from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://lab-qdrant:6333")
COLLECTION_NAME = "nuc-lab-docs"
VECTOR_SIZE = 384

client = AsyncQdrantClient(url=QDRANT_URL)

async def init_collection():
    existing = await client.get_collections()
    names = [c.name for c in existing.collections]
    if COLLECTION_NAME not in names:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

async def insert_vector(id: int, vector: list[float], payload: dict):
    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=id, vector=vector, payload=payload)]
    )

async def search_vectors(vector: list[float], limit: int = 5):
    results = await client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit
    )
    return results
