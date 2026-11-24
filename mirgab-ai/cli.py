"""Command-line interface.

    python cli.py "https://adcb-secure-update.com/login"
    python cli.py --text "فيلا للإيجار 1000 درهم شهري، المالك خارج الدولة، حول العربون"
    python cli.py --lang ar --json "..."
"""
import argparse
import json

from mirgab import analyze

BAR = {"safe": "🟢", "caution": "🟡", "suspicious": "🟠", "critical": "🔴"}


def main():
    ap = argparse.ArgumentParser(description="Mirgab AI | مِرقاب - check a link or message before you click")
    ap.add_argument("input", nargs="?", default="", help="URL or message text")
    ap.add_argument("--text", default="", help="Ad / message text")
    ap.add_argument("--url", default="", help="URL to check")
    ap.add_argument("--lang", choices=["en", "ar"], default="en")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = analyze(text=a.text or a.input, url=a.url, log=False)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    L = a.lang
    print(f"\n{BAR[r['level']]}  {r['score']}/100  {r['level_label'][L]}  —  {r['category'][L]}")
    if r["official_entity"]:
        print(f"   ✔ {r['official_entity']}")
    print("\n" + ("Why:" if L == "en" else "الأسباب:"))
    for x in r["reasons"][:8]:
        print(f"   • {x[L]}  (+{int(x['weight'] * 100)})")
    for x in r["trust_signals"]:
        print(f"   ✓ {x[L]}  (-{int(x['weight'] * 100)})")
    if r["ml"] and r["ml"]["top_fraud_terms"]:
        terms = ", ".join(t["term"] for t in r["ml"]["top_fraud_terms"])
        print(("   AI key words: " if L == "en" else "   كلمات رصدها الذكاء الاصطناعي: ") + terms)
    print("\n" + ("Impact:" if L == "en" else "الأثر:"), r["impact"])
    print("\n" + ("Advice:" if L == "en" else "النصائح:"))
    for x in r["advice"][L]:
        print("   → " + x)
    if r["report_channels"]:
        print("\n" + ("Report:" if L == "en" else "للإبلاغ:"))
        for x in r["report_channels"][L]:
            print("   ☎ " + x)
    print()


if __name__ == "__main__":
    main()
