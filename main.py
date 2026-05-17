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
        }),
