import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.parse import urlparse, parse_qs, urlencode

# ...

def build_test_url(url, param, test_script):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query[param] = test_script
    query_string = urlencode(query, doseq=True)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{query_string}"

# In csrf_scanner:

    # ...

# Global set for visited URLs
visited_urls = set()

def is_vulnerable_to_xss(response):
    """
    Simple XSS vulnerability detection.
    Checks if a <script> tag is reflected in the HTML response.
    """
    test_script = "<script>alert('XSS')</script>"
    if test_script in response.text:
        return True
    return False

def csrf_scanner(starting_url):
    to_visit_urls = [starting_url]
    visited_urls = set()
    test_parameters = ["q", "search", "comment", "id"]


    while to_visit_urls:
        url = to_visit_urls.pop(0)
        if url in visited_urls:
            continue

        visited_urls.add(url)
        print(f"Scanning URL: {url}")

        # Perform the scan
        
        try:
            # First, get the content of the page
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Process all links on the page
            for link in soup.find_all("a", href=True):
                href = link['href']
                next_url = urljoin(url, href)
                parsed_next_url = urlparse(next_url)
                if parsed_next_url.netloc == urlparse(starting_url).netloc:
                    to_visit_urls.append(next_url)

            # Then, test for XSS vulnerabilities
            test_script = "<script>alert('XSS')</script>"
            for param in test_parameters:
                test_url = build_test_url(url, param, test_script)
                #print ("\n" + test_url)
                xss_response = requests.get(test_url)
                if is_vulnerable_to_xss(xss_response):
                    print(f"Potential XSS vulnerability detected at {url} with parameter '{param}'")

        except requests.exceptions.RequestException as e:
            print(f"Error scanning {url}: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python csrf_scanner.py <url>")
        sys.exit(1)

    starting_url = sys.argv[1]
    parsed_starting_url = urlparse(starting_url)
    base_domain = parsed_starting_url.netloc  # Extract the base domain

    csrf_scanner(starting_url)

if __name__ == "__main__":
    main()
