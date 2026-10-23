import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.init_db import init_db, seed_reproducible_data
from app.db.session import SessionLocal
from app.core.logging import logger

if __name__ == "__main__":
    logger.info("Initializing tables...")
    init_db()
    with SessionLocal() as db:
        logger.info("Seeding database...")
        seed_reproducible_data(db)
    logger.info("Seeding complete.")
