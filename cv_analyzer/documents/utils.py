import os
import pymupdf
from google import genai
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(file) -> str:
    """
    Extracts raw text from an uploaded PDF file.
    """
    # Django's FieldFile has a .path attribute with the absolute path
    if hasattr(file, 'path'):
        file_path = file.path
    else:
        file_path = file

    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text

def get_ai_analysis(cv_text: str, job_offer) -> tuple[int, str]:
    """
    Sends CV and job offer text to Gemini and returns a match score (0-100) and missing skills.
    """
    prompt = f"""
        You are an expert HR recruiter and CV analyst.

        Compare the following CV with the job offer and evaluate how well the candidate matches the job requirements.

        Consider the following criteria:
        - Required skills and technologies match
        - Years of experience relevance
        - Education requirements
        - Language requirements
        - Overall profile fit

        CV:
        \"\"\"
        Text from candidate cv: {cv_text}
        \"\"\"

        JOB OFFER:
        \"\"\"
        Job offer title: {job_offer.title}
        Text about job_offer: {job_offer.raw_text}
        Required skills and technologies for job: {job_offer.skills}
        \"\"\"

        Return your answer in EXACTLY this format (one line, no extra text):
        SCORE|MISSING_SKILLS

        Where:
        - SCORE is a single integer from 0 to 100 (match percentage)
        - MISSING_SKILLS is a comma-separated list of skills required by the job offer that the candidate is missing (or "none" if all skills match)

        Example responses:
        75|Docker, Kubernetes, AWS
        100|none
        30|Python, Django, SQL, REST API

        Do not include any other text, explanation, or formatting. Just one line in the format above.
        """

    try:
        response = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )
        parts = response.output_text.strip().split("|",1)
        score = max(0, min(100, int(parts[0].strip())))
        missing = parts[1].strip() if len(parts) > 1 and parts[1].strip().lower() != "none" else ""
        return score, missing
    except Exception:
        return 0, ""