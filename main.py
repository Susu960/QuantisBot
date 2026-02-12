from fastapi import FastAPI, Request, HTTPException
import logging
import os
from deriv_client import DerivClient
from decision_engine import DecisionEngine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trading-backend")

app = FastAPI(title="Trading Bot Backend")

bot_state = {"online": False}
deriv_token = os.environ.get("DERIV_API_TOKEN")
openai_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OpenIA_Api_Key")

@app.get("/")
async def root():
    return {"message": "Trading Bot Backend is running", "endpoints": ["/status", "/start", "/stop", "/trade"]}

@app.get("/status")
async def get_status():
    return {"bot": "online" if bot_state["online"] else "offline"}

@app.post("/start")
async def start_bot():
    if not deriv_token:
        raise HTTPException(status_code=500, detail="DERIV_API_TOKEN not set")
    
    client = DerivClient(deriv_token)
    if not client.connect():
        raise HTTPException(status_code=500, detail="Failed to connect to Deriv")
    client.close()
    
    if not openai_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

    bot_state["online"] = True
    logger.info("Bot is ready to trade")
    return {"message": "Bot is ready to trade"}

@app.post("/trade")
async def trade(request: Request):
    if not bot_state["online"]:
        raise HTTPException(status_code=400, detail="Bot is offline. Start the bot first.")
    
    data = await request.json()
    symbol = data.get("symbol", "frxEURUSD")
    action = data.get("action", "BUY")
    amount = data.get("amount", 1)
    
    contract_type = "CALL" if action.upper() == "BUY" else "PUT"
    client = DerivClient(deriv_token)
    if client.connect():
        response = client.buy(symbol, amount, contract_type)
        client.close()
        return {"status": "executed", "deriv_response": response}
    return {"status": "error", "message": "Failed to connect to Deriv"}
