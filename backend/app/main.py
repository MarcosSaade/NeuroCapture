from fastapi import FastAPI
from app.api.v1.endpoints import test

app = FastAPI()
app.include_router(test.router, prefix="/api/v1")


@app.get("/ping")
async def ping():
    return {"message": "pong"}
