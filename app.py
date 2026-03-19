from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from auth import get_auth_url, exchange_code_for_token, get_credentials
from scheduler import get_busy_times, find_free_slots

app = Flask(__name__)
app.secret_key = "secret_key"


# Home Page
@app.route("/")
def index():
    logged_in = "token" in session
    return render_template("index.html", logged_in=logged_in)


# Google Login
@app.route("/login")
def login():
    auth_url = get_auth_url()
    return redirect(auth_url)


# OAUTH Callback
@app.route("/oauth2callback")
def oauth2callback():
    code = request.args.get("code")
    token = exchange_code_for_token(code)
    session["token"] = token
    return redirect(url_for("index"))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Find Times
@app.route("/find-times", methods=["POST"])
def find_times():
    if "token" not in session:
        return redirect(url_for("login"))

    emails_raw = request.form.get("emails", "")
    duration = int(request.form.get("duration", 60))
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    emails = [e.strip() for e in emails_raw.split(",") if e.strip()]

    credentials = get_credentials(session["token"])

    busy_map = get_busy_times(credentials, emails, start_date, end_date)

    suggestions = find_free_slots(busy_map, duration, start_date, end_date)

    return render_template(
        "results.html",
        suggestions=suggestions,
        duration=duration,
        emails=emails,
    )


# Schedule event
@app.route("/schedule-event", methods=["POST"])
def schedule_event():
    if "token" not in session:
        return redirect(url_for("login"))

    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    emails = json.loads(request.form.get("emails", "[]"))

    credentials = get_credentials(session["token"])

    from googleapiclient.discovery import build
    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": "Group Meeting",
        "start":   {"dateTime": start_time, "timeZone": "America/Los_Angeles"},
        "end":     {"dateTime": end_time,   "timeZone": "America/Los_Angeles"},
        "attendees": [{"email": e} for e in emails],
    }

    service.events().insert(calendarId="primary", body=event, sendUpdates="all").execute()

    return render_template("scheduled.html", start_time=start_time, emails=emails)


if __name__ == "__main__":
    app.run(debug=True)