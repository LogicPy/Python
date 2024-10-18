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
