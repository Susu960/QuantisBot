import json
import websocket
import logging

logger = logging.getLogger("deriv-client")

class DerivClient:
    def __init__(self, token):
        self.token = token
        self.ws = None
        self.url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

    def connect(self):
        try:
            self.ws = websocket.create_connection(self.url)
            self.ws.send(json.dumps({"authorize": self.token}))
            response = json.loads(self.ws.recv())
            return "error" not in response
        except:
            return False

    def buy(self, symbol, amount, contract_type):
        trade_data = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type.upper(),
                "currency": "USD",
                "duration": 1,
                "duration_unit": "m",
                "symbol": symbol
            }
        }
        self.ws.send(json.dumps(trade_data))
        return json.loads(self.ws.recv())

    def close(self):
        if self.ws: self.ws.close()
