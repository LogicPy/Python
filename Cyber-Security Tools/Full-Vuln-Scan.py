
# Full Vulnerability Scanner - Wayne's Web Scanner Plus (WWSP)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import threading
import time
from queue import Queue

# -----------------------------
# Configuration
# -----------------------------


# Thread-safe set for visited URLs
visited_urls = set()
visited_lock = threading.Lock()

# User-Agent Header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Vulnerability Scanner)'
}

# Logging Configuration
def setup_logging():
    logger = logging.getLogger('VulnScanner')
    logger.setLevel(logging.INFO)

    # File Handler
    file_handler = logging.FileHandler('vulnerability_scanner.log')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()

# Scanner Configuration
MAX_THREADS = 10
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 0.5  # Seconds

url_queue = Queue()

# Define payloads for different vulnerabilities
VULN_PAYLOADS = {
    'xss': [
        '<script>alert(1)</script>',
        '"><script>alert(1)</script>',
        "';alert(1);//",
        '"><img src=x onerror=alert(1)>',
    ],
    'sqli': [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT NULL, username, password FROM users --",
        "' OR '1'='1' --",
    ],
    'cmd_inj': [
        '|| ls',
        '; ls',
        '| cat /etc/passwd',
        '&& whoami',
    ]
}

# Vulnerability Types
VULN_TYPES = {
    '1': 'Broken Access Control (BAC)',
    '2': 'Cross-Site Scripting (XSS)',
    '3': 'SQL Injection (SQLi)',
    '4': 'Command Injection',
    '5': 'Full Scan'
}

# -----------------------------
# Helper Functions
# -----------------------------

def normalize_url(base, link):
    return urljoin(base, link)

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']

# -----------------------------
# Vulnerability Detection Functions
# -----------------------------

def scan_broken_access_control(url, session):
    """
    Scan for Broken Access Control vulnerabilities by manipulating form parameters.
    """
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"[*] Scanning for BAC: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_url = normalize_url(url, action)
                inputs = {}
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name')
                    input_type = input_tag.get('type', 'text')
                    if name:
                        # Identify potential parameters for BAC testing
                        if input_type in ['hidden', 'text', 'url'] or 'id' in name.lower():
                            inputs[name] = 'test'

                if inputs:
                    # Submit the form normally
                    submit_form(session, form_url, method, inputs, vuln_type='BAC')

                    # Manipulate parameters to test for BAC
                    manipulated_inputs = manipulate_parameters(inputs)
                    submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='BAC')

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error accessing {url} during BAC scan: {e}")

def scan_xss(url, session):
    """
    Scan for Cross-Site Scripting (XSS) vulnerabilities by injecting payloads into form parameters.
    """
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"[*] Scanning for XSS: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_url = normalize_url(url, action)
                inputs = {}
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name')
                    input_type = input_tag.get('type', 'text')
                    if name:
                        if input_type in ['text', 'url', 'search']:
                            inputs[name] = VULN_PAYLOADS['xss'][0]  # Initial payload

                for vuln_payload in VULN_PAYLOADS['xss']:
                    manipulated_inputs = inputs.copy()
                    for key in manipulated_inputs:
                        manipulated_inputs[key] = vuln_payload
                    submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='XSS')

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error accessing {url} during XSS scan: {e}")

def scan_sqli(url, session):
    """
    Scan for SQL Injection (SQLi) vulnerabilities by injecting SQL payloads into form parameters.
    """
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"[*] Scanning for SQLi: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_url = normalize_url(url, action)
                inputs = {}
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name')
                    input_type = input_tag.get('type', 'text')
                    if name:
                        if input_type in ['text', 'search']:
                            inputs[name] = VULN_PAYLOADS['sqli'][0]  # Initial payload

                for vuln_payload in VULN_PAYLOADS['sqli']:
                    manipulated_inputs = inputs.copy()
                    for key in manipulated_inputs:
                        manipulated_inputs[key] = vuln_payload
                    submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='SQLi')

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error accessing {url} during SQLi scan: {e}")

def scan_command_injection(url, session):
    """
    Scan for Command Injection vulnerabilities by injecting command payloads into form parameters.
    """
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"[*] Scanning for Command Injection: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_url = normalize_url(url, action)
                inputs = {}
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    name = input_tag.get('name')
                    input_type = input_tag.get('type', 'text')
                    if name:
                        if input_type in ['text', 'search']:
                            inputs[name] = VULN_PAYLOADS['cmd_inj'][0]  # Initial payload

                for vuln_payload in VULN_PAYLOADS['cmd_inj']:
                    manipulated_inputs = inputs.copy()
                    for key in manipulated_inputs:
                        manipulated_inputs[key] = vuln_payload
                    submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='Command Injection')

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error accessing {url} during Command Injection scan: {e}")

# -----------------------------
# Scanning and Submission Functions
# -----------------------------

def manipulate_parameters(params):
    """
    Manipulate parameters for vulnerability testing.
    """
    manipulated = params.copy()
    for key in manipulated:
        if 'role' in key.lower():
            manipulated[key] = 'admin'
        elif 'id' in key.lower():
            manipulated[key] = '1'
        # Add more manipulation strategies as needed
    return manipulated

def submit_form(session, url, method, data, manipulated=False, vuln_type=None):
    """
    Submit forms with either normal or manipulated data.
    """
    try:
        if method == 'post':
            response = session.post(url, data=data, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        else:
            response = session.get(url, params=data, headers=HEADERS, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            status = "Manipulated" if manipulated else "Normal"
            logger.info(f"[+] {status} form submitted to {url} with data {data}")

            if manipulated and vuln_type:
                analyze_response(response, vuln_type, url)

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error submitting form to {url}: {e}")

def analyze_response(response, vuln_type, url):
    """
    Analyze server responses to detect potential vulnerabilities.
    """
    content = response.text.lower()
    detected = False

    if vuln_type == 'BAC':
        if "admin" in content or "access denied" in content:
            detected = True
    elif vuln_type == 'XSS':
        if '<script>alert(1)</script>' in content or '<img src=x onerror=alert(1)>' in content:
            detected = True
    elif vuln_type == 'SQLi':
        if "syntax error" in content or "sql" in content:
            detected = True
    elif vuln_type == 'Command Injection':
        if "command not found" in content or "error" in content:
            detected = True

    if detected:
        logger.warning(f"[!] Potential {vuln_type} vulnerability detected at {url}")
        print(f"{logging.WARNING}: Potential {vuln_type} vulnerability detected at {url}")

# -----------------------------
# Crawling Function
# -----------------------------

def scan_url(url, session, selected_vulns):
    """
    Scan a single URL for selected vulnerabilities.
    """
    try:
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info(f"[+] Accessing: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and enqueue all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                normalized_href = normalize_url(url, href)
                parsed_href = urlparse(normalized_href)
                if is_valid_url(normalized_href):
                    with visited_lock:
                        if normalized_href not in visited_urls:
                            url_queue.put(normalized_href)

            # Extract and handle all forms
            for form in soup.find_all('form'):
                handle_form(url, form, session, selected_vulns)

    except requests.exceptions.RequestException as e:
        logger.error(f"[-] Error accessing {url}: {e}")

def handle_form(base_url, form, session, selected_vulns):
    """
    Handle form extraction and scanning based on selected vulnerabilities.
    """
    action = form.get('action')
    method = form.get('method', 'get').lower()
    form_url = normalize_url(base_url, action)
    inputs = {}
    for input_tag in form.find_all(['input', 'textarea', 'select']):
        name = input_tag.get('name')
        input_type = input_tag.get('type', 'text')
        if name:
            # Assign default test values
            if input_type in ['hidden', 'text', 'url', 'search']:
                inputs[name] = 'test'

    if inputs:
        # Submit the form normally
        submit_form(session, form_url, method, inputs, vuln_type=None)

        # Depending on selected vulnerabilities, perform manipulations
        if 'BAC' in selected_vulns:
            manipulated_inputs = manipulate_parameters(inputs)
            submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='BAC')

        if 'XSS' in selected_vulns:
            for payload in VULN_PAYLOADS['xss']:
                manipulated_inputs = inputs.copy()
                for key in manipulated_inputs:
                    manipulated_inputs[key] = payload
                submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='XSS')

        if 'SQLi' in selected_vulns:
            for payload in VULN_PAYLOADS['sqli']:
                manipulated_inputs = inputs.copy()
                for key in manipulated_inputs:
                    manipulated_inputs[key] = payload
                submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='SQLi')

        if 'Command Injection' in selected_vulns:
            for payload in VULN_PAYLOADS['cmd_inj']:
                manipulated_inputs = inputs.copy()
                for key in manipulated_inputs:
                    manipulated_inputs[key] = payload
                submit_form(session, form_url, method, manipulated_inputs, manipulated=True, vuln_type='Command Injection')

# -----------------------------
# Worker Function
# -----------------------------

def worker(session, selected_vulns):
    """
    Worker thread to process URLs from the queue.
    """
    while True:
        url = url_queue.get()
        if url is None:
            break
        with visited_lock:
            if url in visited_urls:
                url_queue.task_done()
                continue
            visited_urls.add(url)
        logger.info(f"Crawling URL: {url}")
        scan_url(url, session, selected_vulns)
        url_queue.task_done()
        time.sleep(DELAY_BETWEEN_REQUESTS)

# -----------------------------
# Summary Report Function
# -----------------------------

def generate_summary():
    """
    Generate a summary report of the scanning process.
    """
    with open('vulnerability_scanner.log', 'r') as log_file:
        lines = log_file.readlines()

    total_scanned = len([line for line in lines if "[+] Accessing" in line])
    vulnerabilities = len([line for line in lines if "[!] Potential" in line])

    summary = f"""
    ===== Vulnerability Scan Summary =====
    Total URLs Scanned: {total_scanned}
    Potential Vulnerabilities Found: {vulnerabilities}
    =======================================
    """
    print(summary)
    with open('vulnerability_summary.txt', 'w') as summary_file:
        summary_file.write(summary)


def login(session, login_url, credentials):
    try:
        # First, get the login page to retrieve CSRF token
        response = session.get(login_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Assume the CSRF token is in a hidden input named 'nonce'
        nonce = soup.find('input', {'name': 'nonce'})['value']
        credentials['nonce'] = nonce

        # Now, submit the login form with the CSRF token
        response = session.post(login_url, data=credentials, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200 and 'Dashboard' in response.text:
            logger.info("[+] Logged in successfully.")
            return True
        else:
            logger.warning("[-] Failed to log in.")
            return False
    except Exception as e:
        logger.error(f"[-] Error during login: {e}")
        return False


# -----------------------------
# Main Function
# -----------------------------

def main():
    """
    Main function to run the vulnerability scanner.
    """
    # Display Interactive Menu
    print("======================================")
    print("  Welcome to the Vulnerability Scanner ")
    print("======================================")
    print("Select the type of vulnerabilities to scan for:")
    for key, value in VULN_TYPES.items():
        print(f"{key}. {value}")
    print("0. Exit")

    choice = input("Enter your choice (e.g., 1,2,5): ").strip()

    if choice == '0':
        print("Exiting the scanner. Goodbye!")
        return

    selected_vulns = []
    choices = choice.split(',')

    for c in choices:
        c = c.strip()
        if c in VULN_TYPES:
            if VULN_TYPES[c] == 'Full Scan':
                selected_vulns = ['BAC', 'XSS', 'SQLi', 'Command Injection']
                break
            else:
                vuln_key = VULN_TYPES[c].split(' (')[0] if '(' in VULN_TYPES[c] else VULN_TYPES[c]
                selected_vulns.append(vuln_key)

    if not selected_vulns:
        print("No valid choices selected. Exiting.")
        return

    print(f"Selected Vulnerabilities: {', '.join(selected_vulns)}")
    root_url = input("Enter the root URL to scan (e.g., http://localhost:3000): ").strip()
    if not is_valid_url(root_url):
        print("Invalid URL format. Please ensure it starts with http:// or https://")
        return

    # Initialize session
    session = requests.Session()


    # Example credentials dictionary for WordPress
    credentials = {
        'log': 'your_username',       # Replace with your actual username
        'pwd': 'your_password',       # Replace with your actual password
        'wp-submit': 'Log In',
        'redirect_to': 'http://localhost:3000/wp-admin/',
        'testcookie': '1'
    }

    # Define the login URL
    login_url = 'http://localhost:3000/wp-login.php'



    # Checkpoint

    # Attempt to log in
    #if login(session, login_url, credentials):
     #   print("[+] Logged in successfully. Starting scan...")
    #else:
     #   print("[-] Login failed. Exiting scanner.")
     #   return



    # Enqueue the root URL
    url_queue.put(root_url)

    # Start worker threads
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=worker, args=(session, selected_vulns))
        t.daemon = True
        t.start()
        threads.append(t)

    # Wait until all URLs are processed
    url_queue.join()

    # Stop workers
    for _ in range(MAX_THREADS):
        url_queue.put(None)
    for t in threads:
        t.join()

    # Generate summary report
    generate_summary()
    print("Scanning completed. Check 'vulnerability_scanner.log' and 'vulnerability_summary.txt' for details.")

if __name__ == "__main__":
    main()
