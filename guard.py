"""
ScamShield - input hardening / prompt-injection guard.
Detects attempts to manipulate the AI that analyzes a message, so the tool
can never be turned against its user. Hardened via a red-team suite (redteam.py).
"""
import re

_INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|above|prior|earlier)\s+(instructions?|prompts?|rules?)",
    r"disregard (all |the |your )?(previous |above |prior )?(instructions?|rules?|prompt)",
    r"forget (all |everything )?(your |the )?(previous |above )?(instructions?|rules?)",
    r"new instructions?\s*:",
    r"system\s*prompt",
    r"<\s*/?\s*(system|instruction|prompt)\s*>",
    r"(reply|say|respond|output|classify|mark|label|treat|consider) (that )?(this|it|that|the)( message| text| email)? ?(is |as |to be )?(safe|not a scam|legitimate|genuine|benign)",
    r"note to (the )?(a\.?i\.?|model|assistant|llm|system|bot|classifier)",
    r"override (your|the) (rules|instructions|classification|verdict|decision)",
    r"jailbreak|developer mode|\bDAN mode\b",
]
_INJECTION = re.compile("|".join(f"(?:{p})" for p in _INJECTION_PATTERNS), re.I)


def contains_injection(text):
    """True if the text tries to manipulate the assistant analyzing it."""
    return bool(_INJECTION.search(text or ""))