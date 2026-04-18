import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment and initialize client
load_dotenv()
client = Groq()

# We use the 8B model for classification because it is insanely fast,
# which Person C will appreciate during the live UI demo.
MODEL = "llama-3.1-8b-instant"


def classify_email(email_body: str) -> dict:
    """
    Analyzes an email and returns a JSON dictionary:
    {"is_opportunity": bool, "type": str}
    """

    system_prompt = """
    You are an AI opportunity filter for university students.
    Your job is to read emails and determine if they contain a genuine, actionable opportunity 
    (like a scholarship, internship, competition, fellowship, or admission).

    Ignore generic newsletters, spam, or administrative notices.

    You MUST output valid JSON only, using exactly this schema:
    {
      "is_opportunity": true or false,
      "type": "internship" | "scholarship" | "competition" | "spam" | "newsletter" | "other"
    }
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},  # This forces Groq to return strict JSON
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this email:\n\n{email_body}"}
            ],
            temperature=0.0  # Keep it at 0 so the classification is deterministic and consistent
        )

        # Parse the JSON string returned by the LLM into a Python dictionary
        result_json = response.choices[0].message.content
        return json.loads(result_json)

    except Exception as e:
        print(f"Classification Error: {e}")
        return {"is_opportunity": False, "type": "error"}


# --- Quick Test ---
if __name__ == "__main__":
    test_email_spam = "Hi student, don't forget the cafeteria is closed tomorrow for cleaning."
    test_email_real = "We are accepting applications for the 2026 AI Summer Internship. Deadline is Friday."

    print("Testing Spam Email:")
    print(classify_email(test_email_spam))

    print("\nTesting Real Opportunity:")
    print(classify_email(test_email_real))