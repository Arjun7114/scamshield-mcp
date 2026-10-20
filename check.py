"""
ScamShield - combined check (rules + links + AI).
Rules and link analysis run instantly; the AI adds judgment when needed.
Run:  python check.py
"""
import re
import time
from detector import analyze, RiskLevel
from ai_brain import ai_analyze
from link_detector import analyze_link

URL_RE = re.compile(
    r"(https?://\S+|www\.\S+|\b[a-z0-9][a-z0-9-]*\.(?:com|net|org|in|co|io|tk|top|xyz|info|click|live|app)(?:/\S*)?)",
    re.I,
)


def check_message(text, use_ai=True):
    t0 = time.perf_counter()

    # 1. Fast rule layer on the text
    level, score, reasons = analyze(text)

    # 2. Scan any links inside the message
    for found in URL_RE.findall(text or ""):
        link = analyze_link(found)
        if link["signals"]:
            reasons = reasons + link["signals"]
        if link["risk_level"] == "DANGEROUS":
            level = RiskLevel.DANGEROUS
        elif link["risk_level"] == "SUSPICIOUS" and level == RiskLevel.SAFE:
            level = RiskLevel.SUSPICIOUS

    # 3. AI layer - only when not already certain it's dangerous
    ai = None
    if use_ai and level != RiskLevel.DANGEROUS:
        ai = ai_analyze(text)
        if ai["verdict"] == "SCAM" and ai["confidence"] >= 60:
            level = RiskLevel.DANGEROUS if ai["confidence"] >= 80 else RiskLevel.SUSPICIOUS
            reasons = reasons + [ai["reason"]]

    elapsed = (time.perf_counter() - t0) * 1000
    return {
        "risk_level": level.value,
        "rule_score": score,
        "reasons": reasons,
        "ai": ai,
        "time_ms": round(elapsed, 1),
    }


if __name__ == "__main__":
    tests = [
        "You won 5 lakhs! Claim at hdfcbank-kyc-update.top/confirm now",
        "URGENT: your bank account will be suspended. Share the OTP now.",
        "Hey, are we still on for lunch tomorrow?",
    ]
    for t in tests:
        r = check_message(t)
        note = " (AI consulted)" if r["ai"] else " (rules/links only - instant)"
        print(f"\nMessage: {t}")
        print(f"  -> {r['risk_level']}  [{r['time_ms']} ms]{note}")
        for reason in r["reasons"]:
            print(f"     - {reason}")