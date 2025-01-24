import os
import hashlib
import requests
import uuid
import base64
from typing import Optional
from config import config
from loguru import logger
from pydantic import BaseModel, HttpUrl

class TTSConfig(BaseModel):
    appid: str
    access_token: str
    cluster: str = "volcano_tts"
    voice_type: str = "BV700_V2_streaming"
    language: str = "zh"
    api_url: HttpUrl
    max_text_length: int
    audio_folder: str

class TTSService:
    def __init__(self, config: TTSConfig):
        logger.info("Initializing TTS service...")
        self.config = config
        logger.debug(f"TTS config: {self.config}")
        logger.debug(f"Creating audio folder at: {self.config.audio_folder}")
        os.makedirs(self.config.audio_folder, exist_ok=True)
        logger.info("TTS service initialized successfully")
        
    def speak(self, text: str) -> str:
        try:
            # Create audio file in configured audio folder
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.abspath(os.path.join(self.config.audio_folder, audio_filename))
    
            # Split the text into chunks that are within the allowed length
            text_chunks = [text[i:i + self.config.max_text_length] for i in range(0, len(text), self.config.max_text_length)]
            
            # Create a single MP3 file for all audio data
            with open(audio_path, "wb") as f:
                for i, chunk in enumerate(text_chunks):
                    headers = {"Authorization": f"Bearer;{self.config.access_token}"}

                    request_json = {
                        "app": {
                            "appid": self.config.appid,
                            "token": self.config.access_token,
                            "cluster": self.config.cluster
                        },
                        "user": {
                            "uid": "388808087185088"
                        },
                        "audio": {
                            "voice_type": self.config.voice_type,
                            "language": self.config.language,
                            "encoding": "mp3",
                            "speed_ratio": 1.0,
                            "volume_ratio": 1.0,
                            "pitch_ratio": 1.0,
                        },
                        "request": {
                            "reqid": str(uuid.uuid4()),
                            "text": chunk,
                            "text_type": "plain",
                            "operation": "query",
                            "with_frontend": 1,
                            "frontend_type": "unitTson"
                        }
                    }
                    
                    logger.debug(f"Sending TTS request for chunk {i+1}/{len(text_chunks)}")
                    logger.trace(f"Request payload: {request_json}")
                    
                    response = requests.post(
                        self.config.api_url,
                        json=request_json,
                        headers=headers
                    )
                    response_data = response.json()
                    
                    logger.debug(f"Received response with status: {response.status_code}")
                    logger.trace(f"Response headers: {response.headers}")
                    
                    if response.status_code != 200:
                        error_msg = f"TTS API Error: {response_data.get('message', 'Unknown error')}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                        
                    if "data" not in response_data:
                        error_msg = "No audio data in response"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                        
                    audio_data = base64.b64decode(response_data["data"])
                    if not audio_data:
                        error_msg = "Empty audio data received"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                        
                    bytes_written = f.write(audio_data)
                    logger.debug(f"Wrote {bytes_written} bytes to {audio_path}")

            return audio_path
            
        except Exception as e:
            logger.error(f"TTS request failed: {str(e)}")
            raise

class TTSServiceFactory:
    @staticmethod
    def create_tts_service(tts_type: str = "bytedance") -> TTSService:
        tts_config = TTSConfig(
            appid=config.tts_appid,
            access_token=config.tts_access_token,
            cluster=config.tts_cluster,
            voice_type=config.tts_voice_type,
            language=config.tts_language,
            api_url=config.tts_api_url,
            max_text_length=config.tts_max_text_length,
            audio_folder=config.audio_folder
        )
        return TTSService(tts_config)
