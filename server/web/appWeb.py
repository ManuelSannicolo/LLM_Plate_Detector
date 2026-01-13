# server/web/appWeb.py
try:
    from flask import (
        Flask, render_template, request, redirect, url_for, flash
    )
    from flask_login import LoginManager, login_required, current_user
    from server.database import DatabaseManager
    import server.config as config
    from server.connection.frame_receiver import receiver as frame_receiver_blueprint
except ImportError as e:
    print(f"Errore nel caricamento dei moduli in appWeb.py: {e}")

app = Flask(__name__)
app.register_blueprint(frame_receiver_blueprint)

app.secret_key = config.SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_PERMANENT"] = False

# Database
db = DatabaseManager(config.DATABASE_PATH)

# Login manager
login_manager = LoginManager()
login_manager.login_view = "login_page"
login_manager.init_app(app)

# ============================================================================

@app.route("/")
@login_required
def index():
    stats = {
        "total_plates": len(db.get_all_plates()),
        "recent_logs": db.get_access_history(limit=10),
    }
    return render_template("index.html", stats=stats)

# ================== Plates CRUD ==================
@app.route("/plates")
@login_required
def plates():
    plates = db.get_all_plates()
    return render_template("plates.html", plates=plates)

@app.route("/add_plate", methods=["GET", "POST"])
@login_required
def add_plate():
    if request.method == "POST":
        plate = request.form["plate_number"].strip().upper()
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        role = request.form["role"]
        expiration = request.form["expiration_date"]

        if not plate or len(plate) < 6:
            flash("Numero targa non valido!", "danger")
            return render_template("add_plate.html")

        try:
            result = db.add_authorized_plate(
                plate, first_name, last_name, role, expiration
            )
            if result:
                flash(f"Targa {plate} aggiunta con successo!", "success")
            else:
                flash(f"Targa {plate} già esistente!", "warning")
            return redirect(url_for("plates"))
        except Exception as e:
            flash(f"Errore: {str(e)}", "danger")
            return render_template("add_plate.html")

    return render_template("add_plate.html")

@app.route("/edit_plate/<plate_number>", methods=["GET", "POST"])
@login_required
def edit_plate(plate_number):
    plate = db.get_plate(plate_number)
    if not plate:
        flash("Targa non trovata!", "danger")
        return redirect(url_for("plates"))

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        role = request.form["role"]
        expiration = request.form["expiration_date"]
        try:
            db.update_plate(plate_number, first_name, last_name, role, expiration)
            flash("Targa aggiornata con successo!", "success")
            return redirect(url_for("plates"))
        except Exception as e:
            flash(f"Errore: {str(e)}", "danger")

    return render_template("edit_plate.html", plate=plate)

@app.route("/delete_plate/<plate_number>", methods=["POST"])
@login_required
def delete_plate(plate_number):
    try:
        db.remove_plate(plate_number)
        flash(f"Targa {plate_number} rimossa!", "warning")
    except Exception as e:
        flash(f"Errore: {str(e)}", "danger")
    return redirect(url_for("plates"))

# ================== Logs ==================
@app.route("/logs")
@login_required
def logs():
    plate_number = request.args.get("plate_number", "").strip().upper()
    status = request.args.get("status", "")
    all_logs = db.get_access_history(limit=200)

    if plate_number:
        all_logs = [log for log in all_logs if plate_number in log["plate_number"]]
    if status:
        all_logs = [log for log in all_logs if log["status"] == status]

    return render_template("logs.html", logs=all_logs)

@app.route("/logs/export")
@login_required
def export_logs():
    from datetime import datetime
    from flask import send_file
    import tempfile
    import os

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"access_logs_{timestamp}.csv"
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)

    if db.export_logs_to_csv(filepath):
        return send_file(filepath, mimetype="text/csv", as_attachment=True, download_name=filename)
    else:
        flash("Nessun log da esportare", "warning")
        return redirect(url_for("logs"))

@app.route("/logs/clear", methods=["POST"])
@login_required
def clear_logs():
    try:
        if db.clear_access_log():
            flash("Tutti i log sono stati eliminati con successo", "success")
        else:
            flash("Errore durante l'eliminazione dei log", "danger")
    except Exception as e:
        flash(f"Errore: {str(e)}", "danger")
    return redirect(url_for("logs"))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
