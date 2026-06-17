from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router

# Schema is managed by Alembic migrations (applied on container startup).
# Tests create the schema directly via Base.metadata.create_all (see conftest.py).

app = FastAPI(title="AgriProfit API", version="0.1.0")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the AgriProfit API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
