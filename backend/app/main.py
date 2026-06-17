from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import models, database
from .api.router import api_router

# Initialize database tables
models.Base.metadata.create_all(bind=database.engine)

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
