import json
import time
from classifier import classify_email
from extractor import extract_details


def parse_email(email_body: str, retry_count=2) -> dict:
    """
    Enhanced master function with retry logic and error handling.
    """
    if not email_body or len(email_body.strip()) < 10:
        return {"status": "skipped", "opportunity_type": "invalid_input", "data": None}

    for attempt in range(retry_count + 1):
        try:
            # Step 1: Classification
            classification = classify_email(email_body)

            if not classification.get("is_opportunity"):
                return {
                    "status": "skipped",
                    "opportunity_type": classification.get("type", "unknown"),
                    "data": None
                }

            # Step 2: Extraction
            extracted_data = extract_details(email_body)

            if extracted_data:
                return {
                    "status": "extracted",
                    "opportunity_type": classification.get("type", "opportunity"),
                    "data": extracted_data
                }

        except Exception as e:
            if "rate_limit" in str(e).lower():
                print(f"Rate limit hit, retrying in 2 seconds... (Attempt {attempt + 1})")
                time.sleep(2)
                continue
            print(f"Attempt {attempt + 1} failed: {e}")

    return {"status": "error", "opportunity_type": "failed_after_retries", "data": None}


# --- H5 Stress Test ---
if __name__ == "__main__":
    # Test Case: Empty/Short string
    print("Testing Empty Input:", parse_email("   ")["status"])

    # Test Case: Messy input that looks like an opportunity but is vague
    messy_email = "Someone told me there is a grant for AI students. I think the link is google.com."
    print("Testing Vague Input:", parse_email(messy_email)["status"])