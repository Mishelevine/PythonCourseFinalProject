from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.post import router as post_router
from app.api.v1.post_category import router as post_category_router
from app.api.v1.post_comment import router as post_comment_router
from app.api.v1.post_like import router as post_like_router
from app.api.v1.user import router as user_router

app = FastAPI(
    title="Blog Platform API",
    description="Blog Platform API for Python Course Final Project",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(post_category_router)
app.include_router(post_router)
app.include_router(post_comment_router)
app.include_router(post_like_router)


@app.get("/")
async def root():
    return {"message": "Hello from pythoncoursefinalproject!"}
