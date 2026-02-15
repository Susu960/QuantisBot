import os
import json
from openai import OpenAI

class DecisionEngine:
    def __init__(self, api_key=None):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=key)

    def analyze_market(self, symbol, market_data):
        prompt = f"Analyze {symbol} data: {market_data}. Return JSON: {{\"signal\": \"buy|sell|hold\"}}"
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content.strip())
