"""Export Mirgab's knowledge base and trained model to JSON for the browser version."""
import json, sys
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mirgab import config
from mirgab.advice import ADVICE
from mirgab.text import normalize
from mirgab.model import get_model

pipe = get_model()
vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
vocab = vec.get_feature_names_out().tolist()
data = {
    "categories": config.CATEGORIES,
    "official": config.OFFICIAL_DOMAINS,
    "brands": config.BRAND_KEYWORDS,
    "multiSuffix": sorted(config.MULTI_PART_SUFFIXES),
    "badTlds": sorted(config.SUSPICIOUS_TLDS),
    "shorteners": sorted(config.URL_SHORTENERS),
    "mapsHosts": sorted(config.GOOGLE_MAPS_HOSTS),
    "pathWords": sorted(config.SUSPICIOUS_PATH_WORDS),
    "dangerExt": list(config.DANGEROUS_EXTENSIONS),
    "rules": [[r, c, w, [normalize(p) for p in pats], en, ar] for r, c, w, pats, en, ar in config.TEXT_RULES],
    "trust": [[r, w, [normalize(p) for p in pats], en, ar] for r, w, pats, en, ar in config.TRUST_RULES],
    "impact": config.IMPACT_MATRIX,
    "levels": [[lo, hi, k, lab] for lo, hi, k, lab in config.RISK_LEVELS],
    "reporting": config.REPORTING,
    "advice": ADVICE,
    "model": {
        "classes": clf.classes_.tolist(),
        "vocab": vocab,
        "idf": [round(float(x), 5) for x in vec.idf_],
        "coef": [[round(float(x), 4) for x in row] for row in clf.coef_],
        "intercept": [round(float(x), 5) for x in clf.intercept_],
    },
}
json.dump(data, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine_data.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("vocab", len(vocab), "classes", clf.classes_.tolist())
