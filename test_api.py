import os
print("1. Imports successful...")

from dotenv import load_dotenv
from groq import Groq

print("2. Loading .env file...")
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is missing or empty in the .env file!")
else:
    print(f"3. API Key found (starts with: {api_key[:8]}...)")

print("4. Initializing Groq client...")
client = Groq()

def test_connection():
    print("5. Initiating handshake with Groq API (waiting for response)...")
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "You are a system diagnostic tool. Reply with exactly one word: 'Operational'."}
            ],
            max_tokens=50,
            timeout=10.0 # Adding a 10-second timeout so it doesn't hang forever
        )
        print(f"\n✅ Status: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
    print("6. Script finished.")