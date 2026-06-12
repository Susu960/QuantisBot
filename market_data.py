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

        self.supported_symbols = {
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
            "ETH/USD": "ETH/USD",
            "OURO": "XAU/USD",
            "GOLD": "XAU/USD",
            "BITCOIN": "BTC/USD",
            "BTC": "BTC/USD",
            "ETHEREUM": "ETH/USD",
            "ETH": "ETH/USD"
        }

    def normalize_symbol(self, symbol):

        symbol = symbol.upper().strip()

        return self.supported_symbols.get(
            symbol,
            symbol
        )

    def get_supported_symbols(self):

        return [
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "USD/CHF",
            "AUD/USD",
            "USD/CAD",
            "NZD/USD",
            "EUR/GBP",
            "EUR/JPY",
            "GBP/JPY",
            "XAU/USD",
            "BTC/USD",
            "ETH/USD"
        ]

    def get_market_snapshot(self, symbol):

        try:

            symbol = self.normalize_symbol(
                symbol
            )

            response = requests.get(
                f"{self.base_url}/time_series",
                params={
                    "symbol": symbol,
                    "interval": "1h",
                    "outputsize": 24,
                    "apikey": self.api_key
                },
                timeout=15
            )

            data = response.json()

            if "values" not in data:

                return {
                    "success": False,
                    "error": data
                }

            candles = data["values"]

            closes = []

            for candle in reversed(candles):

                closes.append(
                    float(candle["close"])
                )

            current_price = closes[-1]

            first_price = closes[0]

            change_percent = round(
                (
                    (
                        current_price -
                        first_price
                    )
                    /
                    first_price
                ) * 100,
                2
            )

            return {
                "success": True,
                "symbol": symbol,
                "current_price": current_price,
                "change_percent": change_percent,
                "prices": closes
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
        }
