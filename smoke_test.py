from datetime import datetime

from app import app
from models import db
from models.user import User
from models.result import Result
from werkzeug.security import generate_password_hash

ROUTES = [
    "/",
    "/dashboard",
    "/typing",
    "/hindi",
    "/history",
    "/leaderboard",
    "/profile",
    "/admin",
    "/admin/users",
    "/admin/results",
    "/admin/settings",
    "/admin/paragraphs/english",
    "/admin/paragraphs/hindi",
]

with app.app_context():
    db.create_all()
    user = User.query.filter_by(username="smokeadmin").first()
    if not user:
        user = User(
            full_name="Smoke Admin",
            username="smokeadmin",
            email="smoke@test.com",
            mobile="9999999999",
            password=generate_password_hash("test1234"),
            is_admin=True,
        )
        db.session.add(user)
        db.session.commit()
        r = Result(
            user_id=user.id,
            language="English",
            difficulty="Easy",
            duration=60,
            gross_wpm=40,
            net_wpm=38,
            cpm=200,
            accuracy=97.5,
            errors=3,
            created_at=datetime.utcnow(),
        )
        db.session.add(r)
        db.session.commit()
    uid = user.id

client = app.test_client()
with client.session_transaction() as sess:
    sess["_user_id"] = str(uid)
    sess["_fresh"] = True

for route in ROUTES:
    try:
        resp = client.get(route, follow_redirects=False)
        print(f"{resp.status_code}  {route}")
        if resp.status_code >= 400:
            body = resp.get_data(as_text=True)
            print("   >>> ERROR BODY:", body[:500].replace("\n", " "))
    except Exception as e:
        print(f"EXC  {route}: {type(e).__name__}: {e}")
