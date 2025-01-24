import os
from flask import Blueprint, request, jsonify, current_app, render_template, send_from_directory
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

bp = Blueprint('api', __name__)

@bp.route('/audio/<filename>')
def audio(filename):
    """Serve audio files"""
    return send_from_directory(current_app.config.get('AUDIO_FOLDER'), filename)

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/chat', methods=['POST', 'GET'])
def chat():
    """
    Chat with the AI assistant
    ---
    tags:
      - Chat
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ChatRequest'
    responses:
      200:
        description: AI response
        content:
          application/json:
            schema:
              type: object
              properties:
                response:
                  type: string
      400:
        description: Invalid request
    """
    try:
        logger.info(f"Incoming {request.method} request to /chat from {request.remote_addr}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        if request.method == 'POST':
            data = request.get_json()
            logger.debug(f"POST request data: {data}")
            request_data = ChatRequest(**data)
        else:  # GET
            message = request.args.get('message')
            logger.debug(f"GET request params: {request.args}")
            if not message:
                logger.error("GET request missing 'message' parameter")
                return jsonify({"error": "message parameter is required"}), 400
            request_data = ChatRequest(message=message)
        
        logger.info(f"Processing chat request with message: {request_data.message[:50]}...")
        response = current_app.chatbot.chat(request_data.message)
        logger.info(f"Chatbot response: {response[:50]}...")
        
        # Generate audio for the response
        audio_path = current_app.tts.speak(response)
        logger.debug(f"Generated audio file at: {audio_path}")
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return jsonify({"error": "Failed to generate audio"}), 500
        audio_url = f"/audio/{os.path.basename(audio_path)}"
        logger.debug(f"Audio URL: {audio_url}")
        
        return jsonify({
            "response": response,
            "audio_url": audio_url
        })
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@bp.route('/speak', methods=['POST', 'GET'])
def speak():
    """
    Convert text to speech
    ---
    tags:
      - TTS
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/SpeakRequest'
    responses:
      200:
        description: Success
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
      400:
        description: Invalid request
    """
    try:
        logger.info(f"Incoming {request.method} request to /speak from {request.remote_addr}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        
        if request.method == 'POST':
            data = request.get_json()
            logger.debug(f"POST request data: {data}")
            request_data = SpeakRequest(**data)
            logger.info(f"Processing TTS request with text: {request_data.text[:50]}... (length: {len(request_data.text)})")
        else:  # GET
            text = request.args.get('text')
            if not text:
                logger.error("GET request missing 'text' parameter")
                return jsonify({"error": "text parameter is required"}), 400
            # Ensure text is properly encoded
            try:
                text = text.encode('utf-8').decode('utf-8')
            except UnicodeError:
                logger.error("Invalid text encoding")
                return jsonify({"error": "invalid text encoding"}), 400
            # Validate text length and content
            logger.debug(f"Validating text length: {len(text)} characters")
            if len(text) > 500:
                logger.warning(f"Text too long: {len(text)} characters (max 500)")
                return jsonify({"error": "text too long, max 500 characters"}), 400
            if not text.strip():
                logger.warning("Empty text received")
                return jsonify({"error": "text cannot be empty"}), 400
            logger.debug(f"Text validation passed: {len(text)} characters")
            request_data = SpeakRequest(text=text)
            logger.info(f"GET request received with text: {text[:50]}... (length: {len(text)})")
        
        audio_path = current_app.tts.speak(request_data.text)
        logger.info(f"TTS request processed: {request_data.text[:50]}...")
        return jsonify({
            "status": "success",
            "audio_url": f"/audio/{os.path.basename(audio_path)}"
        })
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({"error": str(e)}), 400
