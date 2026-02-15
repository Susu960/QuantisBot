fromlask import Flask, jsonify
import os
import fromrt logging
import json
import websocket
from deriv_client import DerivClient
from decision_engine import DecisionEngine
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trading-backend")

app = Flask(__name__)

# Simple state management
bot_state = {"online": False}

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})

@app.route("/status")
def get_status():
    return jsonify({"bot": "online" if bot_state["online"] else "offline"})

@app.route("/start", methods=["POST"])
def start_bot():
    # Load tokens inside the endpoint to ensure we use latest env vars
    token = os.environ.get("DERIV_API_TOKEN")
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OpenIA_Api_Key")

    if not token:
        logger.error("DERIV_API_TOKEN missing")
        return jsonify({"error": "DERIV_API_TOKEN not set"}), 500
    
    # Connection logic moved entirely here
    client = DerivClient(token)
    if not client.connect():
        logger.error("Failed to connect to Deriv")
        return jsonify({"error": "Failed to connect to Deriv"}), 500
    client.close()
    
    if not key:
        logger.error("OPENAI_API_KEY missing")
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500
    
    try:
        DecisionEngine(key)
    except Exception as e:
        logger.error(f"Failed to connect to OpenAI: {e}")
        return jsonify({"error": f"OpenAI error: {str(e)}"}), 500

    bot_state["online"] = True
    logger.info("Deriv is connected")
    logger.info("OpenAI is connected")
    logger.info("Bot is ready to trade")
    return jsonify({"message": "Bot is ready to trade"})

@app.route("/stop", methods=["POST"])
def stop_bot():
    bot_state["online"] = False
    logger.info("Bot stopped")
    return jsonify({"message": "Bot stopped"})

@app.route("/trade", methods=["POST"])
def trade():
    from flask import request
    if not bot_state["online"]:
        return jsonify({"error": "Bot is offline. Start the bot first."}), 400
    
    data = request.get_json()
    symbol = data.get("symbol", "frxEURUSD")
    action = data.get("action", "BUY")
    amount = data.get("amount", 1)
    
    contract_type = "CALL" if action.upper() == "BUY" else "PUT"
    
    logger.info(f"Executing trade: {action} {symbol} amount={amount}")
    
    client = DerivClient(deriv_token)
    if client.connect():
        response = client.buy(symbol, amount, contract_type)
        client.close()
        return jsonify({"status": "executed", "deriv_response": response})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to Deriv"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
