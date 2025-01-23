from app import create_app
from loguru import logger
import os

app = create_app()

# Configure static file route for audio files
app.config['AUDIO_FOLDER'] = os.path.join(os.path.dirname(__file__), 'audio')
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
app.add_url_rule(
    '/audio/<filename>',
    endpoint='audio',
    view_func=app.send_static_file
)

if __name__ == "__main__":
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Starting Flask application")
        app.run(
            host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5000),
            debug=app.config.get("DEBUG", False)
        )
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise
