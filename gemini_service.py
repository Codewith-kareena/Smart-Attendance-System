
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def generate_attendance_summary(attendance_data):

    if not API_KEY:
        return "Gemini API key not found. Check your .env file."

    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(timeout=30000)
        )

        prompt = f"""
        You are an attendance analysis assistant.

        Analyze the following student attendance records:

        {attendance_data}

        Provide:
        1. Total students present.
        2. Total students late.
        3. Total students absent.
        4. Important attendance observations.
        5. A short recommendation for the teacher.

        Keep the response clear and professional.
        """

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=500
            )
        )

        return response.text or "Gemini returned an empty response."

    except Exception as error:
        return f"Gemini service temporarily unavailable: {error}"
