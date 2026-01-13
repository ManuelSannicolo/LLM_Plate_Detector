# server/web/appWeb.py
try:
    from flask import Flask, render_template
    from server.database import DatabaseManager
    import server.config as config
    from server.connection.frame_receiver import receiver as frame_receiver_blueprint
except ImportError as e:
    print(f"Errore nel caricamento dei moduli in appWeb.py: {e}")

app = Flask(__name__)
app.register_blueprint(frame_receiver_blueprint)

app.secret_key = config.SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = False  # False per debug
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_PERMANENT"] = False

# Database
db = DatabaseManager(config.DATABASE_PATH)

# Debug route registrate
if config.VERBOSE:
    print("\n=== ROUTE REGISTRATE ===")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.endpoint}: {rule.rule} {list(rule.methods)}")
    print("========================\n")

# Placeholder home route
@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
