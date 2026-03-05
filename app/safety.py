import re

# Direct, unambiguous crisis expressions — hard stop with resources
CRISIS_KEYWORDS_HARD = [
    r"\bkill\s+my\s*self\b",
    r"\bwant\s+to\s+die\b",
    r"\bdon'?t\s+want\s+to\s+(live|be\s+alive|exist)\b",
    r"\bcutting\s+my\s*self\b",
    r"\bhurt\s+my\s*self\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\bbetter\s+off\s+(dead|without\s+me)\b",
    r"\bplanning\s+to\s+(end|kill|hurt)\b",
]

# Softer mentions that might appear in disclaimers like "not suicidal but..."
CRISIS_KEYWORDS_SOFT = [
    r"\bsuicid\w*\b",
    r"\bend\s+(it|my\s+life|everything)\b",
    r"\bself[- ]?harm\b",
]

# Phrases that indicate the user is disclaiming crisis intent
CRISIS_DISCLAIMERS = [
    r"\bnot\s+(in\s+a\s+)?suicid",
    r"\bnot\s+going\s+to\s+(kill|hurt|harm)\b",
    r"\bnot\s+saying\s+(I|i)\s+(want|wanna)\s+to\s+die\b",
    r"\bdon'?t\s+mean\s+(it\s+)?like\s+that\b",
    r"\bnot\s+like\s+that\b",
    r"\bnot\s+in\s+that\s+way\b",
    r"\bi'?m\s+not\s+there\b",
    r"\bnot\s+actively\b",
]

CRISIS_RESPONSE_HARD = (
    "I hear you, and I want you to know that what you're feeling matters. "
    "Please reach out to someone who can help right now:\n\n"
    "988 Suicide & Crisis Lifeline: Call or text 988 (US)\n"
    "Crisis Text Line: Text HOME to 741741\n"
    "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/\n\n"
    "You don't have to go through this alone. Please talk to someone you trust."
)

# Softer response: acknowledges distress, shares resources gently, but does NOT hard-stop
# Returns None so the message continues through RAG with this prepended
CRISIS_RESPONSE_SOFT = (
    "I can hear how much pain you're in, and I want you to know that's valid. "
    "Just in case it's ever helpful, these are always available to you: "
    "988 Suicide & Crisis Lifeline (call or text 988) and Crisis Text Line (text HOME to 741741).\n\n"
)

OUT_OF_SCOPE_PATTERNS = [
    (r"\b(dosage|dose|how\s+much)\b.*\b(medication|medicine|drug|supplement|mg)\b",
     "I'm not able to advise on medication or supplement dosing. That's something your healthcare provider would be the right person to guide you on. "
     "What I can help with is understanding your symptoms through the nervous system lens, if that would be useful?"),
    (r"\bshould\s+I\s+(stop|quit|reduce|change)\s+(my\s+)?(medication|meds|prescription)\b",
     "Any changes to your medication should always be discussed with your prescribing doctor, so that's outside what I can help with. "
     "But if you want to talk about what you're experiencing and how it fits into recovery, I'm here for that."),
    (r"\bdiagnos(e|is)\b.*\b(me|I)\b",
     "As an educational tool, I'm not able to provide diagnoses. That's something a healthcare professional would need to do. "
     "What I can do is help you understand your symptoms and what might be going on from a nervous system perspective, once your doctor has ruled out other things. "
     "Would that be helpful?"),
]


def check_crisis(message: str) -> dict | None:
    """Returns a dict with 'response' and 'hard_stop' flag, or None if no crisis detected."""
    text = message.lower()

    has_disclaimer = any(re.search(p, text) for p in CRISIS_DISCLAIMERS)

    # Check hard keywords first — these override disclaimers
    for pattern in CRISIS_KEYWORDS_HARD:
        if re.search(pattern, text):
            if has_disclaimer:
                return {"response": CRISIS_RESPONSE_SOFT, "hard_stop": False}
            return {"response": CRISIS_RESPONSE_HARD, "hard_stop": True}

    # Check soft keywords — these respect disclaimers
    for pattern in CRISIS_KEYWORDS_SOFT:
        if re.search(pattern, text):
            if has_disclaimer:
                return {"response": CRISIS_RESPONSE_SOFT, "hard_stop": False}
            return {"response": CRISIS_RESPONSE_HARD, "hard_stop": True}

    return None


def check_out_of_scope(message: str) -> str | None:
    text = message.lower()
    for pattern, response in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, text):
            return response
    return None
