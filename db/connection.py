import psycopg2
import os

from logger_config import get_logger

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "local"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

logger = get_logger(__name__)

def get_connection():
    try:
        logger.debug("Attempting to connect to the database.")
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise
