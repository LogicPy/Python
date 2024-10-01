# app.py
import os
import requests
import json
import imaplib
import email
from email.header import decode_header
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from dotenv import load_dotenv
from tabulate import tabulate
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import logging
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Load environment variables from .env
load_dotenv()

# Enable OAuthlib to use insecure transport (Development Only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove or set to '0' in production

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"),
        logging.StreamHandler()
    ]
)

# Constants
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
NVD_API_KEY = os.getenv('NVD_API_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if not all([GROQ_API_KEY, NVD_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
    logging.error("One or more environment variables are missing. Please check your .env file.")
    exit(1)

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# OAuth 2.0 setup
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'email'
]

def get_gmail_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri=url_for('oauth2callback', _external=True)
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return redirect(auth_url)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Function to send email content to Groq's API for phishing detection
def get_groq_response(message):
    instruction = """
    You are an AI assistant specialized in detecting phishing attempts in email content. 
    Analyze the following email and determine whether it is a phishing attempt. 
    Respond with 'Phishing' or 'Not Phishing' followed by a brief explanation of your reasoning.
    
    Email Content:
    """
    payload = {
        "messages": [
            {
                "role": "user",
                "content": instruction + message  # Combine instructions with the actual email content
            }
        ],
        "model": "llama3-8b-8192",  # Using the specified model
    }
    try:
        response = requests.post(
            groq_api_url,
            json=payload,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        logging.error(f"Groq API HTTP error: {e}")
        return f"Error: {str(e)}"
    except requests.exceptions.RequestException as e:
        logging.error(f"Groq API Request exception: {e}")
        return f"Error: {str(e)}"
    except KeyError as e:
        logging.error(f"Groq API response parsing error: {e}")
        return "Error parsing response."

@app.route('/')
def index():
    return render_template('index.html')  # Landing page

# OAuth2 callback route
@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    
    if not flow.credentials:
        return "Failed to authenticate.", 400
    
    # Save the credentials in the session
    creds = Credentials(
        token=flow.credentials.token,
        refresh_token=flow.credentials.refresh_token,
        token_uri=flow.credentials.token_uri,
        client_id=flow.credentials.client_id,
        client_secret=flow.credentials.client_secret,
        scopes=flow.credentials.scopes
    )
    session['credentials'] = creds_to_dict(creds)
    
    return redirect(url_for('index'))

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

# Route to handle phishing detection manually
@app.route('/detect-phishing', methods=['POST'])
def detect_phishing():
    email_content = request.form.get('email_content')
    
    if not email_content:
        return jsonify({'error': 'No email content provided.'}), 400
    
    # Send the email content to Groq for phishing detection
    ai_response = get_groq_response(email_content)
    
    # Expected AI Response Format:
    # "Phishing: [Explanation]"
    # or
    # "Not Phishing: [Explanation]"
    
    try:
        # Split the AI response into verdict and explanation
        verdict, explanation = ai_response.split(':', 1)
        verdict = verdict.strip().lower()
        explanation = explanation.strip()
        
        if verdict == 'phishing':
            result = 'This email appears to be a phishing attempt.'
        elif verdict == 'not phishing':
            result = 'This email seems safe.'
        else:
            result = 'Unable to determine the nature of this email.'
    
    except ValueError:
        # If the response doesn't contain a colon, handle it gracefully
        logging.error("Unexpected AI response format.")
        result = 'Unable to determine the nature of this email.'
        explanation = ai_response  # Include the raw AI response for debugging
    
    return jsonify({'result': result, 'confidence': 'High' if verdict in ['phishing', 'not phishing'] else 'Low', 'ai_response': explanation})

# Function to generate OAuth2 string for IMAP authentication
def generate_oauth2_string(username, access_token):
    auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
    return base64.b64encode(auth_string.encode()).decode()

# Route to initiate Gmail authentication
@app.route('/authorize')
def authorize():
    return get_gmail_credentials()

# Route to fetch latest emails and detect phishing
@app.route('/fetch-emails', methods=['POST'])
def fetch_emails():
    creds = None
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    
    creds_data = session['credentials']
    creds = Credentials(**creds_data)
    
    if not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            session['credentials'] = creds_to_dict(creds)
        else:
            return redirect(url_for('authorize'))
    
    try:
        # Retrieve the authenticated user's email address using the userinfo endpoint
        userinfo_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        headers = {'Authorization': f'Bearer {creds.token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        email_address = userinfo_response.json().get('email')
        if not email_address:
            logging.error("Failed to retrieve email address from userinfo.")
            return jsonify({'error': 'Failed to retrieve email address.'}), 400
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching userinfo: {e}")
        return jsonify({'error': 'Failed to retrieve user information.'}), 500

    # Generate OAuth2 string
    oauth2_string = generate_oauth2_string(email_address, creds.token)
    
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.authenticate('XOAUTH2', lambda x: oauth2_string)
        mail.select("inbox")  # Connect to inbox.
        
        # Search for all emails
        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            logging.error("Failed to retrieve emails.")
            return jsonify({'error': 'Failed to retrieve emails.'}), 500

        email_ids = messages[0].split()
        
        if not email_ids:
            logging.info("No emails found.")
            return jsonify({'phishing_results': []})
        
        # Fetch the latest 5 emails
        latest_email_ids = email_ids[-5:]
        phishing_results = []
        
        for eid in latest_email_ids:
            res, msg_data = mail.fetch(eid, '(RFC822)')
            if res != 'OK':
                logging.error(f"Failed to fetch email ID {eid.decode()}")
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    from_, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding if encoding else 'utf-8')
                    
                    # Get email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                charset = part.get_content_charset() or 'utf-8'
                                body = part.get_payload(decode=True).decode(charset, errors='replace')
                                break
                    else:
                        content_type = msg.get_content_type()
                        if content_type == "text/plain":
                            charset = msg.get_content_charset() or 'utf-8'
                            body = msg.get_payload(decode=True).decode(charset, errors='replace')
                    
                    if not body:
                        logging.info(f"Email ID {eid.decode()} has no plain text content.")
                        continue
                    
                    # Send email body to Groq for phishing detection
                    ai_response = get_groq_response(body)
                    
                    # Determine phishing based on AI response
                    try:
                        verdict, explanation = ai_response.split(':', 1)
                        verdict = verdict.strip().lower()
                        explanation = explanation.strip()
                        
                        if verdict == 'phishing':
                            result = 'Phishing Attempt Detected'
                        elif verdict == 'not phishing':
                            result = 'No Phishing Detected'
                        else:
                            result = 'Unable to determine the nature of this email.'
                    except ValueError:
                        # If the response doesn't contain a colon, handle it gracefully
                        logging.error("Unexpected AI response format.")
                        result = 'Unable to determine the nature of this email.'
                        explanation = ai_response  # Include the raw AI response for debugging
                    
                    phishing_results.append({
                        'Subject': subject,
                        'From': from_,
                        'Result': result,
                        'AI Response': explanation
                    })
        
        mail.logout()
        
        return jsonify({'phishing_results': phishing_results})
    
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {e}")
        return jsonify({'error': 'Failed to connect to Gmail. Ensure OAuth token is valid.'}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500

if __name__ == "__main__":
    app.run(port=5214, debug=True)
