import os
import json
from openai import OpenAI


class DecisionEngine:

    def __init__(self, api_key=None):

        key = api_key or os.environ.get("OPENAI_API_KEY")

        self.client = OpenAI(api_key=key)

    def analyze_market(self, symbol, market_data):

        prompt = f"""
You are an elite forex trading AI.

Analyze the forex market data carefully.

SYMBOL:
{symbol}

MARKET DATA:
{market_data}

Rules:
- Only take trades with decent probability.
- Avoid overtrading.
- If market conditions are unclear, return HOLD.
- Focus on safer entries.
- Return ONLY valid JSON.

Response format:
{{
    "signal": "BUY or SELL or HOLD",
    "confidence": 0-100,
    "reason": "short explanation"
}}
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional forex AI trading analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)
