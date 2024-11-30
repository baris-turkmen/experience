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
        model="anthropic/claude-3.5-sonnet",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                        }
                    }
                ]
            }
        ]
    )
    print("Success!")
    print("Response:", completion.choices[0].message.content)
    
    print("\nResponse Details:")
    print("Model:", completion.model)
    print("Message Role:", completion.choices[0].message.role)
    print("Finish Reason:", completion.choices[0].finish_reason)
    
except Exception as e:
    print("\nDetailed Error Information:")
    print("Error Type:", type(e).__name__)
    print("Error Message:", str(e))
    print("\nPlease check:")
    print("1. OPENROUTER_API_KEY is set correctly in .env")
    print("2. SITE_URL and APP_NAME are properly configured")
    print("3. Network connection is stable")
    print("4. API endpoint is responding") 