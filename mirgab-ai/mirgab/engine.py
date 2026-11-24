"""
Mirgab decision engine - combines three independent "eyes":

  1. URL intelligence   (structure, impersonation, typosquatting, redirects)
  2. Content rules      (expert knowledge of UAE fraud patterns, AR + EN)
  3. Machine learning   (TF-IDF + Logistic Regression, explainable)

...plus community reports, then produces:
  - a 0-100 risk score and level
  - the fraud domain(s) detected (multi-domain)
  - a multi-dimensional impact profile (financial / health / identity / social)
  - human-readable reasons (Explainable AI) and protective advice
"""
from collections import defaultdict

from . import model, storage
from .advice import ADVICE
from .config import CATEGORIES, IMPACT_MATRIX, RISK_LEVELS, REPORTING
from .text import detect_indicators, extract_urls, extract_phones
from .url_analyzer import analyze_url


def _noisy_or(weights):
    p = 1.0
    for w in weights:
        p *= (1.0 - max(0.0, min(w, 0.95)))
    return 1.0 - p


def _level(score):
    for lo, hi, key, label in RISK_LEVELS:
        if lo <= score < hi:
            return key, label
    return "critical", RISK_LEVELS[-1][3]


def analyze(text: str = "", url: str = "", log: bool = True) -> dict:
    text = (text or "").strip()
    url = (url or "").strip()

    # If the user only pasted a URL into the text box, treat it as a URL
    urls = ([url] if url else []) + [u for u in extract_urls(text) if u != url]
    only_url = bool(urls) and text.replace(urls[0], "").strip() == "" if text else bool(url)
    content = "" if only_url else text

    flags, trust, url_reports = [], [], []
    has_maps = False
    official_hit = None
    primary_domain = ""

    # ---------------- 1. URL intelligence ----------------
    url_results = []
    for u in urls[:5]:
        r = analyze_url(u)
        url_results.append({"url": u, "host": r["host"], "official": r["official"],
                            "flags": len(r["flags"])})
        flags += r["flags"]
        trust += r["trust"]
        has_maps = has_maps or r["is_maps"]
        official_hit = official_hit or r["official"]
        dom = r["registered_domain"] or r["host"]
        primary_domain = primary_domain or dom
        n = storage.report_count(dom)
        if n:
            url_reports.append(dom)
            flags.append({"id": "community_report", "category": "generic", "weight": min(0.6 + 0.1 * n, 0.9),
                          "evidence": [dom], "source": "community",
                          "en": f"Reported as fraud by the community ({n} report{'s' if n > 1 else ''})",
                          "ar": f"تم الإبلاغ عنه كاحتيال من قِبل المجتمع ({n} بلاغ)"})

    if has_maps:
        flags.append({"id": "maps_link", "category": "maps", "weight": 0.10, "evidence": [],
                      "source": "url",
                      "en": "Google Maps link - the map itself is safe, but listing phone numbers/websites can be hijacked",
                      "ar": "رابط Google Maps - الخريطة آمنة لكن أرقام ومواقع النتائج قد يتم التلاعب بها"})

    # ---------------- 2. Content rules ----------------
    if content:
        f, t = detect_indicators(content)
        flags += f
        trust += t

    # ---------------- 3. Machine learning ----------------
    ml = None
    if content and len(content) >= 15:
        ml = model.predict(content)
        # Down-weight the model when it barely recognises the text
        reliability = min(1.0, ml["known_vocabulary"] / 6.0)
        ml["reliability"] = round(reliability, 2)

    # ---------------- Fusion ----------------
    url_score = _noisy_or([x["weight"] for x in flags if x["source"] in ("url", "community")])
    rule_score = _noisy_or([x["weight"] for x in flags if x["source"] == "text"])
    ml_score = (ml["fraud_probability"] * ml["reliability"]) if ml else 0.0

    # Official-domain trust cancels URL risk but only slightly lowers content risk:
    # scammers often paste a real bank link next to a fake phone number.
    url_trust = sum(x["weight"] for x in trust if x["source"] == "url")
    text_trust = sum(x["weight"] for x in trust if x["source"] == "text")
    url_score *= (1.0 - min(url_trust * 2, 1.0))
    combined = _noisy_or([url_score, rule_score * 0.9, ml_score * 0.75])
    trust_total = min(text_trust + 0.3 * url_trust, 0.7)
    combined *= (1.0 - trust_total)
    if url_reports:
        combined = max(combined, 0.85)
    score = int(round(100 * combined))
    level_key, level_label = _level(score)

    # ---------------- Category (multi-domain) ----------------
    votes = defaultdict(float)
    for x in flags:
        if x["category"] != "generic":
            votes[x["category"]] += x["weight"]
    if ml and ml["fraud_probability"] > 0.4:
        votes[ml["likely_category"]] += ml["fraud_probability"] * 0.6 * ml["reliability"]
    ranked = sorted(votes.items(), key=lambda kv: kv[1], reverse=True)
    if score < 25:
        primary = "legit"
    elif ranked:
        primary = ranked[0][0]
    elif ml:
        primary = ml["likely_category"]
    else:
        primary = "impersonation"  # suspicious link with no content: phishing is most common
    if primary != "legit" and not ranked:
        ranked = [(primary, 1.0)]
    total_votes = sum(v for _, v in ranked) or 1.0
    domains = [{"key": k, "en": CATEGORIES[k]["en"], "ar": CATEGORIES[k]["ar"],
                "share": round(v / total_votes, 2)} for k, v in ranked[:3]]

    # ---------------- Multi-dimensional impact ----------------
    impact = {d: 0.0 for d in ("financial", "health", "identity", "social")}
    for k, v in ranked:
        for d in impact:
            impact[d] = max(impact[d], IMPACT_MATRIX[k][d] * (0.5 + 0.5 * v / total_votes))
    if any(x["id"] == "sensitive_data" for x in flags):
        impact["identity"] = max(impact["identity"], 0.9)
    impact = {d: int(round(100 * v * combined)) for d, v in impact.items()}

    # ---------------- Explanations & advice ----------------
    reasons = sorted(flags, key=lambda x: x["weight"], reverse=True)
    reasons_out = [{"en": x["en"], "ar": x["ar"], "weight": round(x["weight"], 2),
                    "source": x["source"], "evidence": x["evidence"]} for x in reasons]
    trust_out = [{"en": x["en"], "ar": x["ar"], "weight": round(x["weight"], 2)} for x in trust]

    if score < 25:
        adv_keys = ["safe"]
    else:
        adv_keys = [d["key"] for d in domains if d["key"] in ADVICE][:2] + ["generic"]
    advice = {"en": [a for k in adv_keys for a in ADVICE[k]["en"]],
              "ar": [a for k in adv_keys for a in ADVICE[k]["ar"]]}

    input_type = "url+text" if (urls and content) else "url" if urls else "text"
    if log:
        try:
            storage.log_scan(input_type, primary_domain, score, level_key, primary)
        except Exception:
            pass

    return {
        "score": score,
        "level": level_key,
        "level_label": level_label,
        "category": {"key": primary, **CATEGORIES[primary]},
        "domains": domains,
        "impact": impact,
        "reasons": reasons_out,
        "trust_signals": trust_out,
        "advice": advice,
        "report_channels": REPORTING if score >= 50 else None,
        "components": {"url": int(url_score * 100), "content_rules": int(rule_score * 100),
                       "ml": int(ml_score * 100), "trust_reduction": int(trust_total * 100)},
        "ml": ml,
        "urls": url_results,
        "phones": extract_phones(text),
        "official_entity": official_hit,
        "input_type": input_type,
        "primary_domain": primary_domain,
    }
