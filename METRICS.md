# ScamShield - Evaluation Results

Labeled dataset: **38 messages** (20 scam, 18 legitimate).

| Configuration | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Rules + links only | 76.3% | 86.7% | 65.0% | 74.3% |
| **Full hybrid (+ AI)** | **92.1%** | **87.0%** | **100.0%** | **93.0%** |

The AI layer raised recall from 65.0% to 100.0%, catching scams the deterministic rules miss.

## Remaining errors (hybrid)

- *false alarm*: Your OTP is 452198. Do not share it with anyone.
- *false alarm*: Congratulations on your work anniversary! Have a great day.
- *false alarm*: Your payment of Rs 299 to Spotify was successful.
