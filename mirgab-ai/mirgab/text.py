"""Bilingual text normalisation and rule-based indicator detection."""
import re

from .config import TEXT_RULES, TRUST_RULES

_DIACRITICS = re.compile(r"[ً-ْٰـ]")  # tashkeel + tatweel
_URL_RE = re.compile(r"(https?://[^\s<>\"']+|www\.[^\s<>\"']+|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|ae|net|org|xyz|top|shop|online|site|info|io|co|me|live|vip|club|abudhabi|link|click|ly|gl)(?:/[^\s<>\"']*)?)", re.I)
_PHONE_RE = re.compile(r"(?:\+|00)\d[\d\s-]{7,}\d|\b05\d[\s-]?\d{3}[\s-]?\d{4}\b")


def normalize(text: str) -> str:
    """Lower-case and normalise Arabic so 'أ/إ/آ'->'ا', 'ة'->'ه', 'ى'->'ي'."""
    t = (text or "").lower()
    t = _DIACRITICS.sub("", t)
    t = re.sub("[إأآٱ]", "ا", t)
    t = t.replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    # Arabic-Indic digits -> Western digits
    t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_urls(text: str):
    found = []
    for m in _URL_RE.findall(text or ""):
        u = m.rstrip(".,;:!?)]}،")
        if "@" in u and "/" not in u:  # skip e-mail addresses
            continue
        if u not in found:
            found.append(u)
    return found


def extract_phones(text: str):
    return [re.sub(r"[\s-]", "", p) for p in _PHONE_RE.findall(text or "")]


def _norm_pattern(p: str) -> str:
    return normalize(p)


# Pre-normalise patterns once
_RULES = [(rid, cat, w, [_norm_pattern(p) for p in pats], en, ar)
          for rid, cat, w, pats, en, ar in TEXT_RULES]
_TRUST = [(rid, w, [_norm_pattern(p) for p in pats], en, ar)
          for rid, w, pats, en, ar in TRUST_RULES]


def _contains(norm_text: str, pattern: str) -> bool:
    if re.fullmatch(r"[a-z0-9 ]+", pattern):
        # English/ASCII: whole-word match to avoid 'pin' in 'shopping'
        return re.search(r"(?<![a-z0-9])" + re.escape(pattern) + r"(?![a-z0-9])", norm_text) is not None
    return pattern in norm_text


def detect_indicators(text: str):
    """Return (red_flags, trust_signals). Each item is a dict with evidence."""
    norm = normalize(text)
    flags, trust = [], []
    for rid, cat, w, pats, en, ar in _RULES:
        hits = [p for p in pats if _contains(norm, p)]
        if hits:
            flags.append({"id": rid, "category": cat, "weight": w,
                          "evidence": hits[:3], "en": en, "ar": ar, "source": "text"})
    for rid, w, pats, en, ar in _TRUST:
        hits = [p for p in pats if _contains(norm, p)]
        if hits:
            trust.append({"id": rid, "weight": w, "evidence": hits[:3],
                          "en": en, "ar": ar, "source": "text"})

    # A message that *warns* about OTPs ("never share your OTP") is not asking for one
    if any(t["id"] == "never_ask" for t in trust):
        flags = [f for f in flags if f["id"] != "sensitive_data"]

    # Heuristic: implausibly cheap luxury property rent
    m = re.search(r"(villa|فيلا|apartment|شقه)[^.\n]{0,60}?(\d[\d,]{2,})\s*(aed|dhs|درهم)", norm)
    if m:
        try:
            price = int(m.group(2).replace(",", ""))
            if price < 1500 and ("month" in norm or "شهري" in norm or "شهر" in norm):
                flags.append({"id": "re_price_math", "category": "real_estate", "weight": 0.25,
                              "evidence": [m.group(0)[:50]],
                              "en": f"Rent of {price} AED/month for this property type is unrealistic",
                              "ar": f"إيجار {price} درهم شهرياً لهذا النوع من العقارات غير واقعي",
                              "source": "text"})
        except ValueError:
            pass
    return flags, trust
