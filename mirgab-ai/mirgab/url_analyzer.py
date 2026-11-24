"""Offline URL / domain risk analysis.

Works without internet access.  Live intelligence (WHOIS domain age, Google
Safe Browsing, VirusTotal) can be plugged in through `intel.py` later.
"""
import ipaddress
import re
from urllib.parse import urlparse, parse_qs, unquote

from .config import (OFFICIAL_DOMAINS, BRAND_KEYWORDS, MULTI_PART_SUFFIXES,
                     SUSPICIOUS_TLDS, URL_SHORTENERS, GOOGLE_MAPS_HOSTS,
                     SUSPICIOUS_PATH_WORDS, DANGEROUS_EXTENSIONS)

_HOMOGLYPHS = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a"})


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def split_host(host: str):
    """Return (subdomain, registered_domain, tld) without needing tldextract."""
    host = host.lower().strip(".")
    labels = host.split(".")
    if len(labels) < 2:
        return "", host, ""
    last2 = ".".join(labels[-2:])
    if last2 in MULTI_PART_SUFFIXES and len(labels) >= 3:
        reg = ".".join(labels[-3:])
        sub = ".".join(labels[:-3])
        tld = last2
    else:
        reg = last2
        sub = ".".join(labels[:-2])
        tld = labels[-1]
    return sub, reg, tld


def _flag(fid, weight, en, ar, evidence=None, category="generic"):
    return {"id": fid, "category": category, "weight": weight, "evidence": evidence or [],
            "en": en, "ar": ar, "source": "url"}


def analyze_url(raw: str) -> dict:
    url = raw.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*://", url, re.I):
        url = "http://" + url if not url.lower().startswith("www.") else "http://" + url
        scheme_given = False
    else:
        scheme_given = True
    p = urlparse(url)
    host = (p.hostname or "").lower()
    flags, trust = [], []
    result = {"url": raw, "host": host, "flags": flags, "trust": trust,
              "official": None, "is_maps": False, "registered_domain": ""}
    if not host:
        flags.append(_flag("bad_url", 0.3, "Malformed URL", "رابط غير سليم"))
        return result

    # --- IP address host
    try:
        ipaddress.ip_address(host)
        flags.append(_flag("ip_host", 0.45, "Uses a raw IP address instead of a domain name",
                           "يستخدم عنوان IP مباشرة بدلاً من اسم نطاق", [host]))
        is_ip = True
    except ValueError:
        is_ip = False

    sub, reg, tld = ("", host, "") if is_ip else split_host(host)
    result["registered_domain"] = reg
    label = reg.split(".")[0]

    # --- Official / trusted
    if is_ip:
        pass
    elif reg in OFFICIAL_DOMAINS:
        result["official"] = OFFICIAL_DOMAINS[reg]
        trust.append({"id": "official_domain", "weight": 0.45, "evidence": [reg],
                      "en": f"Official domain of {OFFICIAL_DOMAINS[reg]}",
                      "ar": f"النطاق الرسمي لجهة {OFFICIAL_DOMAINS[reg]}", "source": "url"})
    elif tld == "gov.ae" or tld.endswith("gov.ae"):
        trust.append({"id": "gov_tld", "weight": 0.35, "evidence": [reg],
                      "en": "UAE government domain (.gov.ae)",
                      "ar": "نطاق حكومي إماراتي (.gov.ae)", "source": "url"})

    # --- Google Maps
    if host in GOOGLE_MAPS_HOSTS and ("maps" in host or p.path.startswith("/maps")) \
            or (reg == "google.com" and p.path.startswith("/maps")):
        result["is_maps"] = True

    # --- Open redirect inside a trusted domain (google.com/url?q=evil)
    qs = parse_qs(p.query)
    for key in ("q", "url", "u", "redirect", "redirect_uri", "next", "dest", "continue"):
        for val in qs.get(key, []):
            val = unquote(val)
            if re.match(r"https?://", val):
                inner = analyze_url(val)
                if not inner["official"]:
                    flags.append(_flag("redirect", 0.35,
                                       "Redirects to another (untrusted) site hidden in the link",
                                       "يُعيد التوجيه إلى موقع آخر غير موثوق مخفي داخل الرابط",
                                       [inner["host"]]))
                    flags.extend(inner["flags"])
                    # the trusted wrapper (e.g. google.com) must not lend its trust
                    trust.clear()
                    result["official"] = None
                break

    # --- Brand impersonation: brand keyword appears but domain is not official
    if not result["official"]:
        haystack = (host + p.path).replace("-", "").replace(".", "")
        for kw, official in BRAND_KEYWORDS.items():
            if len(kw) <= 5:
                # short keywords (icp, moi, noon, adcb): require them as a distinct token
                if not re.search(r"(^|[.\-/_])" + kw + r"($|[.\-/_])", host + p.path):
                    continue
            elif kw not in haystack:
                continue
            flags.append(_flag("brand_impersonation", 0.65,
                               f"Uses the name '{kw}' but is NOT the official site ({official})",
                               f"يستخدم اسم '{kw}' لكنه ليس الموقع الرسمي ({official})",
                               [host], category="impersonation"))
            break

        # --- Typosquatting against official labels (adcb -> adbc, emiratesnbd -> emiratesnb0)
        norm_label = label.translate(_HOMOGLYPHS).replace("rn", "m").replace("-", "")
        for off in OFFICIAL_DOMAINS:
            off_label = off.split(".")[0]
            if len(off_label) < 4 or off_label == label:
                continue
            d = levenshtein(norm_label, off_label)
            if (d == 0 and norm_label != label) or (0 < d <= (1 if len(off_label) < 7 else 2)):
                flags.append(_flag("typosquat", 0.55,
                                   f"Domain looks like a misspelling of {off} ({OFFICIAL_DOMAINS[off]})",
                                   f"النطاق يشبه تهجئة خاطئة لـ {off} ({OFFICIAL_DOMAINS[off]})",
                                   [reg, off], category="impersonation"))
                break

    # --- Phishing words inside the domain name itself (adcb-secure-update.com)
    if not result["official"] and not is_ip:
        dom_words = set(re.split(r"[.\-]+", sub + "." + label)) & SUSPICIOUS_PATH_WORDS
        if dom_words:
            flags.append(_flag("domain_words", 0.15,
                               "Domain name contains words like: " + ", ".join(sorted(dom_words)),
                               "اسم النطاق يحتوي على كلمات مثل: " + "، ".join(sorted(dom_words)),
                               sorted(dom_words)))

    # --- Structural signals
    if host.startswith("xn--") or ".xn--" in host:
        flags.append(_flag("punycode", 0.35, "Internationalised (punycode) domain - may hide look-alike letters",
                           "نطاق بترميز Punycode - قد يخفي حروفاً مشابهة", [host]))
    if tld.split(".")[-1] in SUSPICIOUS_TLDS:
        flags.append(_flag("cheap_tld", 0.20, f"Low-cost domain extension often abused (.{tld})",
                           f"امتداد نطاق رخيص يكثر استغلاله (.{tld})", [tld]))
    if reg in URL_SHORTENERS or host in URL_SHORTENERS:
        flags.append(_flag("shortener", 0.25, "Shortened link hides the real destination",
                           "رابط مختصر يُخفي الوجهة الحقيقية", [host]))
    if result["is_maps"]:
        # The map itself is Google's, but that says nothing about the listing's
        # phone number / website - so Google's trust must not lower the risk.
        trust.clear()
        result["official"] = None
    if reg == "goo.gl" and not result["is_maps"]:
        flags.append(_flag("shortener", 0.15, "Google short link - destination hidden",
                           "رابط Google مختصر - الوجهة مخفية", [host]))
    if not result["official"]:
        if label.count("-") >= 2:
            flags.append(_flag("hyphens", 0.15, "Many hyphens in the domain name",
                               "عدد كبير من الشرطات في اسم النطاق", [reg]))
        if len(re.findall(r"\d", label)) >= 3:
            flags.append(_flag("digits", 0.10, "Many digits in the domain name",
                               "أرقام كثيرة في اسم النطاق", [reg]))
        if sub.count(".") >= 2:
            flags.append(_flag("deep_sub", 0.15, "Unusually deep sub-domains",
                               "نطاقات فرعية متعددة بشكل غير معتاد", [host]))
        if scheme_given and p.scheme == "http":
            flags.append(_flag("no_https", 0.15, "Not using a secure connection (HTTPS)",
                               "لا يستخدم اتصالاً آمناً (HTTPS)", []))
    if "@" in p.netloc:
        flags.append(_flag("at_sign", 0.40, "Contains '@' - the real site is after the @",
                           "يحتوي على '@' - الموقع الحقيقي بعد العلامة", [p.netloc]))
    if p.port and p.port not in (80, 443):
        flags.append(_flag("port", 0.15, f"Non-standard port {p.port}", f"منفذ غير معتاد {p.port}"))
    if len(url) > 100:
        flags.append(_flag("long_url", 0.08, "Very long URL", "رابط طويل جداً"))
    path_words = set(re.split(r"[/\-_.?=&]+", (p.path + "?" + p.query).lower()))
    hits = sorted(path_words & SUSPICIOUS_PATH_WORDS)
    if hits and not result["official"]:
        flags.append(_flag("path_words", min(0.08 * len(hits), 0.25),
                           "Link contains phishing-style words: " + ", ".join(hits[:4]),
                           "الرابط يحتوي على كلمات تصيّد: " + "، ".join(hits[:4]), hits[:4]))
    if p.path.lower().endswith(DANGEROUS_EXTENSIONS):
        flags.append(_flag("download", 0.40, "Link downloads an app/file directly (e.g. APK)",
                           "الرابط يقوم بتنزيل تطبيق أو ملف مباشرة (مثل APK)", [p.path[-20:]]))
    return result
