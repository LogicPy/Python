
# Broken Access Control Scanner - Wayne Kenney 2024

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import threading
import time
from queue import Queue

# Configuration
ROOT_URL = 'http://localhost:3000'  # Replace with your target URL
SINK_SERVER = 'http://localhost:8000'  # Sink Server URL
MAX_THREADS = 10
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 0.5  # Seconds

# Initialize logging
logging.basicConfig(
    filename='bac_scanner.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# User-Agent Header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Broken Access Control Scanner)'
}

# Thread-safe set for visited URLs
visited_urls = set()
visited_lock = threading.Lock()

# Queue for URLs to scan
url_queue = Queue()

def normalize_url(base, link):
    return urljoin(base, link)

from tqdm import tqdm

# Initialize tqdm progress bar
progress_bar = tqdm(total=1000)  # Set an appropriate total or make it dynamic

def crawl():
    while True:
        url = url_queue.get()
        if url is None:
            break
        with visited_lock:
            if url in visited_urls:
                url_queue.task_done()
                progress_bar.update(1)
                continue
            visited_urls.add(url)
        logging.info(f"Crawling URL: {url}")
        scan_url(url)
        url_queue.task_done()
        progress_bar.update(1)
        time.sleep(DELAY_BETWEEN_REQUESTS)


def scan_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logging.info(f"[+] Accessing: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and enqueue all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                normalized_href = normalize_url(url, href)
                parsed_href = urlparse(normalized_href)
                if parsed_href.scheme in ['http', 'https']:
                    with visited_lock:
                        if normalized_href not in visited_urls:
                            url_queue.put(normalized_href)

            # Extract and handle all forms
            for form in soup.find_all('form'):
                handle_form(url, form)

            # Additional BAC checks can be implemented here

    except requests.exceptions.RequestException as e:
        logging.error(f"[-] Error accessing {url}: {e}")

def handle_form(base_url, form):
    action = form.get('action')
    method = form.get('method', 'get').lower()
    form_url = normalize_url(base_url, action)
    inputs = {}
    for input_tag in form.find_all(['input', 'textarea', 'select']):
        name = input_tag.get('name')
        input_type = input_tag.get('type', 'text')
        if name:
            # Identify potential parameters for BAC testing
            if input_type in ['hidden', 'text', 'url'] or 'id' in name.lower():
                # Assign a test value; this can be enhanced based on parameter analysis
                inputs[name] = 'test'

    if inputs:
        # Attempt to submit the form normally
        submit_form(form_url, method, inputs)

        # Attempt to manipulate parameters for BAC testing
        manipulated_inputs = manipulate_parameters(inputs)
        submit_form(form_url, method, manipulated_inputs, manipulated=True)

def manipulate_parameters(params):
    manipulated = params.copy()
    for key in manipulated:
        # Example manipulation: Accessing admin endpoints
        if 'role' in key.lower():
            manipulated[key] = 'admin'
        elif 'id' in key.lower():
            manipulated[key] = '1'  # Attempt to access resource with ID 1
        # Add more manipulation strategies as needed
    return manipulated

def submit_form(url, method, data, manipulated=False):
    try:
        if method == 'post':
            response = requests.post(url, data=data, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        else:
            response = requests.get(url, params=data, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            status = "Manipulated" if manipulated else "Normal"
            logging.info(f"[+] {status} form submitted to {url} with data {data}")
            if manipulated:
                # Check for unusual responses that might indicate BAC issues
                analyze_response(url, response)
    except requests.exceptions.RequestException as e:
        logging.error(f"[-] Error submitting form to {url}: {e}")

from colorama import init, Fore, Style

# Initialize colorama
init()

def analyze_response(url, response):
    if "admin" in response.text.lower():
        warning_message = f"[!] Potential BAC vulnerability detected at {url}"
        logging.warning(warning_message)
        print(Fore.RED + warning_message + Style.RESET_ALL)
    # Add more conditions as needed

def generate_summary():
    with open('bac_scanner.log', 'r') as log_file:
        lines = log_file.readlines()
    
    total_scanned = len([line for line in lines if "[+] Accessing" in line])
    vulnerabilities = len([line for line in lines if "[!] Potential BAC vulnerability" in line])
    
    summary = f"""
    ===== Broken Access Control Scan Summary =====
    Total URLs Scanned: {total_scanned}
    Potential Vulnerabilities Found: {vulnerabilities}
    ==============================================
    """
    print(summary)
    with open('bac_summary.txt', 'w') as summary_file:
        summary_file.write(summary)


def main():
    # Enqueue the root URL
    url_queue.put(ROOT_URL)

    # Start worker threads
    threads = []
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=crawl)
        t.start()
        threads.append(t)

    # Wait until all URLs are processed
    url_queue.join()

    # Stop workers
    for _ in range(MAX_THREADS):
        url_queue.put(None)
    for t in threads:
        t.join()

    # Generate summary
    generate_summary()

    logging.info("[-] Broken Access Control scanning completed.")


if __name__ == "__main__":
    main()
