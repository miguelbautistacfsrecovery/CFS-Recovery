import re

from app.config import PERSONAL_QUESTION_THRESHOLD, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

PERSONAL_PATTERNS = [
    r"\bmy\s+(symptoms?|condition|situation|recovery|health|body|pain|fatigue|brain\s*fog)\b",
    r"\bam\s+I\s+(in\s+the|at|getting|recovering)\b",
    r"\bshould\s+I\b",
    r"\bwhat\s+(should|can|do)\s+I\s+do\b.*\b(about|for|with)\s+my\b",
    r"\bhow\s+long\s+will\s+(my|it\s+take\s+me)\b",
    r"\bwhat\s+zone\s+am\s+I\b",
    r"\bis\s+my\b.*\bnormal\b",
    r"\bI'?m\s+(stuck|scared|worried|struggling|not\s+improving)\b",
    r"\bI\s+(have|feel|experience|get|suffer)\b.*\b(symptom|pain|fatigue|fog|palpitation|dizz|nause|insomnia)\b",
]

UPSELL_MESSAGE = (
    "It sounds like you're looking for guidance specific to your situation. "
    "For personalized 1-on-1 coaching and a recovery plan tailored to you, "
    "see if you're a good fit for our Recovery System.\n\n"
    "Apply here: https://www.cfsrecovery.co/apply"
)


def is_personal_question(message: str) -> bool:
    text = message.lower()
    matches = sum(1 for p in PERSONAL_PATTERNS if re.search(p, text))
    return matches >= 1


def check_upsell(user_id: int, message: str) -> str | None:
    """Returns upsell message if threshold reached, None otherwise."""
    if not is_personal_question(message):
        return None

    result = supabase.table("users").select("personal_question_count").eq("id", user_id).single().execute()
    current_count = result.data["personal_question_count"] if result.data else 0
    new_count = current_count + 1

    supabase.table("users").update({"personal_question_count": new_count}).eq("id", user_id).execute()

    if new_count == PERSONAL_QUESTION_THRESHOLD:
        return UPSELL_MESSAGE
    return None
