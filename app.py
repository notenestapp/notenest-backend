from flask import Flask, jsonify, render_template, request, g
import time
import threading
import psutil
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
from routes.credit_history import bp as credits_bp

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
app.register_blueprint(credits_bp)


# --- Metrics tracking -------------------------------------------------
# Record app start time and initial network counters
APP_START = time.time()
NET_INITIAL = psutil.net_io_counters()

# Thread-safe counters for request-level stats
_metrics_lock = threading.Lock()
_metrics = {"count": 0, "bytes_in": 0, "bytes_out": 0}


@app.before_request
def _track_before_request():
    # track incoming request size (may be None)
    size = request.content_length or 0
    g._req_size = size
    with _metrics_lock:
        _metrics["count"] += 1
        _metrics["bytes_in"] += size


@app.after_request
def _track_after_request(response):
    # track response size
    try:
        length = response.content_length
        if length is None:
            data = response.get_data()
            length = len(data) if data else 0
    except Exception:
        length = 0
    with _metrics_lock:
        _metrics["bytes_out"] += length
    return response


@app.get("/health")
def health():
    # uptime in seconds
    uptime = int(time.time() - APP_START)

    # routes count
    route_count = sum(1 for _ in app.url_map.iter_rules())

    # system network usage since app start (approximate)
    try:
        net_now = psutil.net_io_counters()
        net_sent = max(0, net_now.bytes_sent - NET_INITIAL.bytes_sent)
        net_recv = max(0, net_now.bytes_recv - NET_INITIAL.bytes_recv)
    except Exception:
        net_sent = net_recv = 0

    with _metrics_lock:
        req_count = _metrics["count"]
        bytes_in = _metrics["bytes_in"]
        bytes_out = _metrics["bytes_out"]

    # Render a simple status page with metrics
    return render_template(
        "health.html",
        uptime=uptime,
        route_count=route_count,
        requests=req_count,
        bytes_in=bytes_in,
        bytes_out=bytes_out,
        net_sent=net_sent,
        net_recv=net_recv,
    )


@app.get("/")
def home():
    return render_template("landing.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
