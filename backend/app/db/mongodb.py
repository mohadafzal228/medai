from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database():
    if db.client is None:
        raise RuntimeError("Database not connected. Please check MongoDB connection.")
    return db.client[settings.DB_NAME]

async def connect_to_mongo():
    """
    Establish connection to MongoDB with proper error handling, validation, and retries.
    Raises RuntimeError if connection fails after retries.
    """
    max_retries = 3
    retry_delay = 2  # seconds

    if not settings.MONGODB_URL:
        raise ValueError("MONGODB_URL is not set in environment variables")

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to MongoDB at {settings.MONGODB_URL[:20]}... (Attempt {attempt + 1}/{max_retries})")
            db.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            
            # Validate connection with ping
            await db.client.admin.command('ping')
            logger.info(f"✓ Successfully connected to MongoDB database: {settings.DB_NAME}")
            
            # Create indexes (optional, but good practice if schema is known)
            # database = db.client[settings.DB_NAME]
            # await database.users.create_index("email", unique=True)
            return
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB (Attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                db.client = None
                raise RuntimeError(
                    f"Could not connect to MongoDB after {max_retries} attempts. "
                    f"Please ensure MongoDB is running and MONGODB_URL is correct. Error: {str(e)}"
                )

async def close_mongo_connection():
    """Close MongoDB connection gracefully"""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")
    else:
        logger.warning("No active MongoDB connection to close")