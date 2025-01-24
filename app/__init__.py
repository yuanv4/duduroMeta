from flask import Flask
from flask_cors import CORS
from loguru import logger
from config import config
import os

def create_app():
    app = Flask(__name__, 
        static_folder='static',
        template_folder='templates',
        static_url_path='/static'
    )
    
    # Configure application
    app.config["SECRET_KEY"] = str(config.flask_secret_key)
    app.config["DEBUG"] = config.flask_debug
    app.config["AUDIO_FOLDER"] = os.path.abspath(config.audio_folder)

    # Configure logging with timestamped log files
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.add(
        f"logs/app_{timestamp}.log",
        rotation="100 MB",
        retention="7 days",
        level="DEBUG" if config.flask_debug else "INFO"
    )
    
    # Register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)
    
    # Initialize services
    from .services.chatbot_service import ChatbotFactory
    from .services.tts_service import TTSServiceFactory
    
    app.chatbot = ChatbotFactory.create_chatbot(
        base_url=config.chatbot_base_url.unicode_string(),
        api_key=str(config.chatbot_api_key),
        model=config.chatbot_model
    )
    
    app.tts = TTSServiceFactory.create_tts_service(
        tts_type="bytedance"
    )
    
    return app
