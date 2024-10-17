# Written by Wayne Kenney
# Influencing a new era in Cyber-security using AI 
# Integrated with software code (Python)

import os
import json
import requests
import pandas as pd
from datetime import datetime
from mem0 import MemoryClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import unittest
import yaml
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import  sys
from pydantic import BaseModel, Field, root_validator

sys.setrecursionlimit(5000) 

# ----------------------- Configuration Setup ----------------------- #

# Load configuration from config.yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize MemoryClient with the API key from config
mem_client = MemoryClient(api_key=config['api_keys']['mem0'])
api_url = config['api_endpoints']['chat']

# Print API details for debugging (remove or comment out in production)
print(f"MemClient API Key: {config['api_keys']['mem0']} . API URL: {api_url}")

# Configure logging
logging.basicConfig(
    filename=config['logging']['file'],
    level=getattr(logging, config['logging']['level']),
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Initialize user context
user_context = {}

# ----------------------- Utility Functions ----------------------- #

def validate_html(target_url):
    """
    Validate HTML of the target URL using the W3C Validator API.
    """
    api_url = "https://validator.w3.org/nu/?out=json"
    headers = {'Content-Type': 'text/html; charset=UTF-8'}
    params = {'doc': target_url}
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTML validation error for {target_url}: {e}")
        return {"error": str(e)}

def log_ai_response(ai_response):
    """
    Log AI responses into a text file with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "ai_feedback_log.txt"

    try:
        with open(log_file, 'a', encoding='utf-8') as file:
            file.write(f"{timestamp} - AI Response:\n{ai_response}\n\n")
        print(f"AI response logged successfully at {timestamp}.")
    except IOError as e:
        logging.error(f"Failed to write AI response to log: {e}")
        print(f"Failed to write AI response to log: {e}")



def analyze_response(response):
    """
    Analyze the response to determine if a vulnerability exists.
    """
    if "alert(1)" in response.text or "whoami" in response.text:
        print("Possible vulnerability detected!")
        return True
    else:
        print("No vulnerability detected in this test.")
        return False

def get_groq_response(email_content):
    """
    Placeholder function to interface with the Groq AI model.
    Replace this with the actual implementation.
    """
    # Example implementation (replace with actual AI model call)
    # For demonstration, returning a mock response
    return "Phishing: This email contains suspicious links and requests personal information."

def suggest_remediation(vulnerability_type):
    """
    Suggest remediation steps based on the vulnerability type.
    """
    remediation_steps = {
        "XSS": "Implement proper input validation and output encoding. Use Content Security Policy (CSP) headers.",
        "SQL Injection": "Use parameterized queries or ORM frameworks to prevent SQL injection.",
        "Rate Limiting Bypass": "Implement rate limiting and monitoring to detect and block excessive requests.",
        "Command Injection": "Validate and sanitize all user inputs. Avoid executing shell commands directly.",
        "SSRF": "Restrict server-side requests to trusted domains and validate all URLs."
    }
    return remediation_steps.get(vulnerability_type, "No remediation steps available.")

# ----------------------- AI Integration ----------------------- #

def generate(user_id: str, prompt: str, target_url: str = None):
    """
    Generate AI threat analysis, optionally including HTML validation.
    """
    context = user_context.get(user_id, "")
    context += f"User: {prompt}\n"

    # Save user input into memory
    user_message = {"role": "user", "content": prompt}
    mem_client.add([user_message], user_id=user_id)

    # Perform HTML validation if a target URL is provided
    if target_url:
        html_validation_result = validate_html(target_url)
        context += f"HTML Validation Report for {target_url}:\n{json.dumps(html_validation_result, indent=2)}\n"

    # Prepare the API request
    api_url_endpoint = config['api_endpoints']['chat']
    headers = {"Content-Type": "application/json"}

    # Construct the payload for the AI model
    payload = {
        "model": "llama2-uncensored:latest",  # Choose a more aggressive and suitable model, such as "White Rabbit Neo". ;)
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant specialized in penetration testing. "
                    "Your task is to identify common web application vulnerabilities in a target URL, such as:\n"
                    "1. **XSS (Cross-Site Scripting)**\n"
                    "2. **SQL Injection**\n"
                    "3. **Rate Limiting Bypass**\n"
                    "4. **Command Injection**\n"
                    "5. **SSRF (Server-Side Request Forgery)**\n"
                    "Run these tests on the target URL and analyze the responses."
                ),
            },
            {
                "role": "user",
                "content": f"Please run tests on the following target: {target_url}"
            }
        ]
    }

    try:
        response = requests.post(api_url_endpoint, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        # Print the raw response for debugging
        # print("Raw response text:")
        # print(response.text)

        # Parse the response based on its format
        lines = response.text.strip().split('\n')
        ai_response = ""
        for line in lines:
            try:
                data = json.loads(line)
                if 'message' in data and 'content' in data['message']:
                    ai_response += data['message']['content']
            except json.JSONDecodeError:
                continue

        # Update context and log the AI response
        context += f"AI: {ai_response}\n"
        user_context[user_id] = context
        log_ai_response(ai_response)

        # Fetch and display the last 20 user messages
        previous_messages = mem_client.get_all(user_id=user_id)
        recent_messages = previous_messages[-20:]
        formatted_messages = ""
        for msg in recent_messages:
            if msg.get('role') == "user":
                formatted_messages += f"User: {msg.get('content')}\n"

        context += f"{formatted_messages}AI: {ai_response}\n"
        user_context[user_id] = context

        # Display AI response
        print(f"\nAI: {ai_response}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        print(f"Request error: {e}")

# ----------------------- Recursive Web Scanning ----------------------- #

def extract_links(html_content, base_url):
    """
    Extract and return all unique, absolute URLs from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()

    for tag in soup.find_all(['a', 'link', 'script', 'img']):
        href = tag.get('href') or tag.get('src')
        if href:
            # Construct absolute URL
            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)
            # Only include HTTP and HTTPS URLs
            if parsed_url.scheme in ['http', 'https']:
                links.add(absolute_url)

    return links

def is_same_domain(url1, url2):
    """
    Check if two URLs belong to the same domain.
    """
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2

def recursive_scan(start_url, max_depth=2):
    """
    Recursively scan the website starting from start_url up to max_depth.
    """
    visited = set()
    vulnerabilities = {}

    def scan(url, depth):
        if depth > max_depth:
            return
        if url in visited:
            return
        visited.add(url)
        print(f"\nScanning URL: {url} (Depth: {depth})")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {url}: {e}")
            print(f"Failed to fetch {url}: {e}")
            return

        # Perform vulnerability tests
        vuln_detected = test_for_exploits(url)
        if vuln_detected:
            vulnerabilities[url] = vuln_detected

        # Extract and scan links recursively
        links = extract_links(html_content, url)
        for link in links:
            if is_same_domain(start_url, link):
                scan(link, depth + 1)

    scan(start_url, 1)
    return vulnerabilities

# ----------------------- Vulnerability Testing ----------------------- #

def test_for_exploits(target_url):
    """
    Test the target URL for common vulnerabilities using predefined payloads.
    Returns a list of detected vulnerabilities.
    """
    detected_vulnerabilities = []

    # Payloads for each type of vulnerability
    xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
    sql_injection_payloads = ["' OR '1'='1", "' OR 'x'='x"]
    command_injection_payloads = ["; ls", "| whoami"]

    # Test XSS payloads
    for payload in xss_payloads:
        print(f"Testing XSS with payload: {payload}")
        generate(user_id, "test for XSS vulnerabilities", target_url=start_url)
        params = {'input': payload}
        try:
            response = requests.get(target_url, params=params, timeout=10)
            if analyze_response(response):
                detected_vulnerabilities.append("XSS")
        except requests.exceptions.RequestException as e:
            logging.error(f"XSS test failed for {target_url}: {e}")
            print(f"XSS test failed for {target_url}: {e}")

    # Test SQL Injection payloads
    for payload in sql_injection_payloads:
        print(f"Testing SQL Injection with payload: {payload}")
        generate(user_id, "test for SQLi vulnerabilities", target_url=start_url)

        data = {'input': payload}
        try:
            response = requests.post(target_url, data=data, timeout=10)
            if analyze_response(response):
                detected_vulnerabilities.append("SQL Injection")
        except requests.exceptions.RequestException as e:
            logging.error(f"SQL Injection test failed for {target_url}: {e}")
            print(f"SQL Injection test failed for {target_url}: {e}")

    # Test Command Injection payloads
    for payload in command_injection_payloads:
        print(f"Testing Command Injection with payload: {payload}")
        generate(user_id, "test for Command Injection vulnerabilities", target_url=start_url)

        data = {'cmd': payload}
        try:
            response = requests.post(target_url, data=data, timeout=10)
            if analyze_response(response):
                detected_vulnerabilities.append("Command Injection")
        except requests.exceptions.RequestException as e:
            logging.error(f"Command Injection test failed for {target_url}: {e}")
            print(f"Command Injection test failed for {target_url}: {e}")

    return detected_vulnerabilities

# ----------------------- Model Training ----------------------- #

def train_threat_hunting_model(file_path):
    """
    Train a Random Forest model for threat detection.
    """
    data = pd.read_csv(file_path)

    # Feature engineering
    data['event_frequency'] = data.groupby('source_ip')['event_id'].transform('count')
    data['time_diff'] = data['timestamp'].diff().fillna(0)

    # Handle categorical data if any
    X = pd.get_dummies(data.drop('is_threat', axis=1), drop_first=True)
    y = data['is_threat']

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model with hyperparameter tuning
    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    print(report)

    return model

# ----------------------- Main Execution ----------------------- #

if __name__ == "__main__":
    user_id = "default_user"

    # Start the AI interaction with optional website validation
    while True:
        # For recursive scanning, prompt the user for the start URL
        start_url = input("Enter the start URL for scanning (or 'exit' to quit): ").strip()
        if start_url.lower() == 'exit':
            print("Exiting the scanner.")
            break
        elif not start_url:
            print("Please enter a valid URL.")
            continue

        prompt = "Can you test this server for me, friend? I'm curious about what you can find. Thanks!"
        generate(user_id, prompt, target_url=start_url)

        # Define maximum recursion depth
        max_depth = 2  # Adjust as needed

        # Perform recursive scanning
        print("\nStarting recursive web scan...")
        vulnerabilities_found = recursive_scan(start_url, max_depth=max_depth)

        # Display and log vulnerabilities
        if vulnerabilities_found:
            print("\nVulnerabilities Detected:")
            for url, vulns in vulnerabilities_found.items():
                print(f"\nURL: {url}")
                for vuln in vulns:
                    print(f" - {vuln}: {suggest_remediation(vuln)}")
        else:
            print("\nNo vulnerabilities detected during the scan.")

        # Optionally, log the vulnerabilities or generate a report
        # This can be implemented as needed

        # Sleep for a short duration to prevent overwhelming the server
        time.sleep(2)
