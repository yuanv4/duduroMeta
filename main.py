import os
from services.chatbot_service import ChatbotFactory
from services.tts_service import TTSServiceFactory

class ChatbotApp:
    def __init__(self):
        self.chatbot = ChatbotFactory.create_chatbot(
            chatbot_type="deepseek",
            api_key="sk-f23f998a866a4148b8f075278b768e6e"
        )
        self.tts = TTSServiceFactory.create_tts_service(tts_type="bytedance")
        
    def chat(self, message):
        """Send a message to the chatbot and get a response."""
        return self.chatbot.chat(message)
            
    def speak(self, text):
        """Use TTS service to convert text to speech and play it."""
        self.tts.speak(text)

def main():
    try:
        app = ChatbotApp()
    except ValueError as e:
        print(f"ChatbotApp Init Error: {str(e)}")
        return
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            # Get chatbot response and speak it
            response = app.chat(user_input)
            print(f"Bot: {response}")
            app.speak(response)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
