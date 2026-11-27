from fastapi import FastAPI

from app.api.v1.auth import router as auth_router

app = FastAPI(
    title="Blog Platform API",
    description="Blog Platform API for Python Course Final Project",
    version="0.0.1",
)

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello from pythoncoursefinalproject!"}
