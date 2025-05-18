import socket
import threading
import json
import logging
from queue import Queue
from pathlib import Path

cfg = json.load(open(Path(__file__).parent / 'config.json'))
serverPort = cfg['serverPort']
logFile = cfg['logFile']

logging.basicConfig(filename=logFile, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

dataQueue = Queue()

class DroneHandler(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr

    def run(self):
        logging.info(f"Connection from {self.addr}")
        buffer = b''
        try:
            while True:
                chunk = self.conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if b'\n' in buffer:
                    raw, buffer = buffer.split(b'\n', 1)
                    try:
                        msg = json.loads(raw.decode())
                        dataQueue.put(msg)
                        logging.info(f"Received data: {msg}")
                    except:
                        logging.error("Invalid JSON")
        except:
            logging.error(f"Error with {self.addr}")
        finally:
            self.conn.close()
            logging.info(f"Disconnected {self.addr}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', serverPort))
    sock.listen(5)
    logging.info(f"Listening on port {serverPort}")
    try:
        while True:
            conn, addr = sock.accept()
            handler = DroneHandler(conn, addr)
            handler.start()
    except KeyboardInterrupt:
        logging.info("Shutting down")
    finally:
        sock.close()

if __name__ == '__main__':
    main()
