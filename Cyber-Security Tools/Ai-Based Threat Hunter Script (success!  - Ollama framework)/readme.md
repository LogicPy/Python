![ai-scanner](images/threat-hunt.png)

# AI-Based Threat Hunting Tool

## Overview

This tool leverages an AI model to perform threat hunting by identifying common web application vulnerabilities such as XSS, SQL Injection, and more.

## Features

- **HTML Validation:** Uses W3C Validator API to validate target URLs.
- **AI Threat Analysis:** Integrates with a Llama2 model to analyze potential vulnerabilities.
- **Manual Exploit Testing:** Allows users to test predefined vulnerabilities.
- **Logging:** Logs AI responses for future reference and analysis.

## Setup Instructions

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/logicpy/ai-threat-hunting.git
    cd ai-threat-hunting
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure API Keys:**
    - Update `config.yaml` with your `MemoryClient` API key and other configurations.

4. **Run the Script:**
    ```bash
    python threat_hunting.py
    ```

## Usage

1. **Start the AI Interaction:**
    - Enter your prompt and optionally provide a target URL for HTML validation and vulnerability testing.

2. **Analyze Responses:**
    - The AI will provide detailed reports on detected vulnerabilities.

## Troubleshooting

- **JSON Decode Errors:** Ensure the AI model's API endpoint returns properly formatted JSON responses.
- **Authentication Issues:** Verify that API keys and session configurations are correctly set.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
