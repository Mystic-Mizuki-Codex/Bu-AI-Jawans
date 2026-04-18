import os
import json
from datetime import datetime  # <-- 1. IMPORT ADDED HERE
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional

# Load environment and initialize client
load_dotenv()
client = Groq()
MODEL = "llama-3.1-8b-instant"


# ==========================================
# SCHEMA (Matches main.py)
# ==========================================
class OpportunityDetails(BaseModel):
    is_opportunity: bool = Field(description="True if this is a valid opportunity, False otherwise.")
    title: str = Field(description="A short, clear title for the opportunity.")
    opportunity_type: str = Field(description="e.g., Internship, Hackathon, Fellowship")
    deadline: Optional[str] = Field(
        description="The deadline strictly in YYYY-MM-DD format. Null if rolling or not specified.")
    min_cgpa: Optional[float] = Field(description="The minimum CGPA required as a float. Null if not specified.")
    required_skills: List[str] = Field(description="Specific technical or soft skills mentioned.")
    eligibility_conditions: List[str] = Field(description="Other requirements (e.g., semester, degree).")
    required_documents: List[str] = Field(description="Documents needed (e.g., Resume, Transcript).")
    contact_information: Optional[str] = Field(description="Link or email to apply.")


def extract_details(email_body: str) -> dict:
    # <-- 2. WE INJECT THE CLOCK RIGHT HERE -->
    # This runs the exact millisecond the function is called
    today_date = datetime.now().strftime("%Y-%m-%d")

    schema_json = json.dumps(OpportunityDetails.model_json_schema(), indent=2)

    # <-- 3. WE ADD {today_date} TO THE PROMPT -->
    system_prompt = f"""
    You are an expert data extraction AI. 
    Read the provided email and extract the relevant details.

    CRITICAL CONTEXT:
    Today's exact date is {today_date}. 
    Use this date to convert relative deadlines (e.g., "tomorrow", "next Friday") into absolute YYYY-MM-DD dates.

    You MUST output valid JSON only, strictly matching this exact JSON schema:
    {schema_json}

    If a field is missing, use null for floats/strings, or an empty array [] for lists.
    Do not invent information. Ensure dates are strictly YYYY-MM-DD.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract data from this email:\n\n{email_body}"}
            ],
            temperature=0.0
        )

        raw_json = json.loads(response.choices[0].message.content)
        validated_data = OpportunityDetails(**raw_json)
        return validated_data.model_dump()

    except Exception as e:
        print(f"Extraction Error: {e}")
        return None