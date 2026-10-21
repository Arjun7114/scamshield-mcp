# ScamShield - Evaluation Results

**Benchmark:** 56 messages (28 scam, 28 legitimate), a developer-authored set spanning subtle social-engineering, Hinglish (Romanized Hindi), and legitimate look-alikes (real OTPs, refunds, security notices). It is intentionally hard; a small labeled set like this indicates direction, not production performance.

| Configuration | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Rules + links only | 76.8% | 100.0% | 53.6% | 69.8% |
| **Full hybrid (+ AI)** | **98.2%** | **96.6%** | **100.0%** | **98.2%** |

The AI layer lifts recall from 53.6% to 100.0% by catching subtle and multilingual scams the deterministic rules miss. Hybrid confusion matrix: TP=28, FP=1, TN=27, FN=0.

## False alarms (false positives)

- Your OTP for login is 834512. Valid for 10 minutes. Do not share with anyone.
