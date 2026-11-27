from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router

app = FastAPI(
    title="Blog Platform API",
    description="Blog Platform API for Python Course Final Project",
    version="0.0.1",
)

app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello from pythoncoursefinalproject!"}
