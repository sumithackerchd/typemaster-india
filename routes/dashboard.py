from flask import Blueprint

dashboard = Blueprint("dashboard", __name__)

#dashboard route
    
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("pages/dashboard.html")