import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_email

# ==========================================
# API Server Initialization
# ==========================================
app = FastAPI(title="Opportunity Copilot API")

# This is crucial: It allows Person C's Vue app to talk to your Python code without getting blocked
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 1. The Data Contracts (Synced with Vue.js)
# ==========================================
class StudentProfile(BaseModel):
    major: str
    year: int
    gpa: Optional[float] = 0.0
    skills: List[str] = []
    interests: List[str] = []


class ExtractedOpportunity(BaseModel):
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


class APIRequest(BaseModel):
    emails: List[Dict]  # Vue sends a list of objects
    profile: StudentProfile


# ==========================================
# 2. Deterministic Checklist
# ==========================================
def generate_checklist(opp: ExtractedOpportunity) -> list:
    steps = []

    if opp.required_documents:
        docs = ", ".join(opp.required_documents)
        steps.append(f"Prepare required documents: {docs}.")
    else:
        steps.append("Prepare standard resume and transcript.")

    if opp.required_skills:
        skills = ", ".join(opp.required_skills[:3])
        steps.append(f"Highlight these skills in your application: {skills}.")

    contact = opp.contact_information if opp.contact_information and str(opp.contact_information).lower() not in [
        "none", "null", "not specified"] else "the official portal"

    if opp.deadline and str(opp.deadline).lower() not in ["none", "null", "not specified"]:
        steps.append(f"Submit via {contact} before {opp.deadline}.")
    else:
        steps.append(f"Apply ASAP via {contact} (Rolling Admissions).")

    return steps


# ==========================================
# 3. Robust Scoring Engine
# ==========================================
def score_opportunity(opp: ExtractedOpportunity, profile: StudentProfile) -> dict:
    score = 0
    reasons = []
    urgency = "LOW"

    # Check against Vue's 'gpa' variable
    if opp.min_cgpa is not None:
        if profile.gpa < opp.min_cgpa:
            return {
                "total_score": 0,
                "urgency": "DISQUALIFIED",
                "reasons": [f"❌ Disqualified: Requires {opp.min_cgpa} CGPA, but you have {profile.gpa}."]
            }
        else:
            score += 20
            reasons.append(f"✅ CGPA Match: Your {profile.gpa} meets the {opp.min_cgpa} requirement.")
    else:
        score += 10

        # Check against Vue's 'interests' variable
    pref_types = [p.lower() for p in profile.interests]
    if any(pt in opp.opportunity_type.lower() for pt in pref_types):
        score += 30
        reasons.append(f"🎯 Strong Fit: Matches your interest in {opp.opportunity_type}s.")

    if opp.required_skills:
        matched_skills = set([s.lower() for s in profile.skills]).intersection(
            set([s.lower() for s in opp.required_skills]))
        if matched_skills:
            score += 20
            reasons.append(f"💻 Skill Match: You have {len(matched_skills)} required skills.")

    if opp.deadline:
        try:
            target_date = datetime.fromisoformat(opp.deadline)
            days_left = (target_date - datetime.now()).days

            if days_left < 0:
                return {"total_score": 0, "urgency": "EXPIRED", "reasons": ["❌ Deadline has passed."]}
            elif days_left <= 7:
                urgency = "HIGH"
                score += 40
                reasons.append(f"🚨 URGENT: Only {days_left} days left to apply!")
            else:
                urgency = "MEDIUM"
                score += 20
                reasons.append(f"📅 Time to prepare: {days_left} days left until deadline.")

        except ValueError:
            urgency = "MEDIUM"
            score += 10
            reasons.append(f"⏳ Deadline mentioned ({opp.deadline}). Act quickly.")
    else:
        score += 10
        reasons.append("ℹ️ Rolling admissions or no deadline. Apply at your earliest convenience.")

    return {
        "total_score": min(100, score),
        "urgency": urgency,
        "reasons": reasons
    }


# ==========================================
# 4. The Master Ranker
# ==========================================
def process_inbox(raw_emails: List[str], profile: StudentProfile) -> List[dict]:
    ranked_list = []

    print(f"Processing batch of {len(raw_emails)} emails...")
    for email_text in raw_emails:
        parsed = parse_email(email_text)

        if parsed["status"] == "extracted":
            valid_opp = ExtractedOpportunity(**parsed["data"])

            if not valid_opp.is_opportunity:
                continue

            scoring = score_opportunity(valid_opp, profile)
            checklist = generate_checklist(valid_opp)

            ranked_list.append({
                "title": valid_opp.title,
                "opportunity": valid_opp.opportunity_type,
                "score": scoring["total_score"],
                "urgency": scoring["urgency"],
                "reasons": scoring["reasons"],
                "checklist": checklist
            })

    ranked_list.sort(key=lambda x: x["score"], reverse=True)
    return ranked_list


# ==========================================
# 5. The API Endpoint for Vue.js
# ==========================================
@app.post("/api/extractAndRank")
async def extract_and_rank_endpoint(payload: APIRequest):
    """
    This catches the JSON from Person C's Vue form.
    """
    formatted_emails = []
    for e in payload.emails:
        # Convert Vue's object back into a string for the LLM
        raw_text = f"Subject: {e.get('subject', 'No Subject')}\nFrom: {e.get('sender', 'Unknown')}\n\n{e.get('body', '')}"
        formatted_emails.append(raw_text)

    results = process_inbox(formatted_emails, payload.profile)
    return results