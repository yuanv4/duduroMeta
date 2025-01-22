# Deepseek Chatbot

A conversational AI chatbot powered by Deepseek API with text-to-speech capabilities.

## Features

- Natural language conversation using Deepseek API
- Text-to-speech functionality using ByteDance TTS
- Modular architecture for easy maintenance and extension
- Environment-based configuration

## Project Structure

```
deepseek_chatbot/
├── services/               # Core service implementations
│   ├── chatbot_service.py  # Chatbot service implementation
│   └── tts_service.py      # Text-to-speech service implementation
├── main.py                 # Main application entry point
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── .gitignore              # Git ignore rules
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/deepseek-chatbot.git
   cd deepseek-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API credentials:
   ```bash
   DEEPSEEK_API_KEY=your_deepseek_api_key
   BYTEDANCE_APPID=your_bytedance_appid
   BYTEDANCE_ACCESS_TOKEN=your_bytedance_access_token
   BYTEDANCE_CLUSTER=your_cluster
   BYTEDANCE_VOICE_TYPE=your_voice_type
   ```

## Usage

Run the chatbot:
```bash
python main.py
```

Start chatting! Type your message and press Enter. The chatbot will respond both in text and speech.

To exit, type `exit` or press Ctrl+C.

## Configuration

The following environment variables are required:

| Variable                | Description                          |
|-------------------------|--------------------------------------|
| DEEPSEEK_API_KEY        | Your Deepseek API key                |
| BYTEDANCE_APPID         | ByteDance TTS application ID         |
| BYTEDANCE_ACCESS_TOKEN  | ByteDance TTS access token           |
| BYTEDANCE_CLUSTER       | ByteDance TTS cluster                |
| BYTEDANCE_VOICE_TYPE    | ByteDance TTS voice type             |

## License

MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted...
