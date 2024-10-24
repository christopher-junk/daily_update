from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os 

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

wd = 'C:/Users/chris/Documents/daily_update'

os.chdir(wd)

# Email logistic details
sender_email = "christopher.junk24@gmail.com"
password = "lbid aqvf cdqn tmzc"  # Use an App Password if 2FA is enabled

def fail_email(body):
    """Send an email notification."""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "clh3071@gmail.com"
    msg['Subject'] = 'Failed Daily Update'
    msg.attach(MIMEText(body, 'html'))

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)  # Use App Password
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

def execute_script():
    # Execute the daily_update.py script
    try:
        # Call the daily_update.py script
        subprocess.run(['python', 'daily_update.py'], check=True)  # Use 'python3' if needed
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing daily_update.py: {e}")
        body = f"""
        <html>
        <body>
            <h2>Daily Update Failed</h2>
            <p>Error: {e}</p>
        </body>
        </html>
        """
        fail_email(body)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('daily_email',
          default_args=default_args,
          description="Daily update email sent to describe job search and tomorrow's scheduled events",
          schedule_interval='0 17 * * *')

# Define the task to execute the script
email_task = PythonOperator(
    task_id='daily_update_email',
    python_callable=execute_script,
    dag=dag
)