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
# Each rule is: (name, points, pattern to look for, reason to show the user)
RULES = [
    ("URGENCY", 20,
     r"urgent|immediate(ly)?|right now|act now|within \d+\s*(hours?|minutes?|hrs?|mins?)|suspend(ed|ing)?|expir(e|es|ed|ing)|final (notice|warning)|last chance",
     "Creates false time pressure so you act before thinking."),

    ("OTP_REQUEST", 35,
     r"\b(otp|one[- ]?time (code|password|pin)|verification code|security code|2fa)\b",
     "Asks for a one-time code. No real company ever asks you to share this."),

    ("CREDENTIAL_REQUEST", 30,
     r"verify your (account|identity|password|details)|confirm your (login|details|identity|password)|(enter|update|provide|submit) your (details|information|password|card|bank|account|login|credentials)|log ?in to (verify|confirm|secure|your account)",
     "Asks you to enter or verify your personal details - a classic phishing move."),

    ("PAYMENT_DEMAND", 30,
     r"gift ?card|wire transfer|western union|moneygram|bitcoin|crypto|btc|usdt|pay (a |the )?(fee|fine|tax|penalty|charge)|processing fee",
     "Demands payment by untraceable methods scammers prefer."),

    ("PRIZE_LURE", 25,
     r"\byou('?ve| have)? won\b|congratulations|claim your (prize|reward|refund|gift)|(won|win) (a |the )?(prize|lottery|contest|reward|gift|cash)|lottery|lucky draw|selected as (a |the )?winner|free (gift|prize|iphone|voucher|reward)|get (your )?reward",
     "Promises a prize, reward, or winnings you never signed up for."),

    ("CLICK_LURE", 15,
     r"click (here|this|the link|below)|tap (here|this|the link)|open (this |the )?link|follow this link",
     "Pushes you to click a link - a common way to reach a fake site."),

    ("LINK", 10,
     r"https?://|www\.",
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
# This block runs only when you do `python detector.py` directly.
if __name__ == "__main__":
    print("ScamShield - type a message to check it (or 'quit' to exit).\n")
    while True:
        text = input("Message> ")
        if text.strip().lower() in ("quit", "exit", "q"):
            break
        level, score, reasons = analyze(text)
        print(f"  -> {level.value} (score {score})")
        for r in reasons:
            print(f"     - {r}")
        print()