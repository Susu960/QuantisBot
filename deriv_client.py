import json
import websocket
import logging
import ssl

logger = logging.getLogger("deriv-client")


class DerivClient:

    def __init__(self, token):

        self.token = token
        self.ws = None

        self.url = "wss://ws.derivws.com/websockets/v3?app_id=63261"

    def connect(self):

        try:

            self.ws = websocket.create_connection(
                self.url,
                sslopt={"cert_reqs": ssl.CERT_NONE}
            )

            auth_request = {
                "authorize": self.token
            }

            self.ws.send(json.dumps(auth_request))

            response = json.loads(self.ws.recv())

            logger.info(f"Deriv auth response: {response}")

            if "error" in response:

                logger.error(response["error"])

                return {
                    "deriv_error": response["error"]
                }

            return True

        except Exception as e:

            logger.error(f"Connection error: {str(e)}")

            return {
                "connection_error": str(e)
            }

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

        response = json.loads(self.ws.recv())

        logger.info(f"Trade response: {response}")

        return response

    def close(self):

        if self.ws:
            self.ws.close()
