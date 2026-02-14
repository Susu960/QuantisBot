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

@app.route("/")
def root():
    return jsonify({"status": "running"})

@app.route("/status")
def get_status():
    return jsonify({"bot": "online" if bot_state["online"] else "offline"})

@app.route("/start", methods=["POST"])
def start_bot():
    if not deriv_token:
        logger.error("DERIV_API_TOKEN missing")
        return jsonify({"error": "DERIV_API_TOKEN não configurado"}), 500
    
    # Valida Conexão com Deriv
    client = DerivClient(deriv_token)
    if not client.connect():
        logger.error("Falha ao conectar na Deriv durante o startup")
        return jsonify({"error": "Falha ao conectar na Deriv"}), 500
    client.close()
    
    # Valida Conexão com OpenAI
    if not openai_key:
        logger.error("OPENAI_API_KEY missing")
        return jsonify({"error": "OPENAI_API_KEY não configurada"}), 500
    
    try:
        DecisionEngine(openai_key)
    except Exception as e:
        logger.error(f"Falha ao conectar na OpenAI: {e}")
        return jsonify({"error": f"Erro OpenAI: {str(e)}"}), 500

    bot_state["online"] = True
    logger.info("Deriv conectada")
    logger.info("OpenAI conectada")
    logger.info("Bot pronto para operar")
    return jsonify({"message": "Bot pronto para operar"})

@app.route("/stop", methods=["POST"])
def stop_bot():
    bot_state["online"] = False
    logger.info("Bot parado")
    return jsonify({"message": "Bot parado"})

@app.route("/trade", methods=["POST"])
def trade():
    from flask import request
    if not bot_state["online"]:
        return jsonify({"error": "Bot está offline. Inicie o bot primeiro."}), 400
    
    data = request.get_json()
    symbol = data.get("symbol", "frxEURUSD")
    action = data.get("action", "BUY")
    amount = data.get("amount", 1)
    
    contract_type = "CALL" if action.upper() == "BUY" else "PUT"
    
    logger.info(f"Executando trade: {action} {symbol} quant={amount}")
    
    client = DerivClient(deriv_token)
    if client.connect():
        response = client.buy(symbol, amount, contract_type)
        client.close()
        return jsonify({"status": "executado", "deriv_response": response})
    else:
        return jsonify({"status": "erro", "message": "Falha ao conectar na Deriv"}), 500

if __name__ == "__main__":
    # Render usa a variável de ambiente PORT (padrão 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
