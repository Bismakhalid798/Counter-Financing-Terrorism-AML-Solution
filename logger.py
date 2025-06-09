import logging

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # Ensure UTF-8 encoding
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
