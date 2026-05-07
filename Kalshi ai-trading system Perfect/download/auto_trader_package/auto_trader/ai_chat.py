"""
AI Chat Module — Conversational interface with circular buffer memory.

Provides a chat system where the user can:
- Ask about recent trades, signals, and performance
- Give feedback on wins/losses ("Nice win!", "Almost had that one!")
- Get explanations of the bot's reasoning
- Discuss strategy adjustments

All conversation and trade context is stored in a circular buffer for
finite memory that rolls over when full.
"""

import os
from typing import Dict, List, Optional

from .circular_buffer import CircularBuffer


class AIChat:
    """AI-powered chat system with rolling memory context."""

    # Sentiment keywords for simple user message classification
    POSITIVE_KEYWORDS = {
        "nice", "great", "awesome", "brilliant", "amazing", "love",
        "winner", "wins", "profit", "good", "excellent", "thanks",
        "beautiful", "magnificent", "superb", "fantastic", "wow",
    }
    NEGATIVE_KEYWORDS = {
        "loss", "bad", "wrong", "missed", "almost", "close", "dang",
        "unfortunate", "ugh", "fail", "failed", "rough", "tough",
    }
    QUESTION_KEYWORDS = {
        "why", "how", "what", "when", "which", "where", "explain",
        "tell", "show", "status", "performance", "stats", "how's",
    }

    def __init__(
        self,
        buffer: CircularBuffer,
        openrouter_api_key: str = "",
        model: str = "z-ai/glm-5.1",
        memory_capacity: int = 500,
    ):
        self.buffer = buffer
        self.openrouter_api_key = openrouter_api_key or os.getenv(
            "OPENROUTER_API_KEY", ""
        )
        self.model = model

        # Track conversation state
        self._last_user_sentiment: str = "neutral"

    # ── Public API ──────────────────────────────────────────────

    def send(self, user_message: str) -> str:
        """Process a user chat message and return the bot's response.

        This is the main entry point. It:
        1. Classifies user sentiment
        2. Logs the message to the circular buffer
        3. Builds context from recent buffer entries
        4. Calls the AI to generate a contextual response
        5. Logs the bot's response
        """
        sentiment = self._classify_sentiment(user_message)
        self._last_user_sentiment = sentiment

        # Log user message
        self.buffer.append_chat(
            speaker="user",
            message=user_message,
            sentiment=sentiment,
        )

        # Build context for AI
        context = self._build_context(user_message, sentiment)

        # Generate response
        response = self._query_ai(context, user_message, sentiment)

        # Log bot response
        self.buffer.append_chat(
            speaker="bot",
            message=response,
            sentiment="response",
        )

        return response

    def get_chat_history(self, n: int = 50) -> List[Dict]:
        """Return recent chat messages."""
        return self.buffer.recent_chat(n=n)

    def on_trade_result(self, ticker: str, direction: str, outcome: str,
                        pnl: float, confidence: float, reason: str = "",
                        category: str = "crypto") -> None:
        """Called by the bot when a trade completes. Logs to buffer.

        The AI chat can later reference this trade when the user asks.
        """
        self.buffer.append_trade(
            ticker=ticker,
            direction=direction,
            outcome=outcome,
            pnl=pnl,
            confidence=confidence,
            reason=reason,
            category=category,
        )

        # Auto-observation for big wins or losses
        if pnl >= 50:
            self.buffer.append_observation(
                f"Big win on {ticker} ({direction}): +${pnl:.2f}",
                category=category,
                data={"pnl": pnl, "confidence": confidence},
            )
        elif pnl <= -25:
            self.buffer.append_observation(
                f"Notable loss on {ticker} ({direction}): -${abs(pnl):.2f}",
                category=category,
                data={"pnl": pnl, "confidence": confidence},
            )

    def on_signal(self, ticker: str, direction: str, strength: float,
                  confidence: float, recommendation: str, reason: str = "",
                  category: str = "crypto") -> None:
        """Called by the bot when a signal is generated."""
        self.buffer.append_signal(
            ticker=ticker,
            direction=direction,
            strength=strength,
            confidence=confidence,
            recommendation=recommendation,
            reason=reason,
            category=category,
        )

    # ── Sentiment Classification ────────────────────────────────

    def _classify_sentiment(self, message: str) -> str:
        """Classify user message sentiment as positive/negative/neutral/question."""
        lower = message.lower().strip()

        # Check for questions first
        if any(kw in lower for kw in self.QUESTION_KEYWORDS):
            if any(kw in lower for kw in self.POSITIVE_KEYWORDS):
                return "positive_question"
            if any(kw in lower for kw in self.NEGATIVE_KEYWORDS):
                return "negative_question"
            return "question"

        pos_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in lower)
        neg_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    # ── Context Building ────────────────────────────────────────

    def _build_context(self, user_message: str, sentiment: str) -> str:
        """Build a rich context string for the AI prompt."""
        parts = []

        # 1. Recent performance summary
        parts.append("=== RECENT PERFORMANCE ===")
        parts.append(self.buffer.build_trade_summary())

        # 2. Category breakdown
        breakdown = self.buffer.category_breakdown()
        if breakdown:
            parts.append("\n=== CATEGORY BREAKDOWN ===")
            for cat, stats in breakdown.items():
                parts.append(
                    f"  {cat}: {stats['wins']}/{stats['total']} "
                    f"({stats['win_rate']:.1%}), PnL: ${stats['total_pnl']:.2f}"
                )

        # 3. Recent activity (last 10 entries)
        parts.append("\n=== RECENT ACTIVITY ===")
        parts.append(self.buffer.build_chat_context(last_n=10))

        # 4. Last 5 trades detail
        recent_trades = self.buffer.recent_trades(n=5)
        if recent_trades:
            parts.append("\n=== LAST 5 TRADES ===")
            for t in recent_trades:
                parts.append(
                    f"  {t.get('ticker')} {t.get('direction')} → "
                    f"{t.get('outcome')} | PnL: ${t.get('pnl', 0):.2f} | "
                    f"Conf: {t.get('confidence', 0):.0%} | "
                    f"Cat: {t.get('category', '?')} | Reason: {t.get('reason', 'N/A')}"
                )

        # 5. Last 5 signals
        recent_signals = self.buffer.recent_signals(n=5)
        if recent_signals:
            parts.append("\n=== LAST 5 SIGNALS ===")
            for s in recent_signals:
                parts.append(
                    f"  {s.get('ticker')} {s.get('direction')} | "
                    f"Str: {s.get('strength', 0):.4f} | "
                    f"Conf: {s.get('confidence', 0):.0%} | "
                    f"Rec: {s.get('recommendation', '?')} | "
                    f"Cat: {s.get('category', '?')}"
                )

        return "\n".join(parts)

    # ── AI Query ─────────────────────────────────────────────────

    def _query_ai(self, context: str, user_message: str,
                  sentiment: str) -> str:
        """Call OpenRouter API to generate a contextual response."""
        system_prompt = self._build_system_prompt(sentiment)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nUser says: {user_message}"},
        ]

        try:
            return self._call_openrouter(messages)
        except Exception as e:
            # Fallback to local response if API fails
            return self._local_response(user_message, sentiment, e)

    def _build_system_prompt(self, sentiment: str) -> str:
        """Build a context-aware system prompt based on user sentiment."""
        base = (
            "You are an AI trading assistant for a Kalshi multi-strategy bot. "
            "You have access to the bot's recent trades, signals, and performance data. "
            "You are conversational, insightful, and data-driven.\n\n"
            "Guidelines:\n"
            "- Reference specific trades, PnL, and signals from the context\n"
            "- Give actionable advice based on the data\n"
            "- Be encouraging on wins, constructive on losses\n"
            "- When the user praises a near-win, acknowledge the good analysis "
            "and discuss how the edge was almost captured\n"
            "- Keep responses concise (2-4 paragraphs max)\n"
            "- Use dollars and percentages for numbers\n"
        )

        if sentiment == "positive":
            base += (
                "\nThe user is in a positive mood! Match their energy — "
                "celebrate wins and reinforce good strategy decisions."
            )
        elif sentiment in ("negative", "negative_question"):
            base += (
                "\nThe user seems frustrated. Be empathetic and constructive — "
                "focus on what can be learned and improved. Highlight any "
                "near-misses as positive signals of the strategy's edge."
            )
        elif sentiment in ("question", "positive_question"):
            base += (
                "\nThe user is asking a question. Give a thorough, data-backed "
                "answer referencing the specific trades and stats in context."
            )

        return base

    def _call_openrouter(self, messages: List[Dict[str, str]]) -> str:
        """Make the API call to OpenRouter."""
        import requests

        if not self.openrouter_api_key:
            raise ValueError("No OpenRouter API key configured")

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kalshi-trader.local",
            "X-Title": "Kalshi AI Trader Chat",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"].strip()

    def _local_response(self, user_message: str, sentiment: str,
                        error: Exception) -> str:
        """Fallback response when AI is unavailable."""
        stats = self.buffer.trade_stats()

        if sentiment in ("positive", "positive_question"):
            return (
                f"Thank you for the kind words! 🎉 Stats right now: "
                f"{stats['wins']}W/{stats['losses']}L, "
                f"win rate {stats['win_rate']:.1%}, "
                f"PnL ${stats['total_pnl']:.2f}. "
                f"(AI connection unavailable: {error})"
            )
        elif sentiment in ("negative", "negative_question"):
            return (
                f"I hear you — it's frustrating. Current stats: "
                f"{stats['wins']}W/{stats['losses']}L, "
                f"win rate {stats['win_rate']:.1%}, "
                f"PnL ${stats['total_pnl']:.2f}. "
                f"Let's review the recent trades and adjust. "
                f"(AI connection unavailable: {error})"
            )
        elif sentiment == "question":
            return (
                f"Here are the current stats: "
                f"{stats['wins']}W/{stats['losses']}L, "
                f"win rate {stats['win_rate']:.1%}, "
                f"PnL ${stats['total_pnl']:.2f}. "
                f"(AI connection unavailable for detailed analysis: {error})"
            )
        else:
            return (
                f"Current performance: "
                f"{stats['wins']}W/{stats['losses']}L, "
                f"win rate {stats['win_rate']:.1%}, "
                f"PnL ${stats['total_pnl']:.2f}. "
                f"(AI connection unavailable: {error})"
            )
