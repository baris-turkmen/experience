from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
)

try:
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": os.getenv('SITE_URL'),
            "X-Title": os.getenv('APP_NAME'),
        },
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": "Hello, are you working?"
            }
        ]
    )
    print("Success!")
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", str(e)) 