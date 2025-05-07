from flask import Flask, render_template, request, redirect, url_for
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# Simulated in-memory user database
users = []

# Prometheus metrics
REQUEST_COUNTER = Counter("flask_app_requests_total", "Total requests", ['method', 'endpoint'])
INPROGRESS_GAUGE = Gauge("flask_inprogress_requests", "Inprogress requests")
REQUEST_LATENCY_HIST = Histogram("flask_request_latency_seconds", "Request latency", ['endpoint'], buckets=[0.1, 0.5, 1, 2, 5])
REQUEST_SUMMARY = Summary("flask_request_summary_seconds", "Summary of request processing time", ['endpoint'])
USER_REGISTRATION_GAUGE = Gauge("registered_users_total", "Total registered users")


@app.before_request
def before_request():
    request.start_time = time.time()
    INPROGRESS_GAUGE.inc()


@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    REQUEST_COUNTER.labels(request.method, request.path).inc()
    REQUEST_LATENCY_HIST.labels(request.path).observe(duration)
    REQUEST_SUMMARY.labels(request.path).observe(duration)
    INPROGRESS_GAUGE.dec()
    return response


@app.route("/")
def index():
    return render_template("register.html", users=users)


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    if name and email:
        users.append({"name": name, "email": email})
        USER_REGISTRATION_GAUGE.set(len(users))
    return redirect(url_for("index"))


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
