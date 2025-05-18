import socket
import threading
import json
import logging
import os
from queue import Queue
from pathlib import Path

# Load the configuration
def load_config():
    try:
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Config file not found. Please provide a valid config.json.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding config file: {e}")
        exit(1)

# Initialize logging
def initialize_logger(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logging.info("✅ Server started and logging initialized")

# Main configuration
cfg = load_config()
server_port = cfg.get('serverPort', 6000)
log_file = cfg.get('logFile', 'central_server.log')
initialize_logger(log_file)

# Queue for incoming data
data_queue = Queue()

class DroneHandler(threading.Thread):
    def __init__(self, conn, addr):
        super().__init__(daemon=True)
        self.conn = conn
        self.addr = addr

    def run(self):
        logging.info(f"📶 New connection from {self.addr}")
        buffer = b''

        try:
            while True:
                try:
                    # Receive data from the client
                    chunk = self.conn.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk

                    # Process each complete message in the buffer
                    while b'\n' in buffer:
                        raw, buffer = buffer.split(b'\n', 1)
                        try:
                            message = raw.decode().strip()
                            if message:
                                msg = json.loads(message)
                                data_queue.put(msg)
                                logging.info(f"📥 Received data from {msg.get('sensor_id', 'Unknown')}: {msg}")
                                print(f"📥 Received data: {msg}")

                        except json.JSONDecodeError as e:
                            logging.error(f"❌ JSON decode error: {e}")
                            print(f"❌ JSON decode error: {e}")

                except socket.timeout:
                    logging.warning(f"⚠️ Connection timeout with {self.addr}")
                    print(f"⚠️ Connection timeout with {self.addr}")
                    break

                except ConnectionResetError as e:
                    logging.warning(f"⚠️ Connection reset by {self.addr}: {e}")
                    print(f"⚠️ Connection reset by {self.addr}: {e}")
                    break

                except Exception as e:
                    logging.error(f"❌ Unexpected error with {self.addr}: {e}")
                    print(f"❌ Unexpected error with {self.addr}: {e}")
                    break

        finally:
            self.conn.close()
            logging.info(f"🔌 Connection closed with {self.addr}")
            print(f"🔌 Connection closed with {self.addr}")

def main():
    try:
        # Create server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', server_port))
        sock.listen(5)
        logging.info(f"🚀 Central server listening on port {server_port}")
        print(f"🚀 Central server listening on port {server_port}")

        while True:
            try:
                # Accept incoming connections
                conn, addr = sock.accept()
                conn.settimeout(60)
                handler = DroneHandler(conn, addr)
                handler.start()

            except Exception as e:
                logging.error(f"❌ Error accepting client connection: {e}")
                print(f"❌ Error accepting client connection: {e}")

    except Exception as e:
        logging.error(f"❌ Error starting server: {e}")
        print(f"❌ Error starting server: {e}")

    finally:
        sock.close()
        logging.info("🛑 Server shutdown")
        print("🛑 Server shutdown")

if __name__ == '__main__':
    main()
