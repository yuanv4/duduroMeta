from app import create_app
from loguru import logger
import os

app = create_app()

if __name__ == "__main__":
    try:
        logger.info("Starting Flask application")
        app.run(
            host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5000),
            debug=app.config.get("DEBUG", False)
        )
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise
