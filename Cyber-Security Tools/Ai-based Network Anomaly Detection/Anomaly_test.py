import requests
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
FLASK_API_URL = "http://10.0.0.45:5000/predict"  # Your Flask server endpoint
LOG_FILE = "batch_test.log"  # Log file to store responses
CONCURRENT_REQUESTS = 5  # Number of concurrent requests

# Setup Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Define Test Cases
TEST_CASES = [
    # Anomalous Traffic
    {
        "source_ip": "192.168.5.160",
        "destination_ip": "10.0.0.50",
        "bytes": 25000,
        "packets": 300,
        "unique_dest_ips": 40,
        "total_bytes": 1000000,
        "packet_rate": 200.0
    },
    # Normal Traffic
    {
        "source_ip": "192.168.5.161",
        "destination_ip": "10.0.0.51",
        "bytes": 4000,
        "packets": 40,
        "unique_dest_ips": 3,
        "total_bytes": 12000,
        "packet_rate": 8.0
    },
    # Additional Anomalous Traffic
    {
        "source_ip": "192.168.5.162",
        "destination_ip": "10.0.0.52",
        "bytes": 30000,
        "packets": 350,
        "unique_dest_ips": 50,
        "total_bytes": 1500000,
        "packet_rate": 250.0
    },
    # Additional Normal Traffic
    {
        "source_ip": "192.168.5.163",
        "destination_ip": "10.0.0.53",
        "bytes": 5000,
        "packets": 60,
        "unique_dest_ips": 4,
        "total_bytes": 20000,
        "packet_rate": 12.0
    },
    # ... Add more test cases as needed
]

def send_request(test_case, index):
    """
    Sends a POST request to the Flask server with the provided test case.
    
    Args:
        test_case (dict): The network traffic data.
        index (int): Identifier for the test case.
    
    Returns:
        dict: Contains test case index, response status, predictions, and elaborations.
    """
    try:
        response = requests.post(FLASK_API_URL, json=[test_case], headers={"Content-Type": "application/json"}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        logging.info(f"Test Case {index}: Success")
        logging.info(f"Request Data: {test_case}")
        logging.info(f"Response: {data}")
        
        return {
            "test_case": index,
            "status": "Success",
            "predictions": data.get("predictions"),
            "elaborations": data.get("elaborations")
        }
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Test Case {index}: Request Exception - {e}")
        return {
            "test_case": index,
            "status": "Failed",
            "error": str(e)
        }
    except json.JSONDecodeError as e:
        logging.error(f"Test Case {index}: JSON Decode Error - {e}")
        return {
            "test_case": index,
            "status": "Failed",
            "error": "Invalid JSON response"
        }

def main():
    """
    Main function to execute batch testing using ThreadPoolExecutor for concurrency.
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
        future_to_test = {executor.submit(send_request, test_case, idx): idx for idx, test_case in enumerate(TEST_CASES, 1)}
        
        for future in as_completed(future_to_test):
            test_idx = future_to_test[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Test Case {result['test_case']}: {result['status']}")
            except Exception as exc:
                logging.error(f"Test Case {test_idx}: Generated an exception: {exc}")
                results.append({
                    "test_case": test_idx,
                    "status": "Failed",
                    "error": str(exc)
                })
    
    # Optionally, process results further or generate a summary
    print("\nBatch Testing Completed. Check 'batch_test.log' for detailed logs.")

if __name__ == "__main__":
    start_time = time.time()
    print("Starting Batch Testing...\n")
    main()
    end_time = time.time()
    print(f"\nTotal Testing Time: {end_time - start_time:.2f} seconds")
