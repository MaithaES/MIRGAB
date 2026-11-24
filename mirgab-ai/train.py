"""Train (or retrain) the Mirgab text model.

    python train.py

Add your own labelled samples to data/extra_samples.csv (columns: text,label)
with labels: legit, real_estate, pharma, fake_store, investment, impersonation
"""
from mirgab.model import train, MODEL_PATH

if __name__ == "__main__":
    _, report = train()
    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Hold-out accuracy: {report['accuracy']:.3f}   macro-F1: {report['macro avg']['f1-score']:.3f}")
