from fastapi import FastAPI

app = FastAPI(
    title="NUC AI Core Service",
    description="Backend de telemetría y orquestación de agentes para el laboratorio",
    version="0.1.0"
)

@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "online",
        "service": "nuc-ai-core",
        "version": "0.1.0",
        "environment": "nuc-lab"
    }

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bienvenido al core de telemetría e IA del laboratorio NUC"}
