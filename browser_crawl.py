"""Browser-style page crawl against running server — checks every route for runtime errors."""

import re
import requests
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:5007"
session = requests.Session()

PAGES = [
    "/", "/about", "/privacy", "/terms", "/contact",
    "/login", "/register", "/downloads",
    "/dashboard", "/typing", "/hindi", "/history",
    "/leaderboard", "/profile", "/mock-test", "/result", "/custom/",
    "/admin/", "/admin/users", "/admin/results",
    "/admin/paragraphs/english", "/admin/paragraphs/hindi",
    "/admin/downloads", "/admin/settings",
]

# Login with CSRF
login_page = session.get(f"{BASE}/login")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf = soup.find("input", {"name": "csrf_token"})
token = csrf["value"] if csrf else ""
resp = session.post(
    f"{BASE}/login",
    data={"email": "qaadmin", "password": "test1234", "csrf_token": token, "submit": "Login"},
    allow_redirects=True,
)
logged_in = "dashboard" in resp.url or "Dashboard" in resp.text
print(f"Login: {resp.status_code} -> {resp.url} (logged_in={logged_in})")

errors = []
ok = 0
for path in PAGES:
    try:
        r = session.get(f"{BASE}{path}", timeout=10)
        body = r.text
        bad = (
            r.status_code >= 500
            or "Traceback" in body
            or "Internal Server Error" in body
        )
        if bad:
            errors.append((path, r.status_code, body[:300]))
            print(f"FAIL  {path}  [{r.status_code}]")
        else:
            ok += 1
            print(f"OK    {path}  [{r.status_code}]")
    except Exception as exc:
        errors.append((path, "EXC", str(exc)))
        print(f"EXC   {path}  {exc}")

if logged_in:
    r = session.get(f"{BASE}/result")
    m = re.search(r'href="(/certificate/\d+)"', r.text)
    if not m:
        # fetch latest result id via history
        with session.get(f"{BASE}/history") as hr:
            m = re.search(r"certificate/(\d+)", hr.text)
    if m:
        cert_path = m.group(1) if m.group(1).startswith("/") else f"/certificate/{m.group(1)}"
        if not cert_path.startswith("/"):
            cert_path = "/" + cert_path
        cid = re.search(r"(\d+)", cert_path).group(1)
        for p in [f"/certificate/{cid}", f"/certificate/download/{cid}"]:
            r = session.get(f"{BASE}{p}")
            if r.status_code == 200:
                ok += 1
                print(f"OK    {p}  [{r.status_code}]")
            else:
                errors.append((p, r.status_code, ""))
                print(f"FAIL  {p}  [{r.status_code}]")

        r = session.get(f"{BASE}/certificate/{cid}")
        m2 = re.search(r"TMI-\d{8}-\d{6}", r.text)
        if m2:
            vid = m2.group(0)
            r = session.get(f"{BASE}/verify/{vid}")
            if r.status_code == 200 and "QA Admin" in r.text:
                ok += 1
                print(f"OK    /verify/{vid}  [{r.status_code}]")
            else:
                print(f"FAIL  verify/{vid}")
    else:
        print("WARN  No certificate link found on result page")

print(f"\nCrawl: {ok} OK, {len(errors)} errors")
for e in errors:
    print(" ", e)
