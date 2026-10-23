"""
ScamShield - rule engine (message scam patterns).
Run:  python detector.py   (interactive)
"""
import re
from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    DANGEROUS = "DANGEROUS"


RULES = [
    ("URGENCY", 20,
     r"urgent|immediate(ly)?|right now|act now|within \d+\s*(hours?|minutes?|hrs?|mins?)|suspend(ed|ing)?|expir(e|es|ed|ing)|final (notice|warning)|last chance",
     "Creates false time pressure so you act before thinking."),
    ("CREDENTIAL_REQUEST", 30,
     r"verify your (account|identity|password|details)|confirm your (login|details|identity|password)|(enter|update|provide|submit) your (details|information|password|card|bank|account|login|credentials)|log ?in to (verify|confirm|secure|your account)",
     "Asks you to enter or verify your personal details - a classic phishing move."),
    ("PAYMENT_DEMAND", 30,
     r"gift ?card|wire transfer|western union|moneygram|bitcoin|crypto|btc|usdt|pay (a |the )?(fee|fine|tax|penalty|charge)|processing fee",
     "Demands payment by untraceable methods scammers prefer."),
    ("PRIZE_LURE", 25,
     r"\byou('?ve| have)? won\b|claim your (prize|reward|refund|gift)|(won|win) (a |the )?(prize|lottery|contest|reward|gift|cash)|lottery|lucky draw|selected as (a |the )?winner|free (gift|prize|iphone|voucher|reward)|get (your )?reward",
     "Promises a prize, reward, or winnings you never signed up for."),
    ("CLICK_LURE", 15,
     r"click (here|this|the link|below)|tap (here|this|the link)|open (this |the )?link|follow this link",
     "Pushes you to click a link - a common way to reach a fake site."),
    ("LINK", 10,
     r"https?://|www\.",
     "Contains a link - be careful where it actually leads."),
]

# Secret/credential sharing is handled with context so that an INFORMATIONAL
# message ("do not share your OTP") is not mistaken for a REQUEST to share one.
SECRET_WORD = re.compile(r"\b(otp|one[- ]?time (?:code|password|pin)|verification code|security code|2fa|upi pin|atm pin|card pin|cvv|password|pin number)\b", re.I)
SHARE_VERB = re.compile(r"\b(share|send|give|provide|tell|read out|forward|resend|enter|reply with)\b", re.I)
NO_SHARE = re.compile(r"\b(do not|don'?t|never|not)\b[^.]{0,15}\b(share|send|give|disclose|reveal|tell|provide)\b", re.I)


def analyze(text):
    """Score a message and return (risk_level, score, reasons)."""
    text = (text or "").strip()
    score = 0
    reasons = []
    for name, points, pattern, reason in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            score += points
            reasons.append(reason)

    if SECRET_WORD.search(text) and SHARE_VERB.search(text) and not NO_SHARE.search(text):
        score += 35
        reasons.append("Asks you to share a secret code or credential (OTP, PIN, password) - no real company asks for this.")

    if score >= 60:
        level = RiskLevel.DANGEROUS
    elif score >= 25:
        level = RiskLevel.SUSPICIOUS
    else:
        level = RiskLevel.SAFE
    return level, score, reasons


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