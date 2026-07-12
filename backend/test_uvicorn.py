import sys
import threading
import time
import httpx
from uvicorn import Config, Server
import asyncio

config = Config("main:app", host="127.0.0.1", port=8002, log_level="error")
server = Server(config)

def run_server():
    server.run()

t = threading.Thread(target=run_server)
t.start()

time.sleep(2)  # Wait for server to start

try:
    with open("test.txt", "rb") as f:
        res = httpx.post("http://127.0.0.1:8002/upload", files={"file": f})
        print("Status:", res.status_code)
        print("Response:", res.text)
except Exception as e:
    print("Request Error:", e)
finally:
    server.should_exit = True
    t.join()
