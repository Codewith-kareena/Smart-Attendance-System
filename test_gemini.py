
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

print("1. Loading API key...", flush=True)
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found. Check your .env file.")
else:
    try:
        print("2. Connecting to Gemini...", flush=True)

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000
            )
        )

        print("3. Sending test request...", flush=True)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Reply with: Gemini connection successful!",
            config=types.GenerateContentConfig(
                max_output_tokens=50
            )
        )

        print("4. Response received:", flush=True)
        print(response.text)

    except Exception as error:
        print("Gemini connection failed:", repr(error))
