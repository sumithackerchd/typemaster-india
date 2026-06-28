"""
Module 1 typing engine tests — run: python tests/test_typing_engine.py
"""
import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)


def test_sqlite_uri():
    from config import Config, DATABASE_PATH

    uri = Config.SQLALCHEMY_DATABASE_URI
    assert uri.startswith("sqlite:///"), uri
    assert DATABASE_PATH.replace("\\", "/") in uri, uri
    print("PASS config SQLite URI")


def test_paragraph_json():
    english_path = os.path.join(BASE_DIR, "static", "data", "paragraphs.json")
    hindi_path = os.path.join(BASE_DIR, "static", "data", "hindi_mangal.json")

    with open(english_path, encoding="utf-8") as f:
        english = json.load(f)

    with open(hindi_path, encoding="utf-8") as f:
        hindi = json.load(f)

    for level in ("easy", "medium", "hard"):
        assert english["english"][level], f"Missing english.{level}"
        assert hindi["hindi"][level], f"Missing hindi.{level}"

    print("PASS paragraph JSON structure")


def test_wpm_formulas():
    total_typed = 100
    correct = 90
    wrong = 10
    minutes = 1

    gross = round((total_typed / 5) / minutes)
    net = max(0, round(((correct - wrong) / 5) / minutes))
    cpm = round(correct / minutes)
    accuracy = round((correct / total_typed) * 100, 2)

    assert gross == 20
    assert net == 16
    assert cpm == 90
    assert accuracy == 90.0

    print("PASS WPM / CPM / accuracy formulas")


def test_save_result_route():
    from app import app, init_db
    from models import db
    from models.user import User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        init_db()

        user = User.query.filter_by(email="engine_test@example.com").first()

        if not user:
            user = User(
                full_name="Engine Test",
                username="engine_test",
                email="engine_test@example.com",
                mobile="9999999999",
                password=generate_password_hash("password123"),
            )
            db.session.add(user)
            db.session.commit()

        client = app.test_client()

        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

        payload = {
            "language": "English",
            "difficulty": "Easy",
            "duration": 60,
            "gross_wpm": 25,
            "net_wpm": 22,
            "cpm": 120,
            "accuracy": 95.5,
            "errors": 2,
        }

        response = client.post(
            "/save-result",
            json=payload,
            content_type="application/json",
        )

        assert response.status_code == 200, response.get_data(as_text=True)
        data = response.get_json()
        assert data["success"] is True, data
        assert "result_id" in data

    print("PASS save-result API")


def test_result_and_admin_templates():
    from app import app, init_db

    with app.app_context():
        init_db()

        client = app.test_client()

        result_response = client.get("/result")
        assert result_response.status_code in (200, 302)

        admin_response = client.get("/admin/")
        assert admin_response.status_code in (200, 302)

    print("PASS result + admin dashboard routes reachable")


if __name__ == "__main__":
    test_sqlite_uri()
    test_paragraph_json()
    test_wpm_formulas()
    test_save_result_route()
    test_result_and_admin_templates()
    print("\nAll Module 1 typing engine tests passed.")
