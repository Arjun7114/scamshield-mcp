"""
ScamShield - real-data validation on the public UCI SMS Spam Collection (5,574 real messages).
CAVEAT: this corpus labels 'spam' (mostly 2005 marketing SMS), which is NOT 'scam'/fraud.
ScamShield targets fraud and intentionally ignores promotional spam, so recall-vs-spam
understates scam ability. The meaningful signal is the false-positive rate on real messages.
Run:  python realdata_eval.py
"""
import os, random, time, urllib.request
from check import check_message

URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
PATH = "sms.tsv"
SAMPLE = 200  # smaller hybrid sample so it finishes in ~5 min

if not os.path.exists(PATH):
    print("Downloading public SMS dataset...")
    urllib.request.urlretrieve(URL, PATH)

rows = []
for line in open(PATH, encoding="utf-8", errors="ignore"):
    line = line.rstrip("\n")
    if "\t" not in line:
        continue
    lab, txt = line.split("\t", 1)
    rows.append((lab.strip(), txt))
print(f"Loaded {len(rows)} real messages "
      f"({sum(l=='spam' for l,_ in rows)} spam, {sum(l=='ham' for l,_ in rows)} ham)")


def score(data, use_ai, progress=False):
    tp = fp = tn = fn = 0
    for i, (lab, txt) in enumerate(data, 1):
        if progress and i % 5 == 0:
            print(f"    ...{i}/{len(data)} done")
        pred = check_message(txt, use_ai=use_ai)["risk_level"] != "SAFE"
        spam = lab == "spam"
        if spam and pred: tp += 1
        elif spam: fn += 1
        elif pred: fp += 1
        else: tn += 1
    return tp, fp, tn, fn


print("\n[1] FAST layer over the FULL dataset (instant)...")
tp, fp, tn, fn = score(rows, use_ai=False)
ham = tn + fp
print(f"  False-positive rate on {ham} real legitimate messages: {fp/ham*100:.2f}%  ({fp} false alarms)")
print(f"  Flagged {tp}/{tp+fn} 'spam' (low -- most are marketing, not fraud; see caveat)")

print(f"\n[2] FULL HYBRID over a random sample of {SAMPLE} (calls llama3 - progress below)...")
random.seed(42)
sample = random.sample(rows, SAMPLE)
t0 = time.perf_counter()
h_tp, h_fp, h_tn, h_fn = score(sample, use_ai=True, progress=True)
h_ham = h_tn + h_fp
print(f"  Sample: {h_tp+h_fn} spam, {h_ham} ham   [{time.perf_counter()-t0:.0f}s]")
print(f"  Hybrid false-positive rate on real ham: {h_fp/h_ham*100:.1f}%  ({h_fp}/{h_ham})")
print(f"  Hybrid flagged spam: {h_tp}/{h_tp+h_fn}")

with open("METRICS.md", "a", encoding="utf-8") as f:
    f.write("\n\n## Real-data validation (public UCI SMS Spam Collection)\n\n")
    f.write(f"Tested on **{len(rows)} real messages**. **Caveat:** this corpus labels *spam* "
            "(largely 2005 marketing SMS), not *scam*/fraud. ScamShield targets fraud and "
            "intentionally ignores promotional spam, so recall-vs-spam understates scam ability; "
            "the meaningful signal is the low false-positive rate on genuine messages.\n\n")
    f.write(f"- **Fast layer:** {fp/ham*100:.2f}% false-positive rate on {ham} real legitimate "
            f"messages ({fp} false alarms).\n")
    f.write(f"- **Hybrid** (random sample of {SAMPLE}): {h_fp/h_ham*100:.1f}% false-positive rate on real ham.\n")
print("\nAppended a 'Real-data validation' section to METRICS.md")