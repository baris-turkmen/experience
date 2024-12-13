from flask import Flask, jsonify, request, render_template, Response, stream_with_context
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
import base64
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
)

elevenlabs_client = ElevenLabs(
    api_key=os.getenv('ELEVENLABS_API_KEY')
)

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['JSON_AS_ASCII'] = False

class Message:
    def __init__(self, role: str, content: List[Dict] | str):
        self.role = role
        self.content = content
        self.tokens = len(str(content)) // 4

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

conversation_manager = ConversationManager()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:    
        data = request.get_json(force=True)
        user_message = data.get('message', '').strip()
        image_data = data.get('image')
        
        message_content = []
        
        # Add system prompt
        system_prompt = "You are yildiz teknopark's AI assistant. Keep your response short and concise in Turkish. "
        message_content.append({
            "type": "text",
            "text": system_prompt + user_message
        })
        
        # Add image if provided and properly format it
        if image_data:
            try:
                # Remove data URL prefix if present
                if 'data:image/' in image_data:
                    # Extract the base64 part and image type
                    image_format = image_data.split(';')[0].split('/')[1]
                    base64_data = image_data.split('base64,')[1]
                    
                    # Format the image URL according to OpenAI's requirements
                    message_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{base64_data}"
                        }
                    })
            except Exception as e:
                logging.error(f"Image processing error: {str(e)}")
                return jsonify({"error": "Invalid image format"}), 400

        conversation_manager.add_message("user", message_content)
        
        headers = {
            "HTTP-Referer": os.getenv('SITE_URL'),
            "X-Title": os.getenv('APP_NAME'),
            "Content-Type": "application/json; charset=utf-8"
        }
        
        completion = client.chat.completions.create(
            extra_headers=headers, 
            model="anthropic/claude-3-opus",
            messages=conversation_manager.get_messages_for_api(),
            max_tokens=200
        )
        
        assistant_response = completion.choices[0].message.content.encode('utf-8').decode('utf-8')
        conversation_manager.add_message("assistant", assistant_response)
        
        # Generate audio
        audio_generator = elevenlabs_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_multilingual_v2",
            text=assistant_response,
            voice_settings={
                "stability": 0.71,
                "similarity_boost": 0.75,
                "style": 0.6,
                "use_speaker_boost": True
            }
        )
        audio_content = b''.join(audio_generator)
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
        logging.error(f"Error in /api/chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 