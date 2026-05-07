"""
Kalshi Multi-Strategy AI Trading Bot
Prediction market auto-trader with multi-category strategies,
AI chat, and circular buffer memory.

Strategies: Weather, Politics, Economics, Sports, Market Making, Crypto
"""

__version__ = "2.1.0"
__author__ = "Wayne + Super Z"

from .circular_buffer import CircularBuffer
from .ai_chat import AIChat
from .dashboard import Dashboard

__all__ = [
    "CircularBuffer",
    "AIChat",
    "Dashboard",
]