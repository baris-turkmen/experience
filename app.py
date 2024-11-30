from flask import Flask, jsonify, request, render_template
import requests
import json
import os  # for environment variables
from dotenv import load_dotenv
from openai import OpenAI

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

app = Flask(__name__)

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
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Use the exact same configuration as the test script
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv('SITE_URL'),
                "X-Title": os.getenv('APP_NAME'),
            },
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "My name is Qutaiba, i am research assistant. Dont mention my id or name in your response. but make your response as if you are talking to me. " + user_message
                }
            ]
        )
        
        # Add debug logging
        print("API Response received:", completion.choices[0].message.content)
        
        return jsonify({
            "choices": [{
                "message": {
                    "content": completion.choices[0].message.content
                }
            }]
        })
    except Exception as e:
        error_msg = f"Error in /api/chat: {str(e)}"
        print(error_msg)  # Server-side logging
        return jsonify({"error": error_msg}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 