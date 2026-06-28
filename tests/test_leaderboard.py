"""Leaderboard query tests — run: python tests/test_leaderboard.py"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)


def test_leaderboard_one_row_per_user():
    from app import app, init_db
    from models import db
    from models.user import User
    from models.result import Result
    from werkzeug.security import generate_password_hash

    with app.app_context():
        init_db()

        def ensure_user(username, email):
            user = User.query.filter_by(username=username).first()
            if user:
                return user
            user = User(
                full_name=username.title(),
                username=username,
                email=email,
                mobile="9999999999",
                password=generate_password_hash("password123"),
            )
            db.session.add(user)
            db.session.commit()
            return user

        alice = ensure_user("lb_alice", "lb_alice@example.com")
        bob = ensure_user("lb_bob", "lb_bob@example.com")

        Result.query.filter(Result.user_id.in_([alice.id, bob.id])).delete(
            synchronize_session=False
        )
        db.session.commit()

        db.session.add_all([
            Result(user_id=alice.id, language="English", difficulty="Easy",
                   duration=60, net_wpm=40, accuracy=90.0, gross_wpm=42, cpm=200, errors=1),
            Result(user_id=alice.id, language="English", difficulty="Medium",
                   duration=60, net_wpm=55, accuracy=88.0, gross_wpm=58, cpm=250, errors=2),
            Result(user_id=alice.id, language="Hindi", difficulty="Easy",
                   duration=60, net_wpm=55, accuracy=95.0, gross_wpm=57, cpm=260, errors=1),
            Result(user_id=bob.id, language="English", difficulty="Easy",
                   duration=60, net_wpm=55, accuracy=92.0, gross_wpm=56, cpm=240, errors=1),
            Result(user_id=bob.id, language="English", difficulty="Hard",
                   duration=60, net_wpm=30, accuracy=99.0, gross_wpm=32, cpm=150, errors=0),
        ])
        db.session.commit()

        client = app.test_client()
        response = client.get("/leaderboard")
        assert response.status_code == 200

        html = response.get_data(as_text=True)
        assert "lb_alice" in html
        assert "lb_bob" in html
        from sqlalchemy import func, and_
        from models.user import User as UserModel

        best_wpm_subq = (
            db.session.query(
                Result.user_id.label("user_id"),
                func.max(Result.net_wpm).label("best_wpm"),
            )
            .group_by(Result.user_id)
            .subquery()
        )

        best_accuracy_subq = (
            db.session.query(
                Result.user_id.label("user_id"),
                func.max(Result.accuracy).label("best_accuracy"),
            )
            .join(
                best_wpm_subq,
                and_(
                    Result.user_id == best_wpm_subq.c.user_id,
                    Result.net_wpm == best_wpm_subq.c.best_wpm,
                ),
            )
            .group_by(Result.user_id)
            .subquery()
        )

        total_tests_subq = (
            db.session.query(
                Result.user_id.label("user_id"),
                func.count(Result.id).label("total_tests"),
            )
            .group_by(Result.user_id)
            .subquery()
        )

        rows = (
            db.session.query(
                UserModel.username,
                best_wpm_subq.c.best_wpm,
                best_accuracy_subq.c.best_accuracy.label("accuracy"),
                total_tests_subq.c.total_tests,
            )
            .join(best_wpm_subq, UserModel.id == best_wpm_subq.c.user_id)
            .join(best_accuracy_subq, UserModel.id == best_accuracy_subq.c.user_id)
            .join(total_tests_subq, UserModel.id == total_tests_subq.c.user_id)
            .order_by(
                best_wpm_subq.c.best_wpm.desc(),
                best_accuracy_subq.c.best_accuracy.desc(),
            )
            .all()
        )

        assert len(rows) >= 2
        usernames = [r.username for r in rows if r.username.startswith("lb_")]
        assert len(usernames) == len(set(usernames))

        alice_row = next(r for r in rows if r.username == "lb_alice")
        bob_row = next(r for r in rows if r.username == "lb_bob")

        assert alice_row.best_wpm == 55
        assert alice_row.accuracy == 95.0
        assert alice_row.total_tests == 3
        assert bob_row.best_wpm == 55
        assert bob_row.accuracy == 92.0
        assert bob_row.total_tests == 2

        lb_rows = [r for r in rows if r.username.startswith("lb_")]
        assert lb_rows[0].username == "lb_alice"
        assert lb_rows[1].username == "lb_bob"

    print("PASS leaderboard one row per user, best WPM, tie-break accuracy")


if __name__ == "__main__":
    test_leaderboard_one_row_per_user()
    print("\nLeaderboard tests passed.")
