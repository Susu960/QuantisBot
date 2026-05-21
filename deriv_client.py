import json
import websocket
import logging
import ssl
import requests

logger = logging.getLogger("deriv-client")


class DerivClient:

    def __init__(self, token):

        self.token = token
        self.ws = None

        self.app_id = "33jlLVvXXSH9iPFRywUjM"

        self.account_id = "SUA_CONTA_DERIV"

    def connect(self):

        try:

            response = requests.post(
                f"https://api.derivws.com/trading/v1/options/accounts/{self.account_id}/otp",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Deriv-App-ID": self.app_id
                }
            )

            data = response.json()

            logger.info(f"OTP response: {data}")

            if "errors" in data:

                return {
                    "otp_error": data["errors"]
                }

            ws_url = data["data"]["url"]

            self.ws = websocket.create_connection(
                ws_url,
                sslopt={"cert_reqs": ssl.CERT_NONE}
            )

            logger.info("Connected to websocket")

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
