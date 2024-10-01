import shodan
import requests
import logging
import time
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"),
        logging.StreamHandler()
    ]
)

# Constants
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')  # Ensure you have your Shodan API key set similarly
NVD_API_URL = 'https://services.nvd.nist.gov/rest/json/cves/1.0/'
NVD_API_KEY = os.getenv('NVD_API_KEY')  # Your newly obtained NVD API key

# Initialize Shodan API
api = shodan.Shodan(SHODAN_API_KEY)

def get_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def resolve_domain(target):
    try:
        ip = socket.gethostbyname(target)
        logging.info(f"Resolved domain {target} to IP {ip}")
        return ip
    except socket.gaierror as e:
        logging.error(f"Error resolving domain {target}: {e}")
        return None

def is_ip(target):
    try:
        socket.inet_aton(target)
        return True
    except socket.error:
        return False

def get_host_info(target):
    ip = None
    if is_ip(target):
        ip = target
    else:
        ip = resolve_domain(target)
    
    if not ip:
        logging.error(f"Could not resolve target: {target}")
        return None
    
    try:
        host = api.host(ip)
        return host
    except shodan.APIError as e:
        logging.error(f"Shodan API error for {ip}: {e}")
        return None

def extract_services(host_info):
    services = []
    for service in host_info.get('data', []):
        port = service.get('port')
        product = service.get('product') or service.get('banner') or 'Unknown'
        version = service.get('version') or 'Unknown'
        service_info = {
            'port': port,
            'product': product,
            'version': version
        }
        services.append(service_info)
    return services

def get_cve_for_service(product, version):
    if version == 'Unknown':
        keyword = f"{product}"
    else:
        keyword = f"{product} {version}"
    
    params = {
        'keyword': keyword,
        'resultsPerPage': 20
    }
    headers = {
        'apiKey': NVD_API_KEY
    }
    session = get_session()
    try:
        logging.debug(f"Querying NVD with keyword: {keyword}")
        response = session.get(NVD_API_URL, params=params, headers=headers)
        logging.info(f"Request URL: {response.url}")
        logging.info(f"Status Code: {response.status_code}")
        #logging.debug(f"Response Headers: {response.headers}")
        #logging.debug(f"Response Content: {response.text[:500]}")  # Print first 500 chars

        response.raise_for_status()

        data = response.json()
        return data.get('result', {}).get('CVE_Items', [])
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.JSONDecodeError as json_err:
        logging.error(f"JSON decode error: {json_err}")
        #logging.debug(f"Response Content: {response.text}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
    
    return []

# Cached version to reduce API calls
@lru_cache(maxsize=256)
def get_cve_for_service_cached(product, version):
    return get_cve_for_service(product, version)

def scan_target(target):
    host_info = get_host_info(target)
    if not host_info:
        return

    print(f"Scanning Target: {target}")
    services = extract_services(host_info)

    for service in services:
        product = service['product']
        version = service['version']
        port = service['port']
        print(f"\nService: {product} {version} on port {port}")
        
        cves = get_cve_for_service_cached(product, version)
        if cves:
            print(f"Found {len(cves)} CVEs:")
            for cve in cves:
                cve_id = cve['cve']['CVE_data_meta']['ID']
                description = cve['cve']['description']['description_data'][0]['value']
                # Extract severity if available
                severity = 'N/A'
                if 'impact' in cve:
                    if 'baseMetricV3' in cve['impact']:
                        severity = cve['impact']['baseMetricV3']['cvssV3']['baseSeverity']
                    elif 'baseMetricV2' in cve['impact']:
                        severity = cve['impact']['baseMetricV2']['severity']
                print(f" - {cve_id}: {description} [Severity: {severity}]")
                # Log the CVE being scanned
                logging.info(f"Scanned CVE: {cve_id}")
        else:
            print("No known CVEs found for this service.")
        
        time.sleep(1)  # Sleep to respect rate limits

if __name__ == "__main__":
    target = input("Domain/host (wayne.cool): ")  # Replace with your target domain or IP
    scan_target(target)
