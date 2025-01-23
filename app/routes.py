import os
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, Field
from typing import Optional
from loguru import logger

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

bp = Blueprint('api', __name__)

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
        if request.method == 'POST':
            data = request.get_json()
            request_data = ChatRequest(**data)
        else:  # GET
            message = request.args.get('message')
            if not message:
                return jsonify({"error": "message parameter is required"}), 400
            request_data = ChatRequest(message=message)
        
        response = current_app.chatbot.chat(request_data.message)
        logger.info(f"Chat request processed: {request_data.message[:50]}...")
        
        return jsonify({"response": response})
    
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
        if request.method == 'POST':
            data = request.get_json()
            request_data = SpeakRequest(**data)
        else:  # GET
            text = request.args.get('text')
            if not text:
                return jsonify({"error": "text parameter is required"}), 400
            # Ensure text is properly encoded
            try:
                text = text.encode('utf-8').decode('utf-8')
            except UnicodeError:
                return jsonify({"error": "invalid text encoding"}), 400
            # Validate text length and content
            if len(text) > 500:
                return jsonify({"error": "text too long, max 500 characters"}), 400
            if not text.strip():
                return jsonify({"error": "text cannot be empty"}), 400
            request_data = SpeakRequest(text=text)
            logger.info(f"GET request received with text: {text}")
        
        audio_path = current_app.tts.speak(request_data.text)
        logger.info(f"TTS request processed: {request_data.text[:50]}...")
        return jsonify({
            "status": "success",
            "audio_url": f"/audio/{os.path.basename(audio_path)}"
        })
    
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({"error": str(e)}), 400
