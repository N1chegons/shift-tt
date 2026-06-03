from fastapi import FastAPI

app = FastAPI(
    title="Test Task SHIFT",
    description="Test task for SHIFT",
)

@app.get("/")
async def root():
    return {"message": "Hello World"}