"""
ScamShield - scam/phishing message detector (core logic).
Pure Python, no dependencies.
Run it with:  python detector.py
"""
import re
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    DANGEROUS = "DANGEROUS"


# Each rule is: (name, points, pattern to look for, reason to show the user)
RULES = [
    ("URGENCY", 20,
     r"urgent|immediately|right now|within \d+ (hours?|minutes?)|suspended|expire",
     "Creates false time pressure so you act before thinking."),

    ("OTP_REQUEST", 35,
     r"\b(otp|one[- ]?time (code|password|pin)|verification code)\b",
     "Asks for a one-time code. No real company ever asks you to share this."),

    ("CREDENTIAL_REQUEST", 30,
     r"verify your (account|identity|password)|confirm your (login|details)",
     "Asks you to verify your credentials - a classic phishing move."),

    ("PAYMENT_DEMAND", 30,
     r"gift ?card|wire transfer|bitcoin|crypto|pay a (fee|fine)",
     "Demands payment by untraceable methods scammers prefer."),

    ("PRIZE_LURE", 20,
     r"you (have |'ve )won|congratulations|claim your (prize|reward|refund)",
     "Promises a prize or refund you never signed up for."),

    ("LINK", 10,
     r"http://|https://|www\.",
     "Contains a link - be careful where it actually leads."),
]


def analyze(text):
    """Score a message and return (risk_level, score, reasons)."""
    text = (text or "").strip()
    score = 0
    reasons = []
    for name, points, pattern, reason in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            score += points
            reasons.append(reason)

    if score >= 60:
        level = RiskLevel.DANGEROUS
    elif score >= 25:
        level = RiskLevel.SUSPICIOUS
    else:
        level = RiskLevel.SAFE
    return level, score, reasons


# This block runs only when you do `python detector.py` directly.
if __name__ == "__main__":
    tests = [
        "URGENT: your bank account will be suspended. Share the OTP to verify your identity now.",
        "Hey, are we still on for lunch tomorrow at 1?",
    ]
    for t in tests:
        level, score, reasons = analyze(t)
        print(f"\nMessage: {t}")
        print(f"  -> {level.value} (score {score})")
        for r in reasons:
            print(f"     - {r}")