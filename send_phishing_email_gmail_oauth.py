from googleapiclient.discovery import build
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

# Load credentials from token.pkl
with open('token.pkl', 'rb') as token:
    creds = pickle.load(token)

# Create Gmail API service
service = build('gmail', 'v1', credentials=creds)

# Create the email
message = MIMEMultipart()
message['to'] = 'sampletesla98789@gmail.com'        # Replace with recipient email
message['subject'] = 'Phishing Simulation Test'    # Subject of your simulation

# Email body
html = """
<html>
  <body>
    <p>Hello,</p>
    <p>We detected unusual activity on your account. Please <a href="http://localhost:5000/track_click?user=sampletesla98789@gmail.com">verify your identity</a>.</p>
    <p>Thank you,</p>
    <p>Security Team</p>
  </body>
</html>
"""


message.attach(MIMEText(body, 'plain'))

# Encode message
raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
create_message = {'raw': raw_message}

# Send the email
send_message = (service.users().messages().send(userId="me", body=create_message).execute())

print(f"✅ Email sent successfully! Message Id: {send_message['id']}")
