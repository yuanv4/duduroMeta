import os
import base64
import json
import uuid
import requests

class TTSService:
    """Abstract base class for TTS services"""
    def speak(self, text: str) -> None:
        """Convert text to speech"""
        raise NotImplementedError()

class TTSServiceFactory:
    @staticmethod
    def create_tts_service(tts_type: str) -> 'TTSService':
        if tts_type == "bytedance":
            return ByteDanceTTS()
        raise ValueError(f"Unknown TTS type: {tts_type}")

class ByteDanceTTS(TTSService):
    def __init__(self):
        self.appid = "7757288662"
        self.access_token = "Iwm8utZ5YcKIWsXWjHBXvTY-MFO8MLiU"
        self.cluster = "volcano_tts"
        self.voice_type = "BV700_V2_streaming"
        self.language = "zh"
        self.api_url = f"https://openspeech.bytedance.com/api/v1/tts"
        self.max_text_length = 300  # Adjust this based on the API's limit

    def speak(self, text):
        """Use ByteDance TTS to convert text to speech and play it sequentially."""
        try:
            import subprocess
            import time
            
            # Split the text into chunks that are within the allowed length
            text_chunks = [text[i:i + self.max_text_length] for i in range(0, len(text), self.max_text_length)]
            
            # Create a single MP3 file for all audio data
            audio_filename = f"temp_{uuid.uuid4().hex}.mp3"
            with open(audio_filename, "wb") as f:
                for i, chunk in enumerate(text_chunks):
                    headers = {"Authorization": f"Bearer;{self.access_token}"}
                    
                    request_json = {
                        "app": {
                            "appid": self.appid,
                            "token": "access_token",
                            "cluster": self.cluster
                        },
                        "user": {
                            "uid": "388808087185088"
                        },
                        "audio": {
                            "voice_type": self.voice_type,
                            "language": self.language,
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
                    
                    response = requests.post(self.api_url, json=request_json, headers=headers)
                    response_data = response.json()
                    
                    if response.status_code != 200:
                        raise ValueError(f"TTS API Error: {response_data.get('message', 'Unknown error')}")
                        
                    if "data" not in response_data:
                        raise ValueError("No audio data in response")
                        
                    audio_data = base64.b64decode(response_data["data"])
                    f.write(audio_data)
            
            # Play the combined audio file
            try:
                from playsound import playsound
                audio_path = os.path.abspath(audio_filename)
                playsound(audio_path)
                # Clean up the temporary file
                os.remove(audio_path)
            except ImportError:
                print("Please install playsound: pip install playsound")
                raise
                    
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            raise
