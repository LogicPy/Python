![net-anom](images/net-anom.png)

# Anomaly Detection System

![Anomaly Detection](https://img.shields.io/badge/Anomaly-Detection-brightgreen)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Data Generation](#1-data-generation)
  - [2. Training the Model](#2-training-the-model)
  - [3. Running the Flask Server](#3-running-the-flask-server)
  - [4. Testing the Server](#4-testing-the-server)
- [File Descriptions](#file-descriptions)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Introduction

Welcome to the **Anomaly Detection System**, a comprehensive tool designed to identify unusual patterns in network traffic data. This system leverages machine learning techniques to distinguish between normal and anomalous network activities, providing detailed explanations and remediation steps for detected anomalies through seamless integration with the Ollama AI service.

Whether you're a cybersecurity professional, network administrator, or a developer interested in anomaly detection, this tool offers a robust solution to enhance your network security posture.

## Features

- **Data Generation:** Create synthetic network traffic data, including both normal and anomalous records.
- **Model Training:** Preprocess data and train an Isolation Forest model to detect anomalies.
- **Flask API Server:** Host the trained model to serve real-time predictions via a RESTful API.
- **AI Integration:** Generate detailed explanations and remediation steps for detected anomalies using the Ollama AI service.
- **Batch Testing:** Automate the testing process with concurrent requests to ensure system reliability.
- **Logging:** Comprehensive logging of requests, predictions, and AI elaborations for monitoring and analysis.

## Prerequisites

Before setting up the Anomaly Detection System, ensure you have the following installed on your machine:

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **Virtual Environment (optional but recommended)**
- **Ollama AI Service** running and accessible at `http://localhost:11434/api/chat`
- **Git** (for version control)

## Installation

1. **Clone the Repository**

   ```bash
   cd anomaly-detection


```markdown
# Anomaly Detection System

![Anomaly Detection](https://img.shields.io/badge/Anomaly-Detection-brightgreen)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Data Generation](#1-data-generation)
  - [2. Training the Model](#2-training-the-model)
  - [3. Running the Flask Server](#3-running-the-flask-server)
  - [4. Testing the Server](#4-testing-the-server)
- [File Descriptions](#file-descriptions)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Introduction

Welcome to the **Anomaly Detection System**, a comprehensive tool designed to identify unusual patterns in network traffic data. This system leverages machine learning techniques to distinguish between normal and anomalous network activities, providing detailed explanations and remediation steps for detected anomalies through seamless integration with the Ollama AI service.

Whether you're a cybersecurity professional, network administrator, or a developer interested in anomaly detection, this tool offers a robust solution to enhance your network security posture.

## Features

- **Data Generation:** Create synthetic network traffic data, including both normal and anomalous records.
- **Model Training:** Preprocess data and train an Isolation Forest model to detect anomalies.
- **Flask API Server:** Host the trained model to serve real-time predictions via a RESTful API.
- **AI Integration:** Generate detailed explanations and remediation steps for detected anomalies using the Ollama AI service.
- **Batch Testing:** Automate the testing process with concurrent requests to ensure system reliability.
- **Logging:** Comprehensive logging of requests, predictions, and AI elaborations for monitoring and analysis.

## Prerequisites

Before setting up the Anomaly Detection System, ensure you have the following installed on your machine:

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **Virtual Environment (optional but recommended)**
- **Ollama AI Service** running and accessible at `http://localhost:11434/api/chat`
- **Git** (for version control)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/anomaly-detection.git
   cd anomaly-detection
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Dependencies**

   Ensure you have a `requirements.txt` file with the necessary packages. If not, create one with the following content:

   ```plaintext
   Flask==2.2.5
   joblib==1.3.2
   pandas==1.5.3
   numpy==1.24.3
   scikit-learn==1.2.2
   requests==2.31.0
   Faker==15.3.4
   waitress==2.2.0
   ```

   Then install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

The Anomaly Detection System consists of four main components:

1. **Data Generation (`anomaly.py`)**
2. **Model Training (`training.py`)**
3. **Flask API Server (`flask_server.py`)**
4. **Batch Testing (`Anomaly_test.py`)**

### 1. Data Generation

**Note:** There is a typo in the original file name `anomoly.py`. It should be renamed to `anomaly.py` for consistency and to avoid confusion.

**Renaming the File:**

No longer needed in this setup...

**Running the Data Generation Script:**

```bash
python anomaly.py
```

**Output:**

```
Generating 9500 normal traffic records...
Generating 500 anomalous traffic records...
Dataset saved to network_traffic.csv with 10000 records.
```

This script generates synthetic network traffic data, comprising both normal and anomalous records, and saves it to `network_traffic.csv`.

### 2. Training the Model

**Running the Training Script:**

```bash
python training.py
```

**Output:**

```
Model and preprocessor saved successfully.
```

This script preprocesses the data by handling missing values, trains an Isolation Forest model to detect anomalies, and saves both the model and preprocessor for later use by the Flask server.

### 3. Running the Flask Server

**Starting the Flask Server:**

```bash
python flask_server.py
```

**Console Output:**

```
Preprocessor loaded successfully.
Isolation Forest model loaded successfully.
Serving on http://0.0.0.0:5000
```

The Flask server hosts the anomaly detection model and exposes a `/predict` endpoint to receive network traffic data and return predictions along with AI-generated elaborations.

### 4. Testing the Server

**Running the Batch Testing Script:**

```bash
python Anomaly_test.py
```

**Sample Output:**

```
Starting Batch Testing...

Test Case 1: Success
Test Case 2: Success
Test Case 3: Success
Test Case 4: Success

Batch Testing Completed. Check 'batch_test.log' for detailed logs.

Total Testing Time: 2.35 seconds
```

This script sends multiple test requests to the Flask server, including both normal and anomalous data, and logs the responses for review.

## File Descriptions

### 1. `anomaly.py`

**Purpose:** Generates synthetic network traffic data, including both normal and anomalous records.

**Key Functions:**

- **Data Generation:** Utilizes the `Faker` library to create realistic network traffic patterns.
- **Data Saving:** Exports the generated data to `network_traffic.csv`.

**Note:** Ensure the file is correctly named as `anomaly.py` to reflect its purpose accurately.

### 2. `training.py`

**Purpose:** Preprocesses the generated data and trains the Isolation Forest model for anomaly detection.

**Key Functions:**

- **Data Preprocessing:** Handles missing values by filling them with the median of each column.
- **Model Training:** Trains the Isolation Forest model using the preprocessed data.
- **Model Saving:** Saves both the preprocessor and trained model as `.pkl` files for later use by the Flask server.

### 3. `flask_server.py`

**Purpose:** Hosts the anomaly detection model and provides a RESTful API endpoint for predictions.

**Key Features:**

- **Endpoint `/predict`:** Accepts POST requests with network traffic data and returns predictions along with AI-generated elaborations.
- **AI Integration:** Communicates with the Ollama AI service to generate detailed explanations and remediation steps for detected anomalies.
- **Logging:** Records all incoming requests, predictions, and elaborations to `flask_server.log` for monitoring and debugging.

### 4. `Anomaly_test.py`

**Purpose:** Automates the testing of the Flask server by sending multiple requests and logging the responses.

**Key Features:**

- **Concurrent Requests:** Uses `ThreadPoolExecutor` to send multiple requests simultaneously.
- **Diverse Test Cases:** Includes both normal and anomalous data to validate the system's accuracy.
- **Logging:** Captures detailed logs of each test case, including request data and server responses, in `batch_test.log`.

## Logging

- **Flask Server Logs (`flask_server.log`):** Contains detailed logs of all requests, predictions, and AI elaborations for monitoring and troubleshooting.
  
  **Sample Log Entry:**
  
  ```
  2024-10-17 20:31:08,973 INFO:Received data: [{'source_ip': '192.168.5.161', 'destination_ip': '10.0.0.51', 'bytes': 4000, 'packets': 40, 'unique_dest_ips': 3, 'total_bytes': 12000, 'packet_rate': 8.0}]
  2024-10-17 20:31:08,973 INFO:Predictions: ['normal']
  ```

- **Batch Testing Logs (`batch_test.log`):** Records the outcomes of each test case sent by `Anomaly_test.py`, including successes and failures.
  
  **Sample Log Entry:**
  
  ```
  2024-10-17 20:31:20,627 INFO:Elaboration for 192.168.5.162: Based on the provided network traffic data, I would consider this traffic pattern as potentially anomalous due to the following factors:
  ...
  ```

## Troubleshooting

### 1. Typographical Errors

N/A anymore...

### 2. Connection Issues with Ollama

- **Symptom:** Flask server cannot communicate with Ollama server, resulting in connection errors.
  
  **Solutions:**
  
  - **Ensure Ollama is Running:** Verify that the Ollama server is active and listening on `http://localhost:11434/api/chat`.
  - **Check `OLLAMA_API_URL`:** Confirm that the Flask server is configured to connect to the correct URL (`http://localhost:11434/api/chat`) instead of an incorrect IP address.
  - **Firewall Settings:** Ensure that your firewall allows traffic on port `11434`.
  - **Test Connection Separately:** Use the provided test scripts or tools like Postman to verify connectivity between the Flask server and Ollama.

### 3. JSON Parsing Errors

- **Symptom:** Errors related to JSON decoding when processing responses.
  
  **Solutions:**
  
  - **Ensure Consistent Response Formats:** Align the Flask server's response handling with the successful test scripts that handle multi-line JSON responses.
  - **Update `elaborate_assessment` Function:** Modify the function to correctly parse and concatenate multi-line JSON responses from Ollama.

## Contributing

Contributions are welcome! If you'd like to enhance the Anomaly Detection System, please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- **OpenAI:** For providing the foundational AI models.
- **Flask Community:** For creating and maintaining the Flask framework.
- **Ollama:** For their robust AI services that enhance the anomaly detection capabilities.
- **Python Libraries:** Special thanks to `requests`, `joblib`, `pandas`, `numpy`, `scikit-learn`, `Faker`, and `waitress` for their invaluable contributions.

---

*Stay safe and happy coding! If you have any questions or need further assistance, feel free to reach out. I'm here to help! 😊❤️🚀*

```