import logging
import os

logger = logging.getLogger()
logger.setLevel(level=os.getenv("LOG_LEVEL", "INFO").upper())
