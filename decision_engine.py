import os
import json
from openai import OpenAI


class DecisionEngine:

    def __init__(self, api_key=None):

        key = api_key or os.environ.get(
            "OPENAI_API_KEY"
        )

        self.client = OpenAI(
            api_key=key
        )

    def simplified_analysis(
        self,
        symbol,
        market_data
    ):

        prices = market_data.get(
            "prices",
            []
        )

        if len(prices) < 2:

            return {
                "mode": "SIMPLIFIED",
                "signal": "HOLD",
                "confidence": 50,
                "risk": "MEDIUM",
                "outlook_30m": "NEUTRAL",
                "outlook_2h": "NEUTRAL",
                "outlook_5h": "NEUTRAL",
                "outlook_24h": "NEUTRAL",
                "summary": "Dados insuficientes."
            }

        first_price = prices[0]
        last_price = prices[-1]

        variation = (
            (last_price - first_price)
            / first_price
        ) * 100

        if variation >= 0.15:
            signal = "BUY"

        elif variation <= -0.15:
            signal = "SELL"

        else:
            signal = "HOLD"

        confidence = min(
            max(
                int(abs(variation) * 150),
                55
            ),
            85
        )

        if confidence >= 75:
            risk = "LOW"

        elif confidence >= 65:
            risk = "MEDIUM"

        else:
            risk = "HIGH"

        trend = (
            "BULLISH"
            if signal == "BUY"
            else "BEARISH"
            if signal == "SELL"
            else "NEUTRAL"
        )

        return {
            "mode": "SIMPLIFIED",
            "signal": signal,
            "confidence": confidence,
            "risk": risk,
            "outlook_30m": trend,
            "outlook_2h": trend,
            "outlook_5h": trend,
            "outlook_24h": trend,
            "summary": (
                f"Análise simplificada para {symbol}. "
                f"Variação detectada: {variation:.2f}%."
            )
        }

    def analyze_market(
        self,
        symbol,
        market_data
    ):

        return self.simplified_analysis(
            symbol,
            market_data
        )
