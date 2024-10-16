# app.py
import os
import requests
import json
import imaplib
import email
from email.header import decode_header
from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging
import base64
import ssl
import celery
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask import Flask
from flask_cors import CORS
from flask import Flask
from flask_cors import CORS
from celery import Celery
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask import Flask
from flask_cors import CORS
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key
app = Flask(__name__, static_url_path='/static')

# Allow OAuthlib to use http for local testing (remove in production)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://localhost:5214/oauth2callback'

@app.route('/')
def index():
    return render_template('index.html')

# Allow CORS for specific origins
CORS(app, resources={
    r"/fetch-custom-emails": {"origins": "http://localhost:5214"}
})

CORS(app)


# Allow CORS for all routes and origins
CORS(app, resources={
    r"/fetch-custom-emails": {
        "origins": "http://localhost:5214",
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

from flask import Flask, session, redirect, url_for, request, render_template
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

app = Flask(__name__)
# Replace with your secret key

# Define the path to the client_secret.json file
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')

# OAuth 2.0 scopes for Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://localhost:5214/oauth2callback'

# Rest of your code...

load_dotenv()

EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
NODE_API_KEY = os.getenv('NODE_API_KEY')
NODE_SERVER_URL = os.getenv('NODE_SERVER_URL')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove or set to '0' in production

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import requests
import os
import logging
from dotenv import load_dotenv

# ... (existing imports and configurations)


@app.route('/authorize-gmail')
def authorize_gmail():
    redirect_uri = url_for('gmail_callback', _external=True)
    data = {
        'redirectUri': redirect_uri
    }
    response = communicate_with_node('/api/auth/gmail', data)
    if 'authUrl' in response:
        return redirect(response['authUrl'])
    else:
        return "Failed to initiate Gmail OAuth flow.", 500

@app.route('/fetch-gmail-emails', methods=['POST'])
def fetch_gmail_emails():
    access_token = session.get('gmail_access_token')
    if not access_token:
        return redirect(url_for('authorize_gmail'))
    
    data = {
        'accessToken': access_token
    }
    response = communicate_with_node('/api/gmail/fetch-emails', data)
    if 'error' in response:
        return f"Error fetching emails: {response['error']}", 500
    
    emails = response.get('messages', [])
    phishing_results = []
    
    for email in emails:
        # Fetch individual email details
        msg_id = email['id']
        email_details_response = requests.get(f"https://www.googleapis.com/gmail/v1/users/me/messages/{msg_id}", headers={
            'Authorization': f'Bearer {access_token}'
        })
        if email_details_response.status_code != 200:
            logging.error(f"Failed to fetch email ID {msg_id}")
            continue
        email_details = email_details_response.json()
        
        # Extract subject and sender
        headers = email_details.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        from_ = next((h['value'] for h in headers if h['name'] == 'From'), '(No Sender)')
        
        # Extract body
        parts = email_details.get('payload', {}).get('parts', [])
        body = ""
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='replace')
                    break
        else:
            body = email_details.get('payload', {}).get('body', {}).get('data', '')
            if body:
                body = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8', errors='replace')
        
        if not body:
            logging.info(f"Email ID {msg_id} has no plain text content.")
            continue
        
        # Send email body to AI phishing detector
        ai_response = get_groq_response(body)  # Ensure this function is defined
        
        # Parse AI response
        if ':' in ai_response:
            verdict, explanation = ai_response.split(':', 1)
            verdict = verdict.strip().lower()
            explanation = explanation.strip()

            if verdict == 'phishing':
                result = 'Phishing Attempt Detected'
            elif verdict == 'not phishing':
                result = 'No Phishing Detected'
            else:
                result = 'Unable to determine the nature of this email.'
        else:
            result = 'Unable to determine the nature of this email.'
            explanation = ai_response
        
        phishing_results.append({
            'Subject': subject,
            'From': from_,
            'Result': result,
            'AI Response': explanation
        })
    
    return render_template('gmail_emails.html', phishing_results=phishing_results)

# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import logging
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# ... [Other configurations and routes] ...
# ... [Other routes and app.run()] ...

def connect_to_email():
    # Create an SSL context to enhance security
    context = ssl.create_default_context()

    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)

    # Login to your email account
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

    return mail

def fetch_emails_from_inbox(mail):
    # Select the mailbox you want to use (in this case, the inbox)
    mail.select("inbox")

    # Search for all emails in the inbox
    status, messages = mail.search(None, 'ALL')

    # Convert the result to a list of email IDs
    email_ids = messages[0].split()

    emails = []

    # Fetch the last 10 emails (adjust as needed)
    for email_id in email_ids[-10:]:
        # Fetch the email by ID
        status, msg_data = mail.fetch(email_id, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the email content
                msg = email.message_from_bytes(response_part[1])

                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Decode email sender
                from_, encoding = decode_header(msg.get("From"))[0]
                if isinstance(from_, bytes):
                    from_ = from_.decode(encoding if encoding else "utf-8")

                # Extract email body
                if msg.is_multipart():
                    # Iterate over email parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        # Skip any attachments
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # Get the email body
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    # Email is not multipart
                    body = msg.get_payload(decode=True).decode()

                # Append email data to list
                emails.append({
                    "subject": subject,
                    "from": from_,
                    "body": body
                })

    return emails

def close_connection(mail):
    mail.logout()


@app.route('/gmail/callback')
def gmail_callback():
    code = request.args.get('code')
    if not code:
        return "Authorization code not provided.", 400
    
    redirect_uri = url_for('gmail_callback', _external=True)
    data = {
        'code': code,
        'redirectUri': redirect_uri
    }
    response = communicate_with_node('/api/auth/gmail/callback', data)
    if 'access_token' in response:
        session['gmail_access_token'] = response['access_token']
        session['gmail_refresh_token'] = response.get('refresh_token')
        return redirect(url_for('fetch_gmail_emails'))
    else:
        return "Failed to retrieve Gmail tokens.", 500


print(f"NODE_API_KEY: {NODE_API_KEY}")
print(f"NODE_SERVER_URL: {NODE_SERVER_URL}")

# app.py
@app.route('/test-node-gmail', methods=['GET'])
def test_node_gmail():
    data = {
        'accessToken': 'test_access_token'  # Replace with a valid access token if available
    }
    response = communicate_with_node('/api/gmail/fetch-emails', data)
    return jsonify(response)

# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import logging
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')  # Ensure this is set in .env

# Configure logging
logging.basicConfig(level=logging.INFO)

# Helper function to communicate with Node.js server
def communicate_with_node(endpoint, data):
    node_server_url = os.getenv('NODE_SERVER_URL', 'http://localhost:5000')
    api_key = os.getenv('NODE_API_KEY')

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    try:
        response = requests.post(f"{node_server_url}{endpoint}", json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return {'error': 'HTTP error occurred'}
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return {'error': 'An error occurred while communicating with Node.js server'}

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/fetch-emails-imap', methods=['GET'])
def fetch_emails_imap():
    try:
        mail = connect_to_email()
        emails = fetch_emails_from_inbox(mail)
        close_connection(mail)

        # Analyze each email for phishing
        analyzed_emails = []
        for email_data in emails:
            body = email_data['body']
            prediction = detect_phishing(body)
            email_data['phishing_prediction'] = prediction
            analyzed_emails.append(email_data)

        return jsonify({"emails": analyzed_emails})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Enable OAuthlib to use insecure transport (Development Only)

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
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Remove print statements for security
# print(GOOGLE_CLIENT_ID)
# print(GOOGLE_CLIENT_SECRET)

if not all([GROQ_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
    logging.error("One or more environment variables are missing. Please check your .env file.")
    exit(1)

groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

# OAuth 2.0 setup
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'email'
]

@app.route('/test-node', methods=['GET'])
def test_node():
    data = {
        'accessToken': 'test_access_token'
    }
    response = communicate_with_node('/api/outlook/fetch-emails', data)
    return jsonify(response)

@app.route('/list-endpoints')
def list_endpoints():
    import pprint
    output = {}
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        output[rule.endpoint] = {
            'methods': methods,
            'url': rule.rule
        }
    return pprint.pformat(output)


def get_gmail_credentials():
    creds = None
    if 'credentials' in session:
        creds_data = session['credentials']
        creds = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                session['credentials'] = creds_to_dict(creds)
                return redirect(url_for('index'))
            except Exception as e:
                logging.error(f"Error refreshing credentials: {e}")
                return redirect(url_for('authorize'))
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri=url_for('oauth2callback', _external=True)
            )
            auth_url, _ = flow.authorization_url(prompt='consent')
            return redirect(auth_url)
    # If credentials are valid, proceed without redirect
    return creds


def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    
@app.route('/authorize/outlook')
def authorize_outlook():
    redirect_uri = url_for('outlook_callback', _external=True)
    data = {
        'redirectUri': redirect_uri
    }
    response = communicate_with_node('/api/auth/outlook', data)
    if 'authUrl' in response:
        return redirect(response['authUrl'])
    else:
        return "Failed to initiate Outlook OAuth flow.", 500

def refresh_outlook_token():
    refresh_token = session.get('outlook_refresh_token')
    if not refresh_token:
        return None
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': os.getenv('OUTLOOK_CLIENT_ID'),
        'client_secret': os.getenv('OUTLOOK_CLIENT_SECRET')
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-key': NODE_API_KEY
    }
    try:
        response = requests.post(f"{NODE_SERVER_URL}/api/auth/outlook/token", data=data, headers=headers)
        response.raise_for_status()
        tokens = response.json()
        session['outlook_access_token'] = tokens['access_token']
        session['outlook_refresh_token'] = tokens.get('refresh_token', refresh_token)  # Update if new refresh token is provided
        return tokens['access_token']
    except Exception as e:
        logging.error(f"Error refreshing Outlook token: {e}")
        return None


@app.route('/fetch-outlook-emails', methods=['GET'])
def fetch_outlook_emails():
    access_token = session.get('outlook_access_token')
    if not access_token:
        return redirect(url_for('authorize_outlook'))
    
    data = {
        'accessToken': access_token
    }
    response = communicate_with_node('/api/outlook/fetch-emails', data)
    if 'error' in response:
        return f"Error fetching emails: {response['error']}", 500
    
    emails = response.get('value', [])
    phishing_results = []
    
    for email in emails:
        # Prepare email content
        email_content = f"Subject: {email['subject']}\nFrom: {email['from']}\n\n{email['body']}"
        ai_response = get_groq_response(email_content)  # Assuming get_groq_response is defined
        
        # Parse AI response
        if ':' in ai_response:
            verdict, explanation = ai_response.split(':', 1)
            verdict = verdict.strip().lower()
            explanation = explanation.strip()

            if verdict == 'phishing':
                result = 'Phishing Attempt Detected'
            elif verdict == 'not phishing':
                result = 'No Phishing Detected'
            else:
                result = 'Unable to determine the nature of this email.'
        else:
            result = 'Unable to determine the nature of this email.'
            explanation = ai_response

        phishing_results.append({
            'Subject': email['subject'],
            'From': email['from'],
            'Result': result,
            'AI Response': explanation
        })

    return render_template('outlook_emails.html', phishing_results=phishing_results)



@app.route('/outlook/callback')
def outlook_callback():
    code = request.args.get('code')
    if not code:
        return "Authorization code not provided.", 400
    
    redirect_uri = url_for('outlook_callback', _external=True)
    data = {
        'code': code,
        'redirectUri': redirect_uri
    }
    response = communicate_with_node('/api/auth/outlook/callback', data)
    if 'access_token' in response:
        session['outlook_access_token'] = response['access_token']
        session['outlook_refresh_token'] = response.get('refresh_token')
        return redirect(url_for('fetch_outlook_emails'))
    else:
        return "Failed to retrieve Outlook tokens.", 500

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
        return "Error: Unable to process the request."
    except requests.exceptions.RequestException as e:
        logging.error(f"Groq API Request exception: {e}")
        return "Error: Unable to connect to the AI service."
    except KeyError as e:
        logging.error(f"Groq API response parsing error: {e}")
        return "Error: Invalid response from the AI service."

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


# app.py

@app.route('/scan_emails')
def scan_emails():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    creds = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Fetch emails
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        emails = []

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            # Extract email details
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
            body = get_email_body(msg['payload'])

            # Analyze email for phishing using your AI function
            phishing_prediction, ai_response = detect_phishing(body)

            emails.append({
                'id': message['id'],
                'subject': subject,
                'from': from_,
                'body': body,  # Optionally include the body if needed
                'phishing_prediction': phishing_prediction,
                'ai_response': ai_response
            })

        session['credentials'] = credentials_to_dict(creds)
        return render_template('emails.html', emails=emails)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred while fetching emails.", 500


    
@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(authorization_response=request.url)
    # Rest of your code...

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('scan_emails'))


# Route to handle phishing detection manually
@app.route('/detect-phishing', methods=['POST'])
def detect_phishing(email_content):
    # Initialize variables
    verdict = None
    explanation = None

    try:
        # Send the email content to the AI model for phishing detection
        ai_response = get_groq_response(email_content)

        # Convert AI response to lowercase for consistent parsing
        ai_response_lower = ai_response.lower()

        # Check for keywords indicating phishing
        if 'phishing' in ai_response_lower:
            result = 'Phishing Attempt Detected'
            explanation = ai_response
        elif 'not phishing' in ai_response_lower:
            result = 'No Phishing Detected'
            explanation = ai_response
        elif 'possible phishing' in ai_response_lower or 'suspicious' in ai_response_lower:
            result = 'Possible Phishing Attempt Detected'
            explanation = ai_response
        else:
            # Default case
            result = 'Unable to determine the nature of this email.'
            explanation = ai_response  # Include the raw AI response for debugging

    except Exception as e:
        # Handle any other unforeseen errors
        app.logger.error(f"Error during phishing detection: {e}")
        result = 'An error occurred while analyzing the email.'
        explanation = 'No explanation available.'

    return result, explanation



@app.route('/detect_phishing', methods=['POST'])
def detect_phishing_route():
    email_content = request.form.get('email_content')
    if not email_content:
        return jsonify({'error': 'Email content is required.'}), 400

    # Call the phishing detection function with the email content
    phishing_prediction, ai_response = detect_phishing(email_content)

    # Return the result as JSON
    return jsonify({
        'result': phishing_prediction,
        'ai_response': ai_response,
        'confidence': 'High'  # Or calculate confidence if applicable
    })

def detect_phishing_route_logic(email_content):
    # Initialize variables
    verdict = None
    explanation = None

    try:
        # Send the email content to Groq for phishing detection
        ai_response = get_groq_response(email_content)

        # Expected AI Response Format:
        # "Phishing: [Explanation]"
        # or
        # "Not Phishing: [Explanation]"

        # Split the AI response into verdict and explanation
        if ':' in ai_response:
            verdict, explanation = ai_response.split(':', 1)
            verdict = verdict.strip().lower()
            explanation = explanation.strip()

            if verdict == 'phishing':
                result = 'This email appears to be a phishing attempt.'
            elif verdict == 'not phishing':
                result = 'This email seems safe.'
            else:
                result = 'Unable to determine the nature of this email.'
        else:
            # Handle cases where AI response doesn't contain a colon
            logging.error("Unexpected AI response format.")
            result = 'Unable to determine the nature of this email.'
            explanation = ai_response  # Include the raw AI response for debugging

    except ValueError:
        # Handle cases where AI response doesn't contain a colon
        logging.error("Unexpected AI response format.")
        result = 'Unable to determine the nature of this email.'
        explanation = ai_response  # Include the raw AI response for debugging
    except Exception as e:
        # Handle any other unforeseen errors
        logging.error(f"Error during phishing detection: {e}")
        result = 'An error occurred while analyzing the email.'
        explanation = 'No explanation available.'

    return result, explanation

# Function to generate OAuth2 string for IMAP authentication
def generate_oauth2_string(username, access_token):
    auth_string = f"user={username}\1auth=Bearer {access_token}\1\1"
    return base64.b64encode(auth_string.encode()).decode()

# Route to initiate Gmail authentication
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    app.logger.debug(f"Authorization URL: {authorization_url}")
    return redirect(authorization_url)

# app.py

def get_email_body(payload):
    import base64

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                break
            elif part['mimeType'] == 'text/html':
                data = part['body']['data']
                break
    else:
        data = payload['body']['data']

    if data:
        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
        return decoded_data
    else:
        return ''


@app.route('/view_email/<email_id>')
def view_email(email_id):
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    creds = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Fetch the email by ID
        msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()

        # Extract email details
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_ = next((h['value'] for h in headers if h['name'] == 'From'), '')
        body = get_email_body(msg['payload'])

        # Update credentials in session if refreshed
        session['credentials'] = credentials_to_dict(creds)

        # Render the email content
        return render_template('email_detail.html', subject=subject, from_=from_, body=body)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred while fetching the email.", 500

# app.py

@app.route('/append_email_to_ai/<email_id>')
def append_email_to_ai(email_id):
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    creds = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Fetch the email by ID
        msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()

        # Extract the email body
        body = get_email_body(msg['payload'])

        # Store the email body in the session or pass it to the template
        return render_template('ai_inspection.html', email_content=body)

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return "An error occurred while preparing the email for AI inspection.", 500

# app.py
from flask import jsonify

# app.py

@app.route('/ai_inspect_ajax', methods=['POST'])
def ai_inspect_ajax():
    data = request.get_json()
    email_content = data.get('email_content', '')

    phishing_prediction, ai_response = detect_phishing(email_content)

    return jsonify({
        'phishing_prediction': phishing_prediction,
        'ai_response': ai_response
    })

# app.py

@app.route('/get_email_content/<email_id>')
def get_email_content(email_id):
    if 'credentials' not in session:
        return jsonify({'error': 'User not authenticated.'}), 401

    creds = Credentials(**session['credentials'])
    service = build('gmail', 'v1', credentials=creds)

    try:
        msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
        body = get_email_body(msg['payload'])

        # Update credentials in session if refreshed
        session['credentials'] = credentials_to_dict(creds)

        return jsonify({'body': body})

    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': 'An error occurred while fetching the email.'}), 500




@app.route('/ai_inspect', methods=['POST'])
def ai_inspect():
    email_content = request.form.get('email_content', '')

    # Call your AI phishing detection function
    phishing_prediction, ai_response = detect_phishing(email_content)

    # Render the results
    return render_template('ai_results.html', email_content=email_content, phishing_prediction=phishing_prediction, ai_response=ai_response)

    
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@app.route('/fetch-custom-emails', methods=['POST'])
def fetch_custom_emails():
    try:
        data = request.get_json()
        email_address = data.get('email_address')
        email_password = data.get('email_password')

        if not email_address or not email_password:
            return jsonify({'error': 'Email address and password are required.'}), 400

        emails = fetch_emails_from_custom_account(email_address, email_password)
        return jsonify({'emails': emails})
    except Exception as e:
        app.logger.error(f"Error fetching emails: {e}", exc_info=True)
        return jsonify({'error': f'Failed to fetch emails: {str(e)}'}), 500


def fetch_emails_from_custom_account(email_address, email_password):
    # Your IMAP server settings
    IMAP_SERVER = 'mail.wayne.cool'
    IMAP_PORT = 993  # For SSL

    # Create an SSL context
    context = ssl.create_default_context()

    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)

    # Login to your email account
    mail.login(email_address, email_password)

    # Select the mailbox you want to use (in this case, the inbox)
    mail.select("INBOX")

    # Search for all emails in the inbox
    status, messages = mail.search(None, 'ALL')

    # Convert the result to a list of email IDs
    email_ids = messages[0].split()

    emails = []

    # Fetch the last 10 emails (adjust as needed)
    for email_id in email_ids[-10:]:
        # Fetch the email by ID
        status, msg_data = mail.fetch(email_id, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the email content
                msg = email.message_from_bytes(response_part[1])

                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Decode email sender
                from_, encoding = decode_header(msg.get("From"))[0]
                if isinstance(from_, bytes):
                    from_ = from_.decode(encoding if encoding else "utf-8")

                # Extract email body
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                # Analyze email for phishing
                phishing_prediction, ai_response = detect_phishing(body)

                # Append email data to list
                emails.append({
                    "subject": subject,
                    "from": from_,
                    "body": body,
                    "phishing_prediction": phishing_prediction,
                    "ai_response": ai_response
                })

    # Logout from the email server
    mail.logout()

    return emails

# Landing page
@app.route('/')
def index():
    return render_template('index.html')  # Ensure 'fetch_emails_imap' is defined before rendering

@app.route('/list_routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)
    return '<br>'.join(sorted(output))


# Route to fetch latest emails and detect phishing
@app.route('/fetch-emails', methods=['POST'])
def fetch_emails():
    creds = get_gmail_credentials()
    if isinstance(creds, Response):
        return creds  
        
    creds_data = session['credentials']
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=creds_data.get('scopes')
    )

    if not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                session['credentials'] = creds_to_dict(creds)
            except Exception as e:
                logging.error(f"Error refreshing credentials: {e}")
                return jsonify({'error': 'Failed to refresh credentials. Please re-authorize your Gmail account.'}), 401
        else:
            return jsonify({'error': 'Invalid credentials. Please re-authorize your Gmail account.'}), 401

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
                        if ':' in ai_response:
                            verdict, explanation = ai_response.split(':', 1)
                            verdict = verdict.strip().lower()
                            explanation = explanation.strip()

                            if verdict == 'phishing':
                                result = 'Phishing Attempt Detected'
                            elif verdict == 'not phishing':
                                result = 'No Phishing Detected'
                            else:
                                result = 'Unable to determine the nature of this email.'
                        else:
                            # Handle cases where AI response doesn't contain a colon
                            logging.error("Unexpected AI response format.")
                            result = 'Unable to determine the nature of this email.'
                            explanation = ai_response  # Include the raw AI response for debugging

                    except ValueError:
                        # Handle cases where AI response doesn't contain a colon
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
