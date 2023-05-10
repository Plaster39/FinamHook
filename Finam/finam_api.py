import asyncio
import aiohttp
import config
class CustomOrderClient:
    def __init__(self, token: str, base_url: str):
        self.token = config.FINAM_API_TOKEN
        self.base_url = base_url
        self._order_url = "/api/v1/orders"
        self._stop_order_url = "/api/v1/stops"

    async def _exec_request(self, method, url, params=None, payload=None):
        headers = {
             "X-Api-Key":config.FINAM_API_TOKEN,
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.request(method, self.base_url + url, params=params, json=payload) as response:
                if response.status != 200:
                    print(f"Error: {response.status}")
                    print(await response.text())
                    return None
                return await response.json()

    async def get_orders(self, params):
        return await self._exec_request("GET", self._order_url, params=params)

    async def create_order(self, payload):
        return await self._exec_request("POST", self._order_url, payload=payload)

    async def del_order(self, params):
        return await self._exec_request("DELETE", self._order_url, params=params)

    async def get_stop_orders(self, params):
        return await self._exec_request("GET", self._stop_order_url, params=params)

    async def create_stop_order(self, payload):
        return await self._exec_request("POST", self._stop_order_url, payload=payload)

    async def del_stop_order(self, params):
        return await self._exec_request("DELETE", self._stop_order_url, params=params)

    async def create_stop_order(
            self,
            client_id: str,
            security_board: str,
            security_code: str,
            order_type: str,
            current_price: float,
            stop_loss_percent: float,
            take_profit_percent: float,
    ) :
        stop_loss_activation_price = current_price * (1 - stop_loss_percent / 100)
        take_profit_activation_price = current_price * (1 + take_profit_percent / 100)

        stop_loss = {
            "activationPrice" : stop_loss_activation_price,
            "marketPrice" : True,
            "quantity" : {
                "value" : stop_loss_percent,
                "units" : "Percent"
            },
            "time" : 0,
            "useCredit" : True
        }

        take_profit = {
            "activationPrice" : take_profit_activation_price,
            "marketPrice" : True,
            "quantity" : {
                "value" : take_profit_percent,
                "units" : "Percent"
            },
            "time" : 0,
            "useCredit" : True
        }

        payload = {
            "clientId" : client_id,
            "securityBoard" : security_board,
            "securityCode" : security_code,
            "buySell" : order_type,
            "stopLoss" : stop_loss,
            "takeProfit" : take_profit
        }

        return await self._exec_request("POST", self._stop_order_url, payload=payload)

