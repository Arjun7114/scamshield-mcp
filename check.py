"""
ScamShield - combined check (rules + AI).
Rules run instantly; the AI adds judgment only when the rules aren't certain.
Run:  python check.py
"""
import time
from detector import analyze, RiskLevel
from ai_brain import ai_analyze


def check_message(text, use_ai=True):
    t0 = time.perf_counter()

    # 1. Fast rule layer - always runs, under a millisecond.
    level, score, reasons = analyze(text)

    ai = None
    # 2. AI layer - skip it only when the rules are ALREADY certain it's dangerous.
    #    Everything else (including "safe") gets a second opinion, so a cleverly
    #    worded scam that scores low on rules still gets caught.
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
        "URGENT: your bank account will be suspended. Share the OTP now.",
        "register here, you won 1 lakh",
        "Your KYC is pending. Update it today to avoid account block.",
        "Hey, are we still on for lunch tomorrow?",
    ]
    for t in tests:
        r = check_message(t)
        note = " (AI consulted)" if r["ai"] else " (rules only - instant)"
        print(f"\nMessage: {t}")
        print(f"  -> {r['risk_level']}  [{r['time_ms']} ms]{note}")
        for reason in r["reasons"]:
            print(f"     - {reason}")