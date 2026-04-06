import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("nodetrace")
logger.setLevel(logging.INFO)

# Create logs directory in the current working directory
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "nodetrace.log")

try:
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except Exception as e:
    # Fallback to console handler if file logging fails
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(console_handler)