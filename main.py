from flask import Flask, jsonify
import os
import threading
import logging
import json
import websocket
from deriv_client import DerivClient
from decision_engine import DecisionEngine
from dotenv import load_dotenv

load_dotenv()

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trading-backend")

app = Flask(__name__)

# Gerenciamento de estado do bot
bot_state = {"online": False}
deriv_token = os.environ.get("DERIV_API_TOKEN")
openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OpenIA_Api_Key")

@app.route("/", methods=["GET"])
def health_check():
    """Rota de verificação para o Render detectar que o servidor está vivo"""
    return jsonify({"status": "running"})

@app.route("/status")
def get_status():
    return jsonify({"bot": "online" if bot_state["online"] else "offline"})

@app.route("/start", methods=["POST"])
def start_bot():
    if not deriv_token:
        logger.error("DERIV_API_TOKEN missing")
        return jsonify({"error": "DERIV_API_TOKEN not set"}), 500
    
    # Valida Conexão com Deriv
    client = DerivClient(deriv_token)
    if not client.connect():
        logger.error("Failed to connect to Deriv during startup")
        return jsonify({"error": "Failed to connect to Deriv"}), 500
    client.close()
    
    # Valida Conexão com OpenAI
    if not openai_key:
        logger.error("OPENAI_API_KEY missing")
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500
    
    try:
        DecisionEngine(openai_key)
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
    # O Render exige que o servidor escute na porta definida pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
