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

bot_state = {
    "online": False,
    "ai": "connected",
    "broker": "connected",
    "mode": "monitoring"
}


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})


@app.route("/status", methods=["GET"])
def get_status():

    return jsonify({
        "bot": "online" if bot_state["online"] else "offline",
        "ai": bot_state["ai"],
        "broker": bot_state["broker"],
        "mode": bot_state["mode"]
    })


@app.route("/start", methods=["GET", "POST"])
def start_bot():

    token = os.environ.get("DERIV_API_TOKEN")
    key = os.environ.get("OPENAI_API_KEY")

    if not token:
        return jsonify({
            "error": "DERIV_API_TOKEN not set"
        }), 500

    if not key:
        return jsonify({
            "error": "OPENAI_API_KEY not set"
        }), 500

    client = DerivClient(token)

    connection = client.connect()

    if connection is not True:

        return jsonify({
            "error": connection
        }), 500

    client.close()

    try:
        DecisionEngine(key)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    bot_state["online"] = True

    return jsonify({
        "message": "Bot is ready to trade",
        "status": "online"
    })


@app.route("/stop", methods=["POST"])
def stop_bot():

    bot_state["online"] = False

    return jsonify({
        "message": "Bot stopped"
    })


@app.route("/trade", methods=["POST"])
def trade():

    if not bot_state["online"]:

        return jsonify({
            "error": "Bot is offline"
        }), 400

    data = request.get_json()

    symbol = data.get("symbol", "frxEURUSD")
    amount = data.get("amount", 1)

    market_data = data.get("market_data", {})

    engine = DecisionEngine()

    analysis = engine.analyze_market(
        symbol,
        market_data
    )

    signal = analysis.get("signal", "HOLD")
    confidence = analysis.get("confidence", 0)
    reason = analysis.get("reason", "No reason")

    if signal == "HOLD":

        return jsonify({
            "status": "hold",
            "confidence": confidence,
            "reason": reason
        })

    contract_type = "CALL" if signal == "BUY" else "PUT"

    deriv_token = os.environ.get("DERIV_API_TOKEN")

    client = DerivClient(deriv_token)

    connection = client.connect()

    if connection is not True:

        return jsonify({
            "error": connection
        }), 500

    response = client.buy(
        symbol,
        amount,
        contract_type
    )

    client.close()

    return jsonify({
        "status": "executed",
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "symbol": symbol,
        "amount": amount,
        "deriv_response": response
    })


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
        )
