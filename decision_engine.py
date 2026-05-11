import os
import json
from openai import OpenAI

class DecisionEngine:
    def __init__(self, api_key=None):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=key)

    def analyze_market(self, symbol, market_data):

        prompt = f"""
You are an advanced forex trading AI.

Analyze the following market data for {symbol}.

Market data:
{market_data}

Your job:
- Decide if the bot should BUY, SELL, or HOLD.
- Avoid risky trades.
- Avoid overtrading.
- Protect the trading capital.
- Prioritize high quality entries while maintaining healthy trading opportunities.

Return ONLY valid JSON.

Example:
{{
  "signal": "BUY",
  "confidence": 87,
  "reason": "Strong bullish momentum confirmed"
}}

Or:

{{
  "signal": "SELL",
  "confidence": 79,
  "reason": "Bearish continuation detected"
}}

Or:

{{
  "signal": "HOLD",
  "confidence": 91,
  "reason": "High volatility and weak confirmation"
}}
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional forex trading analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)
