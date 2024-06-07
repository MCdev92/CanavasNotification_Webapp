from flask import Flask, render_template, request, redirect, url_for, flash
from email_content import get_weekly_assignments, send_email, format_due_date
from pytz import timezone, utc
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# CSUEB-Canvas URL and Token
Canvas_URL = 'https://csueb.instructure.com/'
Access_Token = os.environ.get('Access_Token')

# Define the time zone for Canvas and your local time zone
canvas_tz = utc
local_tz = timezone('America/Los_Angeles')  # Change to your local time zone

@app.route('/')
def index():
    assignments = get_weekly_assignments(Canvas_URL, Access_Token, local_tz)
    return render_template("base.html", assignments=assignments)

@app.route('/notify', methods=['POST'])
def notify():
    try:
        # handle the notifications
        assignments = get_weekly_assignments(Canvas_URL, Access_Token, local_tz)
        if assignments:
            email_subject = "Upcoming Assignments Due This Week"
            email_body = """
            <html>
            <body>
            <h1>Upcoming Assignments Due This Week:</h1>
            <ul>
            """
            for assignment in assignments:
                email_body += f"""
                <li>
                    <strong>Course:</strong> {assignment['course']}<br>
                    <strong>Assignment:</strong> {assignment['name']}<br>
                    <strong>Due:</strong> {format_due_date(assignment['due_at'])}
                </li>
                <br><br>
                """
            email_body += """
            </ul>
            <p>Best regards,<br>Your Course Management System</p>
            <br>
            <footer>
            <small>Developed by Manuel Corporan</small>
            <br>
            <small>Copyright © 2024 Mcdev92. All rights reserved.</small>
            </footer>
            </body>
            </html>
            """    
            send_email(email_subject, email_body)
        else:
            send_email("No Assignments Due This Week", """
            <html>
            <body>
            <p>No assignments due this week.</p>
            <p>Best regards,<br>Your Course Management System</p>
            </body>
            </html>
            """)
    except Exception as e:
        print(f"Error notifying assignments: {str(e)}")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
