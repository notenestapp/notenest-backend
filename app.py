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
from routes.phrase import bp as phrase_bp
from routes.exam_score import bp as exam_bp
from routes.video_watch import bp as video_bp
from routes.read_time import bp as read_bp
from routes.push import bp as push_bp

from utils.error import register_error_handlers
from utils.limiter import limiter



app = Flask(__name__, template_folder="screens")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

CORS(app)
register_error_handlers(app)

# Initialize limiter AFTER creating app
limiter.init_app(app)



# Register blueprints
app.register_blueprint(note_bp)
app.register_blueprint(users_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(chapters_bp)
app.register_blueprint(quotes_bp)
app.register_blueprint(plan_bp)
app.register_blueprint(subs_bp)
app.register_blueprint(files_bp)
app.register_blueprint(phrase_bp)
app.register_blueprint(video_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(read_bp)
app.register_blueprint(push_bp)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return render_template("landing.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
