"""
AI-Enhanced Market Analyzer using OpenRouter.

Uses an LLM to provide an additional signal layer on top of
the momentum detector. The AI analyzes recent price action,
market context, and provides a confidence-boosting or
confidence-reducing opinion.
"""

import json
import time
from typing import Optional, Dict, Any

import requests

from .config import OpenRouterConfig


class AIAnalyzer:
    """
    Optional AI-powered analysis layer.

    Uses OpenRouter to query an LLM about the current market
    conditions. The AI provides:
    1. Context about broader market trends
    2. Assessment of the momentum signal quality
    3. Risk warnings (e.g., upcoming events, low liquidity)

    The AI opinion is used as a MODIFIER on the momentum confidence,
    not as a standalone signal. It can boost confidence by up to 10%
    or reduce it by up to 20%.
    """

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or OpenRouterConfig()
        self.api_key = self.config.API_KEY
        self.api_url = self.config.API_URL
        self.model = self.config.MODEL

    def analyze_signal(self, symbol: str, momentum_data: Dict[str, Any],
                       kalshi_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get AI assessment of a momentum signal.

        Args:
            symbol: Crypto symbol
            momentum_data: Dict from MomentumSignal
            kalshi_data: Dict from find_15min_contracts

        Returns dict with:
            - ai_confidence: float 0-1
            - ai_direction: "UP", "DOWN", or "NEUTRAL"
            - risk_warning: str or None
            - reasoning: str
            - confidence_modifier: float (-0.20 to +0.10)
        """
        if not self.api_key:
            return None

        prompt = f"""You are a crypto trading analyst. Analyze this market data and provide a brief assessment.

CRYPTO: {symbol}
CURRENT PRICE: ${momentum_data.get('current_price', 'N/A')}
PRICE CHANGE: {momentum_data.get('price_change_pct', 0):.3f}%
MOMENTUM DIRECTION: {momentum_data.get('direction', 'N/A')}
MOMENTUM STRENGTH: {momentum_data.get('strength', 'N/A')}
DIRECTION CONSISTENCY: {momentum_data.get('direction_consistency', 0):.0%}
VOLATILITY: {momentum_data.get('volatility', 0):.4f}%
KALSHI UP PRICE: {kalshi_data.get('up_price', 'N/A')} cents
KALSHI DOWN PRICE: {kalshi_data.get('down_price', 'N/A')} cents
TIME REMAINING: {kalshi_data.get('time_remaining_sec', 'N/A')} seconds

Provide your analysis as JSON only:
{{
  "ai_direction": "UP" or "DOWN" or "NEUTRAL",
  "ai_confidence": 0.0 to 1.0,
  "confidence_modifier": -0.20 to +0.10,
  "risk_warning": "description of risk" or null,
  "reasoning": "1-2 sentence explanation"
}}"""

        try:
            resp = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://crypto-predictor.local",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a concise crypto analyst. Respond with valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 200,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not content:
                return None

            # Try to parse JSON from the response
            # Sometimes the AI wraps it in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            # Validate and clamp values
            result["confidence_modifier"] = max(-0.20, min(0.10,
                float(result.get("confidence_modifier", 0))))
            result["ai_confidence"] = max(0.0, min(1.0,
                float(result.get("ai_confidence", 0.5))))

            return result

        except Exception as e:
            print(f"[AIAnalyzer] Analysis failed: {e}")
            return None
