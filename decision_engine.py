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
            "summary": (
                "Insufficient market data."
            )
        }

    first_price = prices[0]
    last_price = prices[-1]

    variation = (
        (last_price - first_price)
        / first_price
    ) * 100

    # Mais sensível que a versão anterior
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

    outlook = (
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
        "outlook_30m": outlook,
        "outlook_2h": outlook,
        "outlook_5h": outlook,
        "outlook_24h": outlook,
        "summary": (
            f"Simplified analysis detected "
            f"{outlook.lower()} momentum "
            f"with {confidence}% confidence."
        )
    }

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

Response format:

{{
"mode": "ADVANCED",
"signal": "BUY",
"confidence": 82,
"risk": "LOW",
"outlook_30m": "BULLISH",
"outlook_2h": "BULLISH",
"outlook_5h": "NEUTRAL",
"outlook_24h": "BULLISH",
"summary": "Short explanation."
}}
"""

    try:

        response = (
            self.client
            .chat
            .completions
            .create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional "
                            "market analyst."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        analysis = json.loads(
            content
        )

        analysis["mode"] = (
            "ADVANCED"
        )

        return analysis

    except Exception as e:

        print(
            f"OpenAI unavailable: {e}"
        )

        return self.simplified_analysis(
            symbol,
            market_data
    )
