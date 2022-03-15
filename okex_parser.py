import logging
import queue
import json
import time

import websocket

logger = logging.getLogger(__name__)


class OkexParser:

    def __init__(self, ticks_queue: queue.Queue, timeframe=60 * 5):
        #   : ticks_queue - очередь класса queue.Queue

        self.last_tick = None
        self.ticks_queue = ticks_queue

    def subscribe_on_okex_ticker(self, ws):
        logger.info(
            "Subscribe on okex websocket for symbol {}".format(
                self.symbols
            )
        )
        print([s+'@bookTicker' for s in self.symbols],)
        # подключаемся к потоку, перечисляя в переменной 'params' пары валют в виде списка строк
        params = json.dumps(
            {
                "method": "SUBSCRIBE",
                "params": [s+'@bookTicker' for s in self.symbols],
                "id":1
            }
        ) 

        ws.send(
            params
        )

    def parse_okex(self, ws, message):
        #   :message - сообщение в формате json
        
        data = json.loads(str(message))
        print(data)
        symbol = data["s"] # пара тикеров
        bid = float(data["b"]) # цена на покупку
        bid_qty = float(data["B"]) # количество на покупку 
        ask = float(data["a"]) # цена на продажу
        ask_qty = float(data["A"]) # количество на продажу
        time_now = time.time() # текущее время

        self.ticks_queue.put(
            (
                symbol,
                bid,
                ask,
                time_now
            )
        )


    def start_parsing(self, symbols):
        #   :symbols - список пар тикеров. Пример: ['ethbtc', 'btcusd']

        self.symbols = symbols

        ws_app = websocket.WebSocketApp(
            url="wss://stream.binance.com:9443/ws/v5/public",
            on_open=self.subscribe_on_okex_ticker,
            on_message=self.parse_okex,
            on_error=lambda ws, message: print(message, "ERROR")
        )

        ws_app.run_forever()

        

ttk = OkexParser(ticks_queue = queue.Queue())
ttk.start_parsing(symbols=['BNBUSDT','ethbtc'])

print(ttk.ticks_queue.qet)
print('End')