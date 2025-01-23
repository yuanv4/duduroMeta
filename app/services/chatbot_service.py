import requests
from typing import Optional
from loguru import logger
from pydantic import BaseModel, HttpUrl
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ChatbotConfig(BaseModel):
    base_url: HttpUrl
    api_key: str
    model: str = "deepseek-chat"

class ChatbotResponse(BaseModel):
    response: str
    status_code: int
    success: bool

class Chatbot:
    def __init__(self, config: ChatbotConfig):
        self.config = config
        self.session = self._create_session()
 
    def _create_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    def chat(self, message: str) -> str:
        try:
            url = f"{self.config.base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": "You are a friendly and approachable assistant. Use a casual tone and provide examples when explaining concepts."},
                    {"role": "user", "content": message}
                ]
            }
            
            logger.debug(f"Sending chat request to {url}")
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Chatbot request failed: {str(e)}")
            raise

class ChatbotFactory:
    @staticmethod
    def create_chatbot(base_url: str, api_key: str, model: str = "deepseek-chat") -> Chatbot:
        config = ChatbotConfig(
            base_url=base_url,
            api_key=api_key,
            model=model
        )
        return Chatbot(config)
