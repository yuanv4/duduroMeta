import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from pydantic_settings import BaseSettings
from pydantic import Field, HttpUrl, ValidationError, field_validator
from pathlib import Path
from loguru import logger
from typing import Literal

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Flask Configuration
    flask_secret_key: str = Field(
        ...,
        env="FLASK_SECRET_KEY",
        min_length=32,
        description="Secret key for Flask session management"
    )
    
    flask_debug: bool = Field(
        default=False,
        env="FLASK_DEBUG",
        description="Enable Flask debug mode"
    )

    # Chatbot Configuration
    chatbot_base_url: HttpUrl = Field(
        ...,
        env="CHATBOT_BASE_URL",
        description="Base URL for chatbot API"
    )
    
    chatbot_api_key: str = Field(
        ...,
        env="CHATBOT_API_KEY",
        min_length=32,
        description="API key for chatbot service"
    )
    
    chatbot_model: str = Field(
        default="deepseek-chat",
        env="CHATBOT_MODEL",
        description="Model name for chatbot service"
    )

    # TTS Configuration
    tts_appid: str = Field(
        ...,
        env="TTS_APPID",
        min_length=8,
        description="Application ID for TTS service"
    )
    
    tts_access_token: str = Field(
        ...,
        env="TTS_ACCESS_TOKEN",
        min_length=32,
        description="Access token for TTS service"
    )
    
    tts_cluster: str = Field(
        default="volcano_tts",
        env="TTS_CLUSTER",
        description="Cluster name for TTS service"
    )
    
    tts_voice_type: str = Field(
        default="BV700_V2_streaming",
        env="TTS_VOICE_TYPE",
        description="Voice type for TTS service"
    )
    
    tts_language: Literal["zh", "en"] = Field(
        default="zh",
        env="TTS_LANGUAGE",
        description="Language code for TTS service"
    )
    
    tts_api_url: HttpUrl = Field(
        ...,
        env="TTS_API_URL",
        description="API endpoint for TTS service"
    )
    
    tts_max_text_length: int = Field(
        default=30,
        env="TTS_MAX_TEXT_LENGTH",
        gt=0,
        le=30,
        description="Maximum text length for TTS input"
    )

    # Audio Configuration
    audio_folder: str = Field(
        default=os.path.join(BASE_DIR, "app", "static", "audio"),
        env="AUDIO_FOLDER",
        description="Folder to store generated audio files"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"

    @field_validator("flask_secret_key", "chatbot_api_key", "tts_access_token")
    @classmethod
    def validate_secrets(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("Secret values must be at least 32 characters")
        return value

# Configure logger
logger.remove()
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Initialize config
try:
    config = Settings()
    logger.info("Configuration loaded successfully")
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Failed to load configuration: {str(e)}")
    raise
