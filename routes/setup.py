from flask import Blueprint, render_template, request, redirect, url_for, session

setup = Blueprint("setup", __name__)


@setup.route("/typing-setup", methods=["GET", "POST"])
def typing_setup():

    if request.method == "POST":

        session["typing_settings"] = {
            "candidate": request.form.get("candidate"),
            "language": request.form.get("language", "english"),
            "keyboard": request.form.get("keyboard", "inscript"),
            "duration": int(request.form.get("duration", 60)),
            "difficulty": request.form.get("difficulty", "easy"),
            "paragraph": request.form.get("paragraph", "random")
        }

        return redirect(url_for("dashboard.typing_page"))

    return render_template("pages/typing_setup.html")