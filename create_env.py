env_content = """OPENROUTER_API_KEY=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
SITE_URL=http://localhost:5000
APP_NAME=YourAppName"""

with open('.env', 'w') as f:
    f.write(env_content)

print("New .env file created!") 