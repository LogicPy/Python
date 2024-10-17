# Written by Wayne Kenney
# Influencing a new era in Cyber-security using ai 
# Integrated with software code (python)

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

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

mem_client = MemoryClient(api_key=config['api_keys']['mem0'])
api_url = config['api_endpoints']['chat']

#print(str(mem_client) + ' . ' + str(api_url))
print(f"MemClient API Key: {config['api_keys']['mem0']} . API URL: {api_url}")

logging.basicConfig(
    filename=config['logging']['file'],
    level=getattr(logging, config['logging']['level']),
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Initialize the MemoryClient with your API key
user_context = {}

def validate_html(target_url):
    """
    Validate HTML of the target URL using the W3C Validator API.
    """
    api_url = "https://validator.w3.org/nu/?out=json"
    headers = {'Content-Type': 'text/html; charset=UTF-8'}
    params = {'doc': target_url}
    response = requests.get(api_url, params=params, headers=headers)
    return response.json()

def log_ai_response(ai_response):
    """
    Log AI responses into a text file with a timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "ai_feedback_log.txt"

    with open(log_file, 'a') as file:
        file.write(f"{timestamp} - AI Response:\n{ai_response}\n\n")

    print(f"AI response logged successfully at {timestamp}.")

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
        context += f"HTML Validation Report for {target_url}:\n{html_validation_result}\n"

    # Prepare the API request
    api_url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}

    # Construct the payload for the AI model
    payload = {
        "model": "llama2-uncensored:latest", # Choose a more aggressive and suitable model, such as "White Rabbit Neo". ;)
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
        response = requests.post(api_url, json=payload, headers=headers)
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
        print(f"Request error: {e}")


def test_for_exploits(target_url):
    """
    Test the target URL for common vulnerabilities using predefined payloads.
    """
    # Payloads for each type of vulnerability
    xss_payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]
    sql_injection_payloads = ["' OR '1'='1", "' OR 'x'='x"]
    command_injection_payloads = ["; ls", "| whoami"]

    # Test XSS payloads
    for payload in xss_payloads:
        print(f"Testing XSS with payload: {payload}")
        params = {'input': payload}
        response = requests.get(target_url, params=params)
        analyze_response(response)

    # Test SQL Injection payloads
    for payload in sql_injection_payloads:
        print(f"Testing SQL Injection with payload: {payload}")
        data = {'input': payload}
        response = requests.post(target_url, data=data)
        analyze_response(response)

    # Test Command Injection payloads
    for payload in command_injection_payloads:
        print(f"Testing Command Injection with payload: {payload}")
        data = {'cmd': payload}
        response = requests.post(target_url, data=data)
        analyze_response(response)

def analyze_response(response):
    """
    Analyze the response to determine if a vulnerability exists.
    """
    if "alert(1)" in response.text or "whoami" in response.text:
        print("Possible vulnerability detected!")
    else:
        print("No vulnerability detected in this test.")

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


if __name__ == "__main__":
    user_id = "default_user"

    # Start the AI interaction with optional website validation
    while True:
        prompt = input("Enter your prompt: ")
        target_url = input("Enter a URL to validate (or leave blank): ").strip()
        if target_url:
            generate(user_id, prompt, target_url=target_url)
        else:
            generate(user_id, prompt)
