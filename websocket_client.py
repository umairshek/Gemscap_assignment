import websocket
import json
import threading
import time

latest_ticks = []

def on_message(ws, message):
    data = json.loads(message)
    tick = {
        "timestamp": time.time(),
        "symbol": data["s"],
        "price": float(data["p"]),
        "qty": float(data["q"])
    }
    latest_ticks.append(tick)

def start_socket(symbol):
    socket = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    ws = websocket.WebSocketApp(socket, on_message=on_message)
    t = threading.Thread(target=ws.run_forever)
    t.daemon = True
    t.start()
