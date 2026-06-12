from flask import Flask, jsonify, request
import os
import logging

from dotenv import load_dotenv

from decision_engine import DecisionEngine
from market_data import MarketData

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantis-analyst")

app = Flask(__name__)

market = MarketData()
engine = DecisionEngine()


@app.route("/", methods=["GET"])
def health_check():

    return jsonify({
        "status": "running",
        "service": "Quantis Analyst"
    })


@app.route("/status", methods=["GET"])
def status():

    return jsonify({
        "bot": "online",
        "ai": "connected",
        "market_data": "connected"
    })


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json() or {}

        command = data.get(
            "command",
            ""
        ).strip()

        if not command:

            return jsonify({
                "success": False,
                "error": "Command not provided"
            }), 400

        symbol = extract_symbol(command)

        if not symbol:

            return jsonify({
                "success": False,
                "error": "Unsupported asset"
            }), 400

        market_data = market.get_market_snapshot(
            symbol
        )

        if not market_data.get("success"):

            return jsonify({
                "success": False,
                "error": market_data.get("error")
            }), 500

        analysis = engine.analyze_market(
            symbol,
            market_data
        )

        return jsonify({
            "success": True,
            "asset": symbol,
            "market_data": market_data,
            "analysis": analysis
        })

    except Exception as e:

        logger.exception(e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/market", methods=["POST"])
def market_overview():

    try:

        symbols = market.get_supported_symbols()

        results = []

        for symbol in symbols:

            snapshot = market.get_market_snapshot(
                symbol
            )

            if not snapshot.get("success"):
                continue

            analysis = engine.analyze_market(
                symbol,
                snapshot
            )

            results.append({
                "asset": symbol,
                "analysis": analysis
            })

        results.sort(
            key=lambda x: x["analysis"].get(
                "confidence",
                0
            ),
            reverse=True
        )

        return jsonify({
            "success": True,
            "top_signals": results[:3]
        })

    except Exception as e:

        logger.exception(e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def extract_symbol(command):

    text = command.upper()

    aliases = {
        "OURO": "XAU/USD",
        "GOLD": "XAU/USD",
        "BITCOIN": "BTC/USD",
        "BTC": "BTC/USD",
        "ETHEREUM": "ETH/USD",
        "ETH": "ETH/USD",

        "EUR/USD": "EUR/USD",
        "GBP/USD": "GBP/USD",
        "USD/JPY": "USD/JPY",
        "USD/CHF": "USD/CHF",
        "AUD/USD": "AUD/USD",
        "USD/CAD": "USD/CAD",
        "NZD/USD": "NZD/USD",
        "EUR/GBP": "EUR/GBP",
        "EUR/JPY": "EUR/JPY",
        "GBP/JPY": "GBP/JPY",
        "XAU/USD": "XAU/USD",
        "BTC/USD": "BTC/USD",
        "ETH/USD": "ETH/USD"
    }

    for key, value in aliases.items():

        if key in text:

            return value

    return None


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
