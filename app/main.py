from fastapi import FastAPI

app = FastAPI(
    title="Blog Platform API",
    description="Blog Platform API for Python Course Final Project",
    version="0.0.1",
)


@app.get("/")
async def root():
    return {"message": "Hello from pythoncoursefinalproject!"}
