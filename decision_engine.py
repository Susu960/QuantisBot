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

    def analyze_market(
        self,
        symbol,
        market_data
    ):

        prompt = f"""
You are Quantis Analyst.

Analyze the asset using the provided market data.

ASSET:
{symbol}

MARKET DATA:
{json.dumps(market_data, indent=2)}

Rules:

- Be conservative.
- Avoid forcing trades.
- If confidence is low, return HOLD.
- Only return valid JSON.
- Confidence must be between 0 and 100.
- Risk must be LOW, MEDIUM or HIGH.
- Signal must be BUY, SELL or HOLD.

Response format:

{{
    "signal": "BUY",
    "confidence": 82,
    "risk": "LOW",
    "outlook_30m": "BULLISH",
    "outlook_2h": "BULLISH",
    "outlook_5h": "NEUTRAL",
    "outlook_24h": "BULLISH",
    "summary": "Short explanation for the user."
}}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional market analyst."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        try:

            return json.loads(content)

        except Exception:

            return {
                "signal": "HOLD",
                "confidence": 0,
                "risk": "HIGH",
                "outlook_30m": "NEUTRAL",
                "outlook_2h": "NEUTRAL",
                "outlook_5h": "NEUTRAL",
                "outlook_24h": "NEUTRAL",
                "summary": (
                    "Unable to generate analysis."
                )
            }
