from dotenv import load_dotenv
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

load_dotenv()

print("\nEnvironment Variables:")
print(f"API Key: {os.getenv('OPENROUTER_API_KEY')}")
print(f"Site URL: {os.getenv('SITE_URL')}")
print(f"App Name: {os.getenv('APP_NAME')}")

# Try to read the file directly
if os.path.exists(env_path):
    print("\nFile contents:")
    with open(env_path, 'r') as f:
        print(f.read()) 