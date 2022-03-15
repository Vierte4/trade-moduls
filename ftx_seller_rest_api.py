import hmac
import json
import logging
import threading
import time

import requests
from requests import Request

logger = logging.getLogger("FtxSellerOrder")


class FtxSeller:
    base_endpoint = 'https://ftx.com/api/orders'

    def __init__(self, client_api: str, client_secret: str):
        self.client_api = client_api
        self.client_secret = client_secret
        self.requests_counter = 0
        self.last_request_timestamp = time.time()

    def create_headers(self, payload):
        """Для подключения к лк пользователя необходимо в headers ввести его
        API KEY и signature, который мы получаем путём взятия SHA256 HMAC,
        используя API secret в качестве ключа, от следующих строк:
            :Текущее время, округлённое до мс (1528394229375)
            :Метод запроса (GET или POST)
            :Путь запроса (всё кроме hostname (api/orders)
            :Тело запроса в формате json (только для запросов POST)"""

        ts = int(time.time() * 1000)
        request = Request('POST', FtxSeller.base_endpoint)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}{payload}'.encode()
        signature = hmac.new(self.client_secret.encode(), signature_payload,
                             'sha256').hexdigest()
        prepared.headers['FTX-KEY'] = self.client_api
        prepared.headers['FTX-SIGN'] = signature
        prepared.headers['FTX-TS'] = str(ts)

        return prepared.headers

    def create_request(self, payload):
        headers = self.create_headers(payload)
        response = requests.request("POST", FtxSeller.base_endpoint,
                                    headers=headers, data=payload)
        logger.info("Response: {}".format(response.text))

    def send_trade_action(
            self,
            trade_action: str,  # buy or sell
            price: float,
            symbol: str,  # XRP/USDT
            ord_type: str,  # market or limit
            amount: float,  # 40
    ):
        payload = json.dumps({
            "market": symbol,
            "side": trade_action,
            "price": price,
            "size": amount,
            "type": ord_type,
            "reduceOnly": False,
            "ioc": False,
            "postOnly": False,
            "clientId": None
        })

        threading.Thread(
            target=self.create_request,
            args=(payload,),
            daemon=True
        ).start()


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel("INFO")

    seller = FtxSeller(
        client_api='client_api',
        client_secret='client_secret'
    )

    print("Send order")
    for i in range(10):
        seller.send_trade_action(
            trade_action='buy',
            price=1,
            amount=10,
            symbol="XRP/USDT",
            ord_type="market"
        )
    time.sleep(12)
