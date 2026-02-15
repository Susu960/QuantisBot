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
    return jsonify({"bot": "online" if bot_state["online"] else "offline"})

@app.route("/start", methods=["POST"])
def start_bot():
    token = os.environ.get("DERIV_API_TOKEN")
    key = os.environ.get("OPENAI_API_KEY")

    if not token:
        return jsonify({"error": "DERIV_API_TOKEN not set"}), 500

    client = DerivClient(token)
    if not client.connect():
        return jsonify({"error": "Failed to connect to Deriv"}), 500
    client.close()

    if not key:
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500

    try:
        DecisionEngine(key)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    bot_state["online"] = True
    return jsonify({"message": "Bot is ready to trade"})

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
    action = data.get("action", "BUY")
    amount = data.get("amount", 1)

    contract_type = "CALL" if action.upper() == "BUY" else "PUT"

    deriv_token = os.environ.get("DERIV_API_TOKEN")

    client = DerivClient(deriv_token)
    if client.connect():
        response = client.buy(symbol, amount, contract_type)
        client.close()
        return jsonify({"status": "executed", "deriv_response": response})
    else:
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
