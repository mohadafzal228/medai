import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.api.endpoints import auth, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Medical AI Assistant API - Powered by Google Gemini",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,  # From .env
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def on_startup():
    logger.info("Starting %s v%s", settings.PROJECT_NAME, settings.PROJECT_VERSION)
    await connect_to_mongo()
    logger.info("MongoDB connection established")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down application")
    await close_mongo_connection()
    logger.info("MongoDB connection closed")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to MediBot API",
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs",
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check application health and MongoDB connectivity."""
    try:
        db = await get_database()
        await db.command("ping")
        return {"status": "ok", "detail": "MongoDB connection healthy"}
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )