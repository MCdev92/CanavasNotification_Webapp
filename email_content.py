import os
import smtplib
import requests
import datetime
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pytz import timezone, utc

# Load environment variables from .env file
load_dotenv()

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL')

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

def get_weekly_assignments(Canvas_URL, Access_Token, local_tz):
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
