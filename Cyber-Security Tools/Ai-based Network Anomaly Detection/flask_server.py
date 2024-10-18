from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import logging
import requests
import json
from waitress import serve  # Using Waitress as the WSGI server

app = Flask(__name__)

# Load preprocessor and model
try:
    preprocessor = joblib.load('preprocessor.pkl')
    print("Preprocessor loaded successfully.")
except Exception as e:
    print(f"Error loading preprocessor: {e}")

try:
    isolation_forest = joblib.load('isolation_forest_model.pkl')
    print("Isolation Forest model loaded successfully.")
except Exception as e:
    print(f"Error loading Isolation Forest model: {e}")

# Configure Logging
logging.basicConfig(
    filename='flask_server.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Configuration for Ollama API
OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Ensure this matches Ollama's API endpoint
OLLAMA_MODEL_NAME = "llama3"  # Replace with your actual model name


# Prediction Endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to receive data and return anomaly prediction along with AI elaboration.
    Expects JSON input with feature data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        if isinstance(data, dict):
            data = [data]

        input_df = pd.DataFrame(data)

        # Preprocess input data
        processed_data = preprocessor.transform(input_df)

        # Make predictions
        predictions = isolation_forest.predict(processed_data)

        # Convert predictions to labels
        labels = ['anomaly' if pred == -1 else 'normal' for pred in predictions]

        # Identify anomalies for elaboration
        anomalies = input_df[predictions == -1]

        elaborations = {}
        if not anomalies.empty:
            elaborations = elaborate_assessment(anomalies.to_dict(orient='records'))

        # Prepare response
        response = {
            'predictions': labels,
            'elaborations': elaborations
        }

        # Log predictions and elaborations
        logging.info(f"Received data: {data}")
        logging.info(f"Predictions: {labels}")
        if elaborations:
            logging.info(f"Elaborations: {elaborations}")

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500


def elaborate_assessment(anomalies):
    """
    Use the AI model to elaborate on each detected anomaly.

    Parameters:
    - anomalies (list of dict): List of anomalous records.

    Returns:
    - dict: A dictionary with source IPs as keys and elaborated assessments as values.
    """
    elaborated_results = {}

    for anomaly in anomalies:
        source_ip = anomaly.get('source_ip')
        destination_ip = anomaly.get('destination_ip')
        bytes_transmitted = anomaly.get('bytes')
        packets_transmitted = anomaly.get('packets')
        unique_dest_ips = anomaly.get('unique_dest_ips')
        total_bytes = anomaly.get('total_bytes')
        packet_rate = anomaly.get('packet_rate')

        # Construct prompt
        prompt = (
            f"The following anomaly was detected in network traffic:\n"
            f"Source IP: {source_ip}\n"
            f"Destination IP: {destination_ip}\n"
            f"Bytes Transmitted: {bytes_transmitted}\n"
            f"Packets Transmitted: {packets_transmitted}\n"
            f"Unique Destination IPs: {unique_dest_ips}\n"
            f"Total Bytes: {total_bytes}\n"
            f"Packet Rate: {packet_rate} packets/sec\n\n"
            f"Please provide a detailed explanation of why this traffic pattern is considered anomalous and suggest remediation steps."
        )

        # Prepare API request
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant specialized in cybersecurity. "
                        "Your task is to provide detailed explanations and remediation steps for detected network anomalies."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        try:
            # Send request to Ollama API
            response = requests.post(OLLAMA_API_URL, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            # Handle multi-line JSON responses
            elaborated_text = ""
            lines = response.text.strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        elaborated_text += data['message']['content']
                except json.JSONDecodeError:
                    continue

            elaborated_text = elaborated_text.strip()

            elaborated_results[source_ip] = elaborated_text

            # Log AI response
            logging.info(f"Elaboration for {source_ip}: {elaborated_text}")

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error in elaborate_assessment for {source_ip}: {e}")
            elaborated_results[source_ip] = f"Request error: {e}"
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in elaborate_assessment for {source_ip}: {e}")
            elaborated_results[source_ip] = "Failed to parse AI response."

    return elaborated_results


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
