"""
ScamShield - AI reasoning layer (local, via Ollama).
Catches scams the rules miss by having a local LLM read the message.
Run it with:  python ai_brain.py
Requires: Ollama running + the 'llama3' model.
"""
import json
import ollama

MODEL = "llama3"

SYSTEM = (
    "You are a scam and phishing detector. "
    "Decide whether a message is a scam, phishing, or fraud attempt. "
    "Reply with ONLY a JSON object, no other text, in this exact shape: "
    '{"verdict": "SCAM" or "SAFE", "confidence": 0-100, "reason": "one short sentence"}.'
)


def ai_analyze(text):
    """Ask the local LLM whether `text` is a scam. Returns a dict."""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Message: {text}"},
            ],
            format="json",               # force valid JSON output
            options={"temperature": 0},  # consistent, not creative
        )
        raw = response["message"]["content"]
        data = json.loads(raw)
        return {
            "verdict": str(data.get("verdict", "SAFE")).upper(),
            "confidence": int(data.get("confidence", 0)),
            "reason": data.get("reason", ""),
        }
    except Exception as e:
        # If the AI is unavailable, fail safe - don't crash the whole check.
        return {"verdict": "UNKNOWN", "confidence": 0, "reason": f"AI unavailable: {e}"}


if __name__ == "__main__":
    tests = [
        "register here, you won 1 lakh",
        "Hey, are we still on for lunch tomorrow?",
        "Your KYC is pending. Update it today to avoid account block.",
    ]
    for t in tests:
        result = ai_analyze(t)
        print(f"\nMessage: {t}")
        print(f"  -> {result['verdict']} (confidence {result['confidence']})")
        print(f"     {result['reason']}")