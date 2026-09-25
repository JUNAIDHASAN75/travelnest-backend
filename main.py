from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.database import engine, Base

def run_migrations():
    """Run Alembic migrations programmatically."""
    try:
        # Import models to register them
        import app.models  # noqa: F401
        
        # Create all tables based on SQLAlchemy models
        # This is the simplest approach - create tables from the ORM metadata
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully from models")
    except Exception as e:
        print(f"⚠ Migration error: {e}")
        import traceback
        traceback.print_exc()

# Run migrations before starting the app
run_migrations()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-ready REST API for TravelNest travel booking platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "TravelNest API is running"
    }


@app.get("/db-test", tags=["Health"])
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE()"))
        database_name = result.scalar()

    return {
        "database": database_name,
        "status": "connected"
    }
