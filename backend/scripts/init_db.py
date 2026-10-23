import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.init_db import init_db
from app.core.logging import logger

if __name__ == "__main__":
    logger.info("Running manual database table initialization...")
    init_db()
    logger.info("Done.")
