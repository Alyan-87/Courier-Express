from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, customer, staff, rider

from config.database import get_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Courier & Parcel Delivery System",
    description="Full-stack courier management system with role-based access (Customer, Staff, Rider)",
    version="1.0.0"
)

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(staff.router)
app.include_router(rider.router)

@app.get("/")
def home():
    return {"message": "Courier API is LIVE! Go to /docs for API documentation"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "courier-backend"}


@app.get("/health/db")
def health_db(db=Depends(get_db)):
    """Check MongoDB connectivity using ping command."""
    try:
        db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        raise HTTPException(status_code=503, detail="Database connection failed")
