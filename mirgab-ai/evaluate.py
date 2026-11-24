"""Evaluate Mirgab and print the numbers reported in the documentation.

    python evaluate.py

1. Synthetic hold-out split (from train.py) - shows the model learned the seed data;
   NOT a real-world benchmark because train and test come from the same templates.
2. Hand-written realistic set (data/realistic_test.csv) through the FULL engine
   (URL + rules + ML fusion), fraud = score >= 50.
"""
import csv
import os
from collections import Counter

from mirgab import analyze
from mirgab.model import train

ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print("=== 1. ML model on synthetic hold-out split ===")
    _, rep = train(save=True, verbose=False)
    print(f"accuracy {rep['accuracy']:.3f}  macro-F1 {rep['macro avg']['f1-score']:.3f}  (same-template split: optimistic)\n")

    print("=== 2. Full engine on hand-written realistic set ===")
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "realistic_test.csv"), encoding="utf-8")))
    tp = tn = fp = fn = cat_ok = 0
    per = Counter()
    for r in rows:
        a = analyze(text=r["text"], log=False)
        pred, true = a["score"] >= 50, r["label"] != "legit"
        tp += pred and true; tn += (not pred) and (not true)
        fp += pred and not true; fn += (not pred) and true
        if true and pred and a["category"]["key"] == r["label"]:
            cat_ok += 1
        per[(r["label"], pred == true)] += 1
        print(f"{a['score']:3d}/100  {a['category']['key']:13s}  expected={r['label']:13s}  {'OK ' if pred == true else 'MISS'}  {r['text'][:60]}")
    n = len(rows)
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    print(f"\n{n} messages | fraud-vs-legit accuracy {(tp + tn) / n:.2f} | precision {prec:.2f} | recall {rec:.2f} "
          f"| correct fraud domain {cat_ok}/{tp + fn}")
    print("Caveat: small set (18), and it was used while adding Gulf-dialect rules -> not an independent benchmark.")
