"""
ScamShield - phishing URL detector (pure Python, no dependencies).
Catches the tricks scammers hide in links.
Run:  python link_detector.py
"""
import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly","tinyurl.com","t.co","is.gd","cutt.ly","rb.gy","goo.gl","ow.ly","buff.ly","shorturl.at"}
BAD_TLDS = {"tk","top","xyz","gq","ml","cf","ga","zip","mov","click","country","kim","work","party","review"}
BRANDS = ["paypal","amazon","apple","microsoft","google","netflix","whatsapp","instagram","facebook",
          "sbi","hdfc","icici","axis","paytm","phonepe","gpay","irctc","aadhaar","kyc"]
CRED_WORDS = ["login","signin","verify","secure","update","account","confirm","password","bank","otp","kyc","wallet"]


def _parse(url):
    if not re.match(r"^[a-z]+://", url, re.I):
        url = "http://" + url          # assume http if no scheme, so we can parse the host
    return urlparse(url)


def analyze_link(url):
    """Score a URL for phishing risk. Returns a dict (same shape as the message detector)."""
    url = (url or "").strip()
    if not url:
        return {"risk_level": "SAFE", "score": 0, "signals": []}
    p = _parse(url)
    host = (p.hostname or "").lower()
    score = 0
    signals = []

    def add(pts, reason):
        nonlocal score
        score += pts
        signals.append(reason)

    if "@" in (p.netloc or ""):
        add(40, "Uses an '@' trick to hide the real destination after a trusted-looking name.")
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        add(30, "Links to a raw IP address instead of a real domain name.")
    if "xn--" in host:
        add(30, "Uses punycode - letters that imitate a real brand's name.")
    if host in SHORTENERS:
        add(25, "A shortened link that hides where it really goes.")
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in BAD_TLDS:
        add(25, f"Uses a '.{tld}' domain, a type often used by scams.")
    for b in BRANDS:
        if b in host.replace("-", "").replace(".", ""):
            if not re.match(rf"^(www\.)?{re.escape(b)}\.(com|in|co\.in|net|org)$", host):
                add(30, f"Pretends to be '{b}' but isn't its real website.")
                break
    full = (host + (p.path or "")).lower()
    if any(w in full for w in CRED_WORDS) and score > 0:
        add(10, "Mentions logins/verification in the link - typical of phishing pages.")
    if p.scheme == "http":
        add(6, "Not a secure (https) link.")
    if host.count("-") >= 2 or host.count(".") >= 4:
        add(10, "Oddly complex domain with many hyphens or subdomains.")

    score = min(score, 100)
    level = "DANGEROUS" if score >= 50 else "SUSPICIOUS" if score >= 25 else "SAFE"
    return {"risk_level": level, "score": score, "signals": signals}


if __name__ == "__main__":
    tests = [
        "http://paypal-secure-login.tk/verify",
        "https://bit.ly/3xYzAbc",
        "http://amazon.com@evil-site.xyz/login",
        "https://hdfcbank-kyc-update.top/confirm",
        "https://www.google.com",
    ]
    for t in tests:
        r = analyze_link(t)
        print(f"{r['risk_level']:10s} score={r['score']:3d}  {t}")
        for s in r["signals"]:
            print(f"            - {s}")