from flask import Blueprint, render_template
from flask_login import login_required

hindi = Blueprint("hindi", __name__)


@hindi.route("/hindi")
@login_required
def hindi_page():

    return render_template("pages/hindi.html")
