import logging
import os

__version__ = "0.0.4"

logger = logging.getLogger(__name__)
logger.setLevel(level=os.getenv("LOG_LEVEL", "INFO").upper())

ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
