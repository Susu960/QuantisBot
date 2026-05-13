from flask import Flask, jsonify, request
import os
import logging
from deriv_client import DerivClient
from decision_engine import DecisionEngine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading-backend")

app = Flask(__name__)

bot_state = {"online": False}

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})

@app.route("/status")
def get_status():

    return jsonify({
        "bot": "online" if bot_state["online"] else "offline",
        "ai": "connected",
        "broker": "connected",
        "mode": "monitoring"})

@app.route("/start", methods=["POST"])
def start_bot():

    token = os.environ.get("DERIV_API_TOKEN")
    key = os.environ.get("OPENAI_API_KEY")

    if not token:
        return jsonify({"error": "DERIV_API_TOKEN not set"}), 500

    if not key:
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500

    client = DerivClient(token)

    if not client.connect():
        return jsonify({"error": "Failed to connect to Deriv"}), 500

    client.close()

try:
    engine = DecisionEngine(key)
    test_analysis = engine.analyze_market(
    "frxEURUSD",
    {
    "price": 1.08,
    "trend": "bullish",
    "volume": "medium"
    }
    )
    logger.info(f"AI TEST RESPONSE: {test_analysis}")
except Exception as e:
    return jsonify({"error": str(e)}), 500
    
    bot_state["online"] = True

    return jsonify({
        "message": "Bot is ready",
        "ai": "connected",
        "status": "online"
    })

@app.route("/stop", methods=["POST"])
def stop_bot():
    bot_state["online"] = False
    return jsonify({"message": "Bot stopped"})

@app.route("/trade", methods=["POST"])
def trade():

    if not bot_state["online"]:
        return jsonify({"error": "Bot is offline"}), 400

    data = request.get_json()

    symbol = data.get("symbol", "frxEURUSD")
    amount = data.get("amount", 1)

    market_data = data.get("market_data", {})

    openai_key = os.environ.get("OPENAI_API_KEY")
    deriv_token = os.environ.get("DERIV_API_TOKEN")

    engine = DecisionEngine(openai_key)

    try:
        analysis = engine.analyze_market(symbol, market_data)
    except Exception as e:
        return jsonify({
            "status": "ai_error",
            "error": str(e)
        }), 500

    signal = analysis.get("signal", "HOLD").upper()
    confidence = analysis.get("confidence", 0)
    reason = analysis.get("reason", "No reason provided")

    if signal == "HOLD":
        return jsonify({
            "status": "hold",
            "signal": signal,
            "confidence": confidence,
            "reason": reason
        })

    contract_type = "CALL" if signal == "BUY" else "PUT"

    client = DerivClient(deriv_token)

    if not client.connect():
        return jsonify({
            "status": "connection_error"
        }), 500

    response = client.buy(symbol, amount, contract_type)

    client.close()

    return jsonify({
        "status": "executed",
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "deriv_response": response
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
