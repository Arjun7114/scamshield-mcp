# ScamShield - Evaluation Results

**Benchmark:** 56 messages (28 scam, 28 legitimate), a developer-authored set spanning subtle social-engineering, Hinglish (Romanized Hindi), and legitimate look-alikes (real OTPs, refunds, security notices). It is intentionally hard; a small labeled set like this indicates direction, not production performance.

| Configuration | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| Rules + links only | 76.8% | 100.0% | 53.6% | 69.8% |
| **Full hybrid (+ AI)** | **98.2%** | **96.6%** | **100.0%** | **98.2%** |

The AI layer lifts recall from 53.6% to 100.0% by catching subtle and multilingual scams the deterministic rules miss. Hybrid confusion matrix: TP=28, FP=1, TN=27, FN=0.

## False alarms (false positives)

- Your OTP for login is 834512. Valid for 10 minutes. Do not share with anyone.


## Real-data validation (public UCI SMS Spam Collection)

Validated on the public UCI SMS Spam Collection (5,574 real messages). **Caveat:** this corpus labels *spam* (largely 2005 marketing SMS), not *scam*/fraud. ScamShield targets fraud and intentionally ignores promotional spam, so recall-vs-spam understates scam ability; the meaningful signals are the false-positive rate on genuine messages and the layer trade-off.

| Layer | False-positive rate on real legitimate messages |
|---|---|
| Rules + links (fast) | **0.17%** (8 / 4,827) |
| Full hybrid (+ AI), n=200 sample | 7.7% (13 / 169) |

The deterministic layers are extremely precise on real-world traffic (0.17% false alarms across 4,827 messages). The AI layer adds scam recall — it flagged 28/31 scam-like messages in the sample — but at a precision cost, raising false alarms to ~7.7% on real legitimate messages. This is the classic precision/recall trade-off: ScamShield is tuned to err toward warning (a missed scam is costlier than a false alarm), and reducing the AI's real-world false-positive rate (via confidence-threshold calibration or requiring layer agreement) is the top future-work item.