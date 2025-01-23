from openai import OpenAI

class Chatbot:
    """Abstract base class for chatbot services"""
    def chat(self, message: str) -> str:
        """Send a message to the chatbot and get a response"""
        raise NotImplementedError()

class ChatbotFactory:
    @staticmethod
    def create_chatbot(chatbot_type: str, api_key: str) -> 'Chatbot':
        if chatbot_type == "deepseek":
            return DeepseekChatbot(api_key)
        raise ValueError(f"Unknown chatbot type: {chatbot_type}")

class DeepseekChatbot(Chatbot):
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
    def chat(self, message: str) -> str:
        """Send a message to the Deepseek chatbot and get a response"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a friendly and approachable assistant. Use a casual tone and provide examples when explaining concepts."},
                    {"role": "user", "content": message},
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
