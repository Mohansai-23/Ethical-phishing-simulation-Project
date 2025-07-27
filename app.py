from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
from generate_pixel import generate_pixel  # You already created this

app = Flask(__name__)

# 👋 Home Page
@app.route("/")
def home():
    return "<h2>Welcome to the Ethical Phishing Simulation Platform</h2>"

# 📧 Test Phishing Email
@app.route("/test_email")
def test_email():
    return render_template("phishing_email.html")

# ✅ Track Link Clicks
@app.route("/track_click")
def track_click():
    email = request.args.get('email', 'unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('phishing.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clicks (email, timestamp) VALUES (?, ?)", (email, timestamp))
    conn.commit()
    conn.close()

    # ✅ Redirect to safety tips page after click
    return redirect("/safety_tips")

# 📊 Dashboard to Show Clicks + Opens + Summary Analytics
@app.route("/dashboard")
def dashboard():
    filter_type = request.args.get("type", "all")  # "clicks", "opens", or "all"

    conn = sqlite3.connect('phishing.db')
    cursor = conn.cursor()

    if filter_type == "clicks":
        cursor.execute("SELECT email, timestamp FROM clicks ORDER BY timestamp DESC")
        click_data = cursor.fetchall()
        open_data = []
    elif filter_type == "opens":
        cursor.execute("SELECT email, timestamp FROM opens ORDER BY timestamp DESC")
        open_data = cursor.fetchall()
        click_data = []
    else:
        cursor.execute("SELECT email, timestamp FROM clicks ORDER BY timestamp DESC")
        click_data = cursor.fetchall()
        cursor.execute("SELECT email, timestamp FROM opens ORDER BY timestamp DESC")
        open_data = cursor.fetchall()

    # 📈 Calculate analytics
    all_emails = set([email for email, _ in click_data] + [email for email, _ in open_data])
    total_emails_sent = len(all_emails)
    total_opens = len(set(email for email, _ in open_data))
    total_clicks = len(set(email for email, _ in click_data))

    open_rate = round((total_opens / total_emails_sent) * 100, 2) if total_emails_sent else 0
    success_rate = round((total_clicks / total_emails_sent) * 100, 2) if total_emails_sent else 0

    conn.close()
    return render_template(
        "dashboard.html",
        click_data=click_data,
        open_data=open_data,
        filter_type=filter_type,
        total_emails_sent=total_emails_sent,
        total_opens=total_opens,
        total_clicks=total_clicks,
        open_rate=open_rate,
        success_rate=success_rate
    )

# 🟢 Track Email Open (used by all 3 routes below)
@app.route("/email_opened")
def email_opened():
    email = request.args.get('email', 'unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('phishing.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO opens (email, timestamp) VALUES (?, ?)", (email, timestamp))
    conn.commit()
    conn.close()

    return send_file("static/pixel.png", mimetype="image/png")

@app.route("/track_open")
def track_open():
    email = request.args.get('email', 'unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('phishing.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO opens (email, timestamp) VALUES (?, ?)", (email, timestamp))
    conn.commit()
    conn.close()

    return app.send_static_file("pixel.png")

@app.route('/open_pixel')
def open_pixel():
    email = request.args.get('email', 'unknown')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('phishing.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO opens (email, timestamp) VALUES (?, ?)", (email, timestamp))
    conn.commit()
    conn.close()

    return generate_pixel()

# 🧠 Post-click education page
@app.route("/safety_tips")
def safety_tips():
    return render_template("safety_tips.html")

# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
