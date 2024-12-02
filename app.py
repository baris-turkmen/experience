from flask import Flask, jsonify, request, render_template, send_file, Response, stream_with_context
import requests
import json
import os  # for environment variables
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import logging
from typing import List, Dict

# Try both methods of loading environment variables
load_dotenv()

# Manually set if not loaded from .env
if os.getenv('OPENROUTER_API_KEY') == 'your_api_key_here':
    os.environ['OPENROUTER_API_KEY'] = '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'
    os.environ['SITE_URL'] = 'http://localhost:5000'
    os.environ['APP_NAME'] = 'YourAppName'

# Debug: Print environment variables
print("API Key:", os.getenv('OPENROUTER_API_KEY'))
print("Site URL:", os.getenv('SITE_URL'))
print("App Name:", os.getenv('APP_NAME'))

# Initialize OpenAI client - move this to global scope
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
)

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(
    api_key=os.getenv('ELEVENLABS_API_KEY')
)

app = Flask(__name__)

class Message:
    def __init__(self, role: str, content: List[Dict] | str):
        self.role = role
        self.content = content
        self.tokens = self.estimate_tokens(str(content))

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return len(text) // 4

class ConversationManager:
    def __init__(self):
        self.history: List[Message] = []
        self.MAX_HISTORY_LENGTH = 10
        self.MAX_TOKEN_COUNT = 2000

    def add_message(self, role: str, content: List[Dict] | str):
        self.history.append(Message(role, content))
        self._truncate_history()

    def _truncate_history(self):
        if len(self.history) > self.MAX_HISTORY_LENGTH:
            self.history = self.history[-self.MAX_HISTORY_LENGTH:]
        
        while sum(msg.tokens for msg in self.history) > self.MAX_TOKEN_COUNT and len(self.history) > 1:
            self.history.pop(0)

    def get_messages_for_api(self) -> List[Dict]:
        return [{"role": msg.role, "content": msg.content} for msg in self.history]

# Initialize conversation manager globally
conversation_manager = ConversationManager()

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from my first API!"})

@app.route('/api/time', methods=['GET'])
def get_time():
    from datetime import datetime
    return jsonify({"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        image_url = data.get('image_url')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        message_content = []
        
        message_content.append({
            "type": "text",
            "text": "You are Yildiz Teknopark AI asisstant. Keep your response short and concise in Turkish. " + user_message
        })
        
        if image_url:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })

        # Add user message to conversation history
        conversation_manager.add_message("user", message_content)
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv('SITE_URL'),
                "X-Title": os.getenv('APP_NAME'),
            },
            model="anthropic/claude-3.5-sonnet",
            messages=conversation_manager.get_messages_for_api(),
            max_tokens=200
        )
        
        # Add assistant's response to conversation history
        assistant_response = completion.choices[0].message.content
        conversation_manager.add_message("assistant", assistant_response)
        
        print("API Response received:", assistant_response)
        
        # Generate audio for the response using faster Turkish-compatible model
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM", 
            model_id="eleven_turbo_v2",
            text=assistant_response
        )
        # Convert generator to bytes
        audio_content = b''.join(audio_generator)
        
        # Encode audio content to base64 for sending with JSON
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        return jsonify({
            "choices": [{
                "message": {
                    "content": assistant_response
                }
            }],
            "audio": audio_base64
        })
    except Exception as e:
        error_msg = f"Error in /api/chat: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Generate audio stream with required voice_id and model_id parameters
        audio_stream = elevenlabs_client.text_to_speech.convert_as_stream(
            text=text,
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Turkish voice ID
            model_id="eleven_multilingual_v2"  # Multilingual model ID
        )
        
        # Return audio as a streaming response
        return Response(
            stream_with_context(audio_stream),
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        error_msg = f"Error in /api/text-to-speech: {str(e)}"
        print(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 