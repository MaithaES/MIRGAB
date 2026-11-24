"""Lightweight SQLite storage: anonymised scan log + community fraud reports.

Privacy by design: we never store the full text of a message, only the
domain, score and category, so the dashboard can show trends.
"""
import os
import sqlite3
import time
from contextlib import closing

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("MIRGAB_DB", os.path.join(BASE_DIR, "data", "mirgab.db"))


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS scans(
        id INTEGER PRIMARY KEY, ts REAL, input_type TEXT, domain TEXT,
        score INTEGER, level TEXT, category TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY, ts REAL, domain TEXT, category TEXT, note TEXT)""")
    return c


def log_scan(input_type, domain, score, level, category):
    with closing(_conn()) as c, c:
        c.execute("INSERT INTO scans(ts,input_type,domain,score,level,category) VALUES(?,?,?,?,?,?)",
                  (time.time(), input_type, domain or "", score, level, category))


def add_report(domain, category="", note=""):
    with closing(_conn()) as c, c:
        c.execute("INSERT INTO reports(ts,domain,category,note) VALUES(?,?,?,?)",
                  (time.time(), domain.lower(), category, (note or "")[:300]))


def report_count(domain):
    if not domain:
        return 0
    with closing(_conn()) as c:
        return c.execute("SELECT COUNT(*) FROM reports WHERE domain=?", (domain.lower(),)).fetchone()[0]


def stats():
    with closing(_conn()) as c:
        total = c.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        by_level = dict(c.execute("SELECT level, COUNT(*) FROM scans GROUP BY level").fetchall())
        by_cat = dict(c.execute("SELECT category, COUNT(*) FROM scans WHERE level IN ('suspicious','critical') GROUP BY category").fetchall())
        top_domains = c.execute("""SELECT domain, COUNT(*) n FROM reports GROUP BY domain
                                   ORDER BY n DESC LIMIT 10""").fetchall()
        risky = c.execute("""SELECT domain, MAX(score) s, COUNT(*) n FROM scans
                             WHERE domain!='' AND score>=50 GROUP BY domain ORDER BY s DESC, n DESC LIMIT 10""").fetchall()
        reports = c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    return {"total_scans": total, "by_level": by_level, "by_category": by_cat,
            "reports": reports, "top_reported": top_domains, "top_risky": risky}
