from flask import Flask, jsonify, render_template
from flask_cors import CORS
from routes.notes import bp as note_bp
from routes.users import bp as users_bp
from routes.chapters import bp as chapters_bp
from routes.quotes import bp as quotes_bp
from routes.payments import bp as payment_bp
from routes.plans import bp as plan_bp
from routes.subscriptions import bp as subs_bp
from routes.files import bp as files_bp

app = Flask(__name__, template_folder="screens")

CORS(app)


app.register_blueprint(note_bp)
app.register_blueprint(users_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(chapters_bp)
app.register_blueprint(quotes_bp)
app.register_blueprint(plan_bp)
app.register_blueprint(subs_bp)
app.register_blueprint(files_bp)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def home():
    return render_template("landing.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)