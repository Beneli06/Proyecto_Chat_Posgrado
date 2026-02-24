from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Application"}

app.include_router(api_router)