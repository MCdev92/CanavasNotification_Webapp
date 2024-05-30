from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import datetime
import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pytz import timezone, utc

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Load environment variables from .env file
load_dotenv()

# CSUEB-Canvas URL and Token
Canvas_URL = 'https://csueb.instructure.com/'
Access_Token = os.environ.get('Access_Token')

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

# Define the time zone for Canvas and your local time zone
canvas_tz = utc
local_tz = timezone('America/Los_Angeles')  # Change to your local time zone

def get_weekly_assignments():
    courses_url = f'{Canvas_URL}/api/v1/courses'
    headers = {'Authorization': f'Bearer {Access_Token}'}
    
    response = requests.get(courses_url, headers=headers)
    courses = response.json()

    due_assignments = []
    
    for course in courses:
        assignments_url = f'{Canvas_URL}/api/v1/courses/{course["id"]}/assignments'
        response = requests.get(assignments_url, headers=headers)
        assignments = response.json()
        
        for assignment in assignments:
            if "due_at" in assignment and assignment["due_at"]:
                due_date = datetime.datetime.strptime(assignment["due_at"], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc)
                due_date = due_date.astimezone(local_tz)  # convert to local time zone
                now = datetime.datetime.now(local_tz)
                one_week = datetime.timedelta(weeks=1)
                if now <= due_date <= now + one_week:
                    due_assignments.append({
                        'course': course['name'],
                        'name': assignment['name'],
                        'due_at': due_date
                    })
    return due_assignments

def format_due_date(due_date):
    return due_date.strftime('%A, %B %d, %Y at %I:%M %p')

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = "Canvas Daily Notification <" + EMAIL_USER + ">"
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
    server.quit()

@app.route('/')
def index():
    assignments = get_weekly_assignments()
    return render_template("base.html", assignments=assignments)

@app.route('/notify', methods=['POST'])
def notify():
    assignments = get_weekly_assignments()
    if assignments:
        email_subject = "Upcoming Assignments Due This Week"
        email_body = """
        <html>
        <body>
        <h1>Upcoming Assignments Due This Week:</h1>
        <ul>
        """
        for assignment in assignments:
            email_body += f"<li><strong>Course:</strong> {assignment['course']}</li><br><li><strong>Assignment:</strong> {assignment['name']}</li><br><li><strong>Due:</strong> {format_due_date(assignment['due_at'])}</li>"
        email_body += """
        </ul>
        <p>Best regards,<br>Your Course Management System</p>
        <br>
        <footer>
        <small>Developed by Manuel Corporan
        </small>
        <br>
        <small>Copyright © 2024 Mcdev92. All rights reserved.
        </footer>
        </body>
        </html>
        """    
        send_email(email_subject, email_body)
        flash('Notification sent successfully!', 'success')
    else:
        send_email("No Assignments Due This Week", """
        <html>
        <body>
        <p>No assignments due this week.</p>
        <p>Best regards,<br>Your Course Management System</p>
        </body>
        </html>
        """)
        flash('No assignments due this week!', 'info')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
