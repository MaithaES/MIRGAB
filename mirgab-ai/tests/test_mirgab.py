import csv
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["MIRGAB_DB"] = os.path.join(ROOT, "data", "test.db")

from mirgab import analyze  # noqa: E402
from mirgab.text import normalize, extract_urls  # noqa: E402
from mirgab.url_analyzer import analyze_url, split_host  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _clean_db():
    yield
    if os.path.exists(os.environ["MIRGAB_DB"]):
        os.remove(os.environ["MIRGAB_DB"])


# ---------------- helpers ----------------
def test_arabic_normalisation():
    assert normalize("أَرباح مضمونة") == "ارباح مضمونه"
    assert normalize("١٢٣") == "123"


def test_split_host_gov_ae():
    assert split_host("www.adpolice.gov.ae") == ("www", "adpolice.gov.ae", "gov.ae")


def test_extract_urls():
    assert extract_urls("ادفع الآن https://uae-fines-pay.xyz/pay، شكرا") == ["https://uae-fines-pay.xyz/pay"]


# ---------------- URL engine ----------------
@pytest.mark.parametrize("url", [
    "https://www.adcb.com", "https://adpolice.gov.ae", "https://www.noon.com/uae-en/",
    "https://u.ae/en", "https://afternoon-tea.ae",
])
def test_official_or_benign_urls_are_low_risk(url):
    assert analyze(url=url, log=False)["score"] < 25


@pytest.mark.parametrize("url", [
    "https://adcb-secure-update.com/login/verify",
    "https://emiratesnbd.com.verify-account.xyz/login",
    "http://192.168.4.4/emiratesnbd/otp",
    "https://www.google.com/url?q=https://tamm-services.online/pay-fine",
])
def test_phishing_urls_are_critical(url):
    assert analyze(url=url, log=False)["score"] >= 75


def test_typosquat_detected():
    ids = [f["id"] for f in analyze_url("https://adcbb.com")["flags"]]
    assert "typosquat" in ids


def test_google_redirect_loses_trust():
    r = analyze_url("https://www.google.com/url?q=https://evil.top/x")
    assert r["official"] is None and any(f["id"] == "redirect" for f in r["flags"])


# ---------------- Content engine (all six domains) ----------------
@pytest.mark.parametrize("text,cat", [
    ("فيلا في جزيرة الريم 1000 درهم شهري، المالك خارج الدولة، حول العربون ونرسل لك المفاتيح", "real_estate"),
    ("Buy Xanax without prescription, discreet delivery", "pharma"),
    ("iPhone 90% off, bank transfer only, no cash on delivery, no refunds", "fake_store"),
    ("Guaranteed returns 30% weekly, invite friends referral bonus, minimum deposit 500", "investment"),
    ("شرطة أبوظبي: لديك مخالفة مرورية، سدد المخالفة خلال 24 ساعة عبر الرابط", "impersonation"),
])
def test_domains(text, cat):
    r = analyze(text=text, log=False)
    assert r["score"] >= 50
    assert r["category"]["key"] == cat


def test_pharma_has_health_impact():
    r = analyze(text="متوفر ترامادول بدون وصفة طبية، توصيل سري", log=False)
    assert r["impact"]["health"] > r["impact"]["social"]


def test_maps_scenario():
    r = analyze(text="Got the bank customer service number from Google Maps, they asked for my OTP",
                url="https://maps.app.goo.gl/abc", log=False)
    assert r["score"] >= 50
    assert any(d["key"] == "maps" for d in r["domains"])


def test_safe_bank_message():
    r = analyze(text="ADCB: we will never ask for your OTP. Never share your OTP with anyone.",
                url="https://www.adcb.com", log=False)
    assert r["score"] < 25 and r["category"]["key"] == "legit"


def test_explanations_present():
    r = analyze(text="Double your money with guaranteed profit, daily profit in USDT", log=False)
    assert r["reasons"] and r["ml"]["top_fraud_terms"]
    assert all("ar" in x and "en" in x for x in r["reasons"])


def test_realistic_set_accuracy():
    with open(os.path.join(ROOT, "data", "realistic_test.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    correct = sum((analyze(text=r["text"], log=False)["score"] >= 50) == (r["label"] != "legit") for r in rows)
    assert correct / len(rows) >= 0.85


# ---------------- API ----------------
def test_api_and_community_reports():
    from app import app
    c = app.test_client()
    r = c.post("/api/analyze", json={"url": "https://totally-new-shop.ae"})
    before = r.get_json()["score"]
    c.post("/api/report", json={"url": "https://totally-new-shop.ae", "category": "fake_store"})
    after = c.post("/api/analyze", json={"url": "https://totally-new-shop.ae"}).get_json()["score"]
    assert after >= 85 > before
    assert c.post("/api/report", json={"url": "https://adcb.com"}).status_code == 400
    assert c.get("/api/stats").get_json()["reports"] >= 1
    assert c.post("/api/analyze", json={}).status_code == 400
