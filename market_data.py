import os
import requests


class MarketData:

    def __init__(self):

        self.api_key = os.environ.get(
            "TWELVE_DATA_API_KEY"
        )

        self.base_url = (
            "https://api.twelvedata.com"
        )

    def get_price(self, symbol):

        try:

            response = requests.get(
                f"{self.base_url}/price",
                params={
                    "symbol": symbol,
                    "apikey": self.api_key
                },
                timeout=10
            )

            data = response.json()

            if "price" not in data:

                return {
                    "success": False,
                    "error": data
                }

            return {
                "success": True,
                "symbol": symbol,
                "price": float(data["price"])
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def get_multiple_prices(self, symbols):

        results = []

        for symbol in symbols:

            results.append(
                self.get_price(symbol)
            )

        return results
