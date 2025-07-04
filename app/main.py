from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="elevator-sim API",
    description="Stores simulation metadata and elevator requests for model training",
    version="0.1.0"
)

# Include the endpoints
app.include_router(router)
