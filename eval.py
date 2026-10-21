"""
ScamShield - evaluation harness.
A harder, diverse benchmark: subtle social-engineering, Hinglish (Romanized
Hindi), and legitimate look-alikes, to measure the system honestly. Compares the
fast layer (rules + links) vs the full hybrid (rules + links + AI). Writes METRICS.md.
Run:  python eval.py   (the hybrid pass calls llama3 - a few minutes)
"""
import time
from check import check_message

DATASET = [
    # ===== SCAMS (English, incl. subtle social-engineering) =====
    ("URGENT: account suspended. Verify your identity and share the OTP now.", "scam"),
    ("Congratulations! You won a lottery of Rs 10,00,000. Claim your prize now.", "scam"),
    ("Your KYC is pending. Update at hdfc-kyc-verify.top/login to avoid block.", "scam"),
    ("Your parcel is on hold. Pay a customs fee via UPI to release it.", "scam"),
    ("Your electricity will be disconnected tonight. Call 9XXXX immediately.", "scam"),
    ("Work-from-home job! Pay Rs 2000 refundable deposit to start earning.", "scam"),
    ("Your PayPal is limited. Confirm details at paypal-secure-login.tk/verify", "scam"),
    ("I am a prince and need help to transfer 10 million dollars, send bank details.", "scam"),
    ("Income Tax refund of Rs 15,490 approved. Submit your account number to receive it.", "scam"),
    ("Free iPhone! Just pay the shipping fee with a Google Play gift card.", "scam"),
    ("Hi, this is Microsoft support. Your PC has a virus, allow remote access to fix it.", "scam"),
    ("Loan approved! Share your Aadhaar and OTP to receive Rs 50,000 instantly.", "scam"),
    ("Your Netflix payment failed. Update your card at netflix-billing-update.click", "scam"),
    ("amazon order issue, verify at amazon.com@secure-check.xyz/login", "scam"),
    ("Final notice: pay your tax penalty within 2 hours or face arrest.", "scam"),
    ("Reply with your UPI PIN to receive your Rs 5000 promotion money.", "scam"),
    ("Hi, bank fraud team here. We detected suspicious activity. Confirm your card's last 4 digits and the OTP we sent.", "scam"),
    ("Dad, I lost my phone, this is my new number. I'm stuck, transfer 5000 urgently, explain later.", "scam"),
    ("Your BlueDart package is held, incomplete address. Update: bluedart-redelivery.xyz", "scam"),
    ("Investment opportunity: double your money in 30 days, guaranteed. Join our Telegram.", "scam"),
    ("You have a pending Rs 2,500 cashback. Accept the collect request on your UPI app to receive it.", "scam"),
    ("Your power will be cut tonight, bill pending. Pay now: billpay-fast.top", "scam"),
    # ===== SCAMS (Hinglish) =====
    ("Aapka SBI account block ho gaya hai. Turant KYC update karein sbi-kyc.top warna band ho jayega.", "scam"),
    ("Badhai ho! Aap 25 lakh ki lottery jeet gaye. Apna bank detail bhejein claim karne ke liye.", "scam"),
    ("Sir aapke naam par parcel hai, customs fee 999 rupaye pay karein warna wapas chala jayega.", "scam"),
    ("Paise double karna hai? Abhi invest karein aur 1 mahine me double returns payein.", "scam"),
    ("KBC lottery winner! Aapko 25 lakh mila hai, processing fee bharein.", "scam"),
    ("Bank verification ke liye apna OTP abhi batayein warna account band.", "scam"),
    # ===== LEGIT (everyday) =====
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
    ("The meeting notes are in the shared drive.", "safe"),
    # ===== LEGIT (hard: look scammy but real) =====
    ("Your OTP for login is 834512. Valid for 10 minutes. Do not share with anyone.", "safe"),
    ("Reminder: your electricity bill of Rs 842 is due on Oct 25. Pay via the official app.", "safe"),
    ("We noticed a new login from Chrome on Windows. If this was you, no action needed.", "safe"),
    ("Your subscription renews on Nov 1 for Rs 499. Manage anytime in Settings.", "safe"),
    ("Congratulations! Your leave request has been approved by your manager.", "safe"),
    ("Your refund of Rs 1,200 for order #55 has been processed to your original payment method.", "safe"),
    ("Hi, this is Dr. Rao's clinic confirming your appointment tomorrow at 11 AM.", "safe"),
    ("Your UPI payment of Rs 250 to Zomato is successful. Ref 12345.", "safe"),
    ("Your flight is delayed by 2 hours. New boarding 4:30 PM, gate 14.", "safe"),
    # ===== LEGIT (Hinglish) =====
    ("Beta, khana kha liya? Call karna jab free ho.", "safe"),
    ("Kal office meeting 10 baje hai, mat bhoolna.", "safe"),
    ("Aapka Amazon order kal deliver hoga, track karein app me.", "safe"),
    ("Party kab rakh rahe ho? Bahut time ho gaya mile hue.", "safe"),
]


def evaluate(use_ai):
    tp = fp = tn = fn = 0
    fns, fps = [], []
    t0 = time.perf_counter()
    for text, label in DATASET:
        predicted_scam = check_message(text, use_ai=use_ai)["risk_level"] != "SAFE"
        if label == "scam" and predicted_scam:
            tp += 1
        elif label == "scam":
            fn += 1; fns.append(text)
        elif label == "safe" and predicted_scam:
            fp += 1; fps.append(text)
        else:
            tn += 1
    n = len(DATASET)
    acc = (tp + tn) / n
    prec = tp / (tp + fp) if (tp + fp) else 0
    rec = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0
    return dict(acc=acc, prec=prec, rec=rec, f1=f1, tp=tp, fp=fp, tn=tn, fn=fn,
                fns=fns, fps=fps, secs=time.perf_counter() - t0, n=n)


def fmt(m):
    return (f"Accuracy {m['acc']*100:.1f}% | Precision {m['prec']*100:.1f}% | "
            f"Recall {m['rec']*100:.1f}% | F1 {m['f1']*100:.1f}%  "
            f"(TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']})")


if __name__ == "__main__":
    print("Evaluating FAST layer (rules + links only)...")
    fast = evaluate(use_ai=False)
    print("  " + fmt(fast) + f"  [{fast['secs']:.2f}s]")

    print("\nEvaluating FULL HYBRID (rules + links + AI)...")
    print("  (calls llama3 per message - please wait a few minutes)")
    hyb = evaluate(use_ai=True)
    print("  " + fmt(hyb) + f"  [{hyb['secs']:.1f}s]")

    with open("METRICS.md", "w", encoding="utf-8") as f:
        f.write("# ScamShield - Evaluation Results\n\n")
        f.write(f"**Benchmark:** {fast['n']} messages "
                f"({fast['tp']+fast['fn']} scam, {fast['tn']+fast['fp']} legitimate), "
                "a developer-authored set spanning subtle social-engineering, "
                "Hinglish (Romanized Hindi), and legitimate look-alikes (real OTPs, "
                "refunds, security notices). It is intentionally hard; a small labeled "
                "set like this indicates direction, not production performance.\n\n")
        f.write("| Configuration | Accuracy | Precision | Recall | F1 |\n")
        f.write("|---|---|---|---|---|\n")
        f.write(f"| Rules + links only | {fast['acc']*100:.1f}% | {fast['prec']*100:.1f}% | {fast['rec']*100:.1f}% | {fast['f1']*100:.1f}% |\n")
        f.write(f"| **Full hybrid (+ AI)** | **{hyb['acc']*100:.1f}%** | **{hyb['prec']*100:.1f}%** | **{hyb['rec']*100:.1f}%** | **{hyb['f1']*100:.1f}%** |\n\n")
        f.write(f"The AI layer lifts recall from {fast['rec']*100:.1f}% to {hyb['rec']*100:.1f}% "
                f"by catching subtle and multilingual scams the deterministic rules miss. "
                f"Hybrid confusion matrix: TP={hyb['tp']}, FP={hyb['fp']}, TN={hyb['tn']}, FN={hyb['fn']}.\n\n")
        if hyb["fns"]:
            f.write("## Missed scams (false negatives)\n\n")
            for t in hyb["fns"]:
                f.write(f"- {t}\n")
            f.write("\n")
        if hyb["fps"]:
            f.write("## False alarms (false positives)\n\n")
            for t in hyb["fps"]:
                f.write(f"- {t}\n")
    print("\nWrote METRICS.md")