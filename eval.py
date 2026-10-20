"""
ScamShield - evaluation harness.
Measures accuracy on a labeled dataset, comparing the fast layer (rules + links)
against the full hybrid (rules + links + AI). Writes METRICS.md.
Run:  python eval.py   (the hybrid pass calls llama3, so it takes a few minutes)
"""
import time
from check import check_message

DATASET = [
    # ---- SCAMS ----
    ("URGENT: Your account will be suspended. Verify your identity and share the OTP now.", "scam"),
    ("Congratulations! You won a lottery of Rs 10,00,000. Claim your prize now.", "scam"),
    ("Your KYC is pending. Update today at hdfc-kyc-verify.top/login to avoid block.", "scam"),
    ("click this link and register, you have won 5 lakhs", "scam"),
    ("Your parcel is on hold. Pay a small customs fee via UPI to release it.", "scam"),
    ("Dear customer, your electricity will be disconnected tonight. Call 9XXXX immediately.", "scam"),
    ("You are selected for a work-from-home job. Pay Rs 2000 registration to start.", "scam"),
    ("Your PayPal account is limited. Confirm your details at paypal-secure-login.tk/verify", "scam"),
    ("I am a prince and need your help to transfer 10 million dollars, send your bank details.", "scam"),
    ("Income Tax refund of Rs 15,490 approved. Submit your account number to receive it.", "scam"),
    ("Get a free iPhone! Just pay the shipping fee with a Google Play gift card.", "scam"),
    ("Your SBI account is blocked. Reactivate at http://sbi.online-verify.xyz/login now.", "scam"),
    ("Hi, this is Microsoft support. Your computer has a virus, allow remote access to fix it.", "scam"),
    ("Loan approved! Share your Aadhaar and OTP to receive Rs 50,000 instantly.", "scam"),
    ("Your Netflix payment failed. Update your card at netflix-billing-update.click now.", "scam"),
    ("You have won a lucky draw. Send Rs 499 processing fee to claim your cash reward.", "scam"),
    ("amazon order issue, verify at amazon.com@secure-check.xyz/login", "scam"),
    ("Final notice: pay your pending tax penalty within 2 hours or face arrest.", "scam"),
    ("Your phone number won in our promotion. Reply with your UPI PIN to receive money.", "scam"),
    ("Update your bank details here www.icici-kyc-update.top to keep your account active.", "scam"),
    # ---- SAFE ----
    ("Hey, are we still on for lunch tomorrow at 1?", "safe"),
    ("Your Amazon order has shipped and will arrive on Tuesday.", "safe"),
    ("Your OTP is 452198. Do not share it with anyone.", "safe"),
    ("Reminder: your dentist appointment is on Friday at 4pm.", "safe"),
    ("Your October account statement is now available in the app.", "safe"),
    ("Congratulations on your work anniversary! Have a great day.", "safe"),
    ("Mom: call me when you are free, nothing urgent.", "safe"),
    ("Netflix: new episodes of your show are now available.", "safe"),
    ("Your food order is out for delivery and will arrive in 20 minutes.", "safe"),
    ("Can you send me the lecture notes from today?", "safe"),
    ("Your payment of Rs 299 to Spotify was successful.", "safe"),
    ("Team standup moved to 10am tomorrow, see you there.", "safe"),
    ("Happy birthday! Hope you have a wonderful year ahead.", "safe"),
    ("Your flight AI203 is on time, boarding at gate 12.", "safe"),
    ("Thanks for shopping with us. Your invoice is attached.", "safe"),
    ("Let's catch up this weekend, it's been a while.", "safe"),
    ("Your library book is due next Monday.", "safe"),
    ("The meeting notes are in the shared drive.", "safe"),
]


def evaluate(use_ai):
    tp = fp = tn = fn = 0
    misses = []
    t0 = time.perf_counter()
    for text, label in DATASET:
        r = check_message(text, use_ai=use_ai)
        predicted_scam = r["risk_level"] != "SAFE"
        if label == "scam" and predicted_scam:
            tp += 1
        elif label == "scam":
            fn += 1; misses.append(("missed scam", text))
        elif label == "safe" and predicted_scam:
            fp += 1; misses.append(("false alarm", text))
        else:
            tn += 1
    n = len(DATASET)
    acc = (tp + tn) / n
    prec = tp / (tp + fp) if (tp + fp) else 0
    rec = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    return dict(acc=acc, prec=prec, rec=rec, f1=f1, tp=tp, fp=fp, tn=tn, fn=fn,
                misses=misses, secs=time.perf_counter() - t0, n=n)


def fmt(m):
    return (f"Accuracy {m['acc']*100:.1f}% | Precision {m['prec']*100:.1f}% | "
            f"Recall {m['rec']*100:.1f}% | F1 {m['f1']*100:.1f}%  "
            f"(TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']})")


if __name__ == "__main__":
    print("Evaluating FAST layer (rules + links only)...")
    fast = evaluate(use_ai=False)
    print("  " + fmt(fast) + f"  [{fast['secs']:.2f}s]")

    print("\nEvaluating FULL HYBRID (rules + links + AI)...")
    print("  (this calls llama3 for each message - please wait a few minutes)")
    hyb = evaluate(use_ai=True)
    print("  " + fmt(hyb) + f"  [{hyb['secs']:.1f}s]")

    with open("METRICS.md", "w", encoding="utf-8") as f:
        f.write("# ScamShield - Evaluation Results\n\n")
        f.write(f"Labeled dataset: **{fast['n']} messages** "
                f"({fast['tp']+fast['fn']} scam, {fast['tn']+fast['fp']} legitimate).\n\n")
        f.write("| Configuration | Accuracy | Precision | Recall | F1 |\n")
        f.write("|---|---|---|---|---|\n")
        f.write(f"| Rules + links only | {fast['acc']*100:.1f}% | {fast['prec']*100:.1f}% | {fast['rec']*100:.1f}% | {fast['f1']*100:.1f}% |\n")
        f.write(f"| **Full hybrid (+ AI)** | **{hyb['acc']*100:.1f}%** | **{hyb['prec']*100:.1f}%** | **{hyb['rec']*100:.1f}%** | **{hyb['f1']*100:.1f}%** |\n\n")
        f.write(f"The AI layer raised recall from {fast['rec']*100:.1f}% to {hyb['rec']*100:.1f}%, "
                f"catching scams the deterministic rules miss.\n\n")
        if hyb["misses"]:
            f.write("## Remaining errors (hybrid)\n\n")
            for kind, t in hyb["misses"]:
                f.write(f"- *{kind}*: {t}\n")
    print("\nWrote METRICS.md")