"""Machine-learning text classifier with built-in explanations (Explainable AI).

Model: TF-IDF (word 1-2 grams, Arabic-normalised) + multinomial Logistic Regression.
Why this model: it is fast, works offline, handles Arabic + English together and
is *transparent* - every prediction can be decomposed into the words that
pushed it towards "fraud", which is what the user sees as "why".
"""
import csv
import os

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

from .dataset import build_dataset
from .text import normalize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "data", "mirgab_model.joblib")
EXTRA_DATA = os.path.join(BASE_DIR, "data", "extra_samples.csv")


def _load_extra():
    rows = []
    if os.path.exists(EXTRA_DATA):
        with open(EXTRA_DATA, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("text") and r.get("label"):
                    rows.append((r["text"], r["label"].strip()))
    return rows


def train(save: bool = True, verbose: bool = True):
    rows = build_dataset() + _load_extra()
    texts, labels = zip(*rows)
    X_tr, X_te, y_tr, y_te = train_test_split(texts, labels, test_size=0.2,
                                              random_state=7, stratify=labels)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=normalize, ngram_range=(1, 2),
                                  min_df=2, sublinear_tf=True,
                                  token_pattern=r"(?u)\b\w\w+\b")),
        ("clf", LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced")),
    ])
    pipe.fit(X_tr, y_tr)
    report = classification_report(y_te, pipe.predict(X_te), output_dict=True, zero_division=0)
    if verbose:
        print(classification_report(y_te, pipe.predict(X_te), zero_division=0))
    pipe.fit(texts, labels)  # refit on everything for the shipped model
    if save:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(pipe, MODEL_PATH)
    return pipe, report


_MODEL = None


def get_model():
    """Load the trained model, or train it on first run (takes a few seconds).

    The model file is not committed to git: a pickle made with one scikit-learn
    version may not load in another, so retraining locally is the safe default.
    """
    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = joblib.load(MODEL_PATH)
        except Exception:
            _MODEL = train(verbose=False)[0]
    return _MODEL


def predict(text: str, top_k: int = 6) -> dict:
    """Return fraud probability, most likely category and word-level explanation."""
    pipe = get_model()
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    X = vec.transform([text])
    proba = clf.predict_proba(X)[0]
    classes = list(clf.classes_)
    p = dict(zip(classes, proba))
    fraud_prob = 1.0 - p.get("legit", 0.0)
    fraud_classes = [c for c in classes if c != "legit"]
    category = max(fraud_classes, key=lambda c: p[c])

    # Explanation: contribution of each present word = tfidf * (w_category - w_legit)
    ci, li = classes.index(category), classes.index("legit") if "legit" in classes else None
    w = clf.coef_[ci] - (clf.coef_[li] if li is not None else 0)
    row = X.tocoo()
    contribs = [(vec.get_feature_names_out()[j], float(v * w[j])) for j, v in zip(row.col, row.data)]
    contribs.sort(key=lambda t: t[1], reverse=True)
    top_fraud = [{"term": t, "score": round(s, 3)} for t, s in contribs[:top_k] if s > 0.02]
    top_safe = [{"term": t, "score": round(s, 3)} for t, s in contribs[::-1][:3] if s < -0.02]
    return {
        "fraud_probability": float(fraud_prob),
        "category": category if fraud_prob >= 0.5 else "legit",
        "likely_category": category,
        "class_probabilities": {c: round(float(v), 3) for c, v in p.items()},
        "top_fraud_terms": top_fraud,
        "top_safe_terms": top_safe,
        "known_vocabulary": int(X.nnz),
    }
