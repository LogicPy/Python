# DORB - Discord Operational Remote Backdoor

**Cross-platform remote administration tool for educational and research purposes**

## Features

### 🖥️ Cross-Platform Compatibility
- **Windows**: Full feature support with native Win32 API integration
- **Linux**: X11-based messagebox support, pynput keylogging
- **macOS**: Cocoa framework integration for native dialogs

### 🔧 Core Commands
- `!help` - Display available commands and system status
- `!info` - Show detailed system information
- `!screenshot` - Capture and upload screenshot to Imgur
- `!keylog start/stop` - Start/stop keylogging functionality
- `!keystrokes` - View captured keystrokes without stopping
- `!msgbox <message>` - Display messagebox on target system
- `!stop` - Stop all active operations

### 🏗️ Architecture

The refactored DORB uses a modular architecture:

```
PlatformDetector
├── Detects OS and available capabilities
├── Manages platform-specific imports
└── Provides capability flags

CommandHandler
├── Clean command registration system
├── Modular command functions
└── Easy extensibility for new commands

CrossPlatformMessageBox
├── Windows: ctypes + Win32 API
├── Linux: zenity/kdialog subprocess calls
└── macOS: osascript + Cocoa

KeyloggerManager
├── Thread-safe keylogging
├── Cross-platform pynput integration
└── Memory-efficient keystroke storage

ScreenshotManager
├── Imgur integration for remote access
├── Local fallback storage
└── Temporary file cleanup
```

## Installation

### Prerequisites
- Python 3.7+
- Discord bot token
- Imgur API credentials (optional, for screenshot uploads)

### Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Platform-specific setup:**

**Linux:**
```bash
# For messagebox support
sudo apt-get install zenity  # GNOME
# OR
sudo apt-get install kdialog  # KDE
```

**Windows:**
```bash
# Enhanced features (optional)
pip install pywin32
```

**macOS:**
```bash
# Enhanced features (optional)
pip install pyobjc-framework-Cocoa
```

3. **Configure credentials:**
Edit the `main()` function in `dorb_refactored.py`:
```python
DISCORD_TOKEN = "your_discord_bot_token"
IMGUR_CLIENT_ID = "your_imgur_client_id"
IMGUR_CLIENT_SECRET = "your_imgur_client_secret"
```

## Usage

1. **Run the bot:**
```bash
python dorb_refactored.py
```

2. **Send commands via Discord:**
- Use `!help` to see available commands
- All commands start with `!` prefix
- Some commands accept arguments (e.g., `!msgbox Hello World`)

## Adding New Commands

The modular architecture makes adding new commands simple:

```python
async def cmd_custom(self, args: str, message: discord.Message) -> str:
    """Custom command implementation"""
    # Your logic here
    return "Command executed successfully"

# Register in _register_commands():
self.commands['custom'] = self.cmd_custom
```

## Security Considerations

- **Educational Use Only**: This tool is designed for cybersecurity research and education
- **Consent Required**: Only use on systems where you have explicit permission
- **Token Security**: Keep Discord and Imgur tokens secure
- **Network Security**: All communications go through Discord's infrastructure

## Logging

The bot maintains comprehensive logs:
- Console output for real-time monitoring
- File logging (`dorb.log`) for persistent records
- Error tracking and debugging information

## Troubleshooting

### Common Issues

1. **Import Errors**: Install missing platform-specific dependencies
2. **Permission Denied**: Run with appropriate system permissions
3. **Discord Connection**: Check bot token and internet connectivity
4. **Linux MessageBox**: Install zenity or kdialog system packages

### Debug Mode

Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new features:
1. Maintain cross-platform compatibility
2. Add proper error handling
3. Update documentation
4. Test on multiple platforms
5. Follow the existing code style

## License

Educational and research use only. Users are responsible for compliance with applicable laws and regulations.

## Disclaimer

This tool is provided for educational and research purposes only. Users must obtain explicit consent before monitoring any system. The authors are not responsible for misuse of this software.