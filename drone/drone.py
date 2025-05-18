import socket
import threading
import json
import os
import logging
from datetime import datetime
from queue import Queue
from gui import DroneGUI


def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Config file not found. Please provide a valid config.json.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding config file: {e}")
        exit(1)

def create_logger(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    return logging.getLogger("Drone")

class DroneServer:
    def __init__(self, config, logger):
        self.server_port = config.get("server_port", 5000)
        self.aggregation_window = config.get("aggregation_window", 10)
        self.logger = logger
        self.data_queue = Queue()
        self.aggregation_thread = threading.Thread(target=self.aggregate_and_forward)
        self.aggregation_thread.daemon = True
        self.aggregation_thread.start()
        self.central_server_ip = config.get("central_server_ip", "127.0.0.1")
        self.central_server_port = config.get("central_server_port", 6000)
        self.battery_threshold = config.get("battery_threshold", 20)
        self.battery_level = 100
        self.forwarding_enabled = True
        self.battery_thread = threading.Thread(target=self.simulate_battery)
        self.battery_thread.daemon = True
        self.battery_thread.start()
 


    def start(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", self.server_port))
            server_socket.listen()

            self.logger.info(f"Drone server listening on port {self.server_port}")
            print(f"🚀 Drone server listening on port {self.server_port}")

            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    client_socket.settimeout(60)
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                    client_thread.start()

                except Exception as e:
                    self.logger.error(f"Error accepting client connection: {e}")
                    print(f"❌ Error accepting client connection: {e}")

        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            print(f"❌ Error starting server: {e}")
            exit(1)
    
    def handle_client(self, client_socket, client_address):
        self.logger.info(f"New connection from {client_address}")
        buffer = b""

        try:
            while True:
                try:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    buffer += chunk

                    # Process complete JSON messages in the buffer
                    while b"\n" in buffer:
                        message, buffer = buffer.split(b"\n", 1)
                        try:
                            sensor_data = json.loads(message.decode().strip())
                            self.data_queue.put(sensor_data)
                            self.logger.info(f"Received data from {sensor_data['sensor_id']}: {sensor_data}")
                            print(f"📥 From {sensor_data['sensor_id']}: {sensor_data}")

                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON decode error from {client_address}: {e}")
                            print(f"❌ JSON decode error from {client_address}: {e}")

                except socket.timeout:
                    self.logger.warning(f"Connection timeout with {client_address}")
                    print(f"⚠️ Connection timeout with {client_address}")
                    break

                except ConnectionResetError as e:
                    self.logger.warning(f"Connection reset by {client_address}: {e}")
                    print(f"⚠️ Connection reset by {client_address}: {e}")
                    break

                except Exception as e:
                    self.logger.error(f"Unexpected error with {client_address}: {e}")
                    print(f"❌ Unexpected error with {client_address}: {e}")
                    break

        finally:
            client_socket.close()
            self.logger.info(f"Connection closed with {client_address}")
            print(f"🔌 Connection closed with {client_address}")

    def aggregate_and_forward(self):
        # Separate buffers for each sensor type
        buffers = {
            "temperature_humidity": [],
            "air_quality": [],
            "noise_level": [],
            "wind_speed": []
        }

        while True:
            try:
                data = self.data_queue.get()

                # Determine the sensor type
                if "temperature" in data and "humidity" in data:
                    buffers["temperature_humidity"].append(data)

                elif "co2" in data and "pm25" in data:
                    buffers["air_quality"].append(data)

                elif "decibel" in data:
                    buffers["noise_level"].append(data)

                elif "wind_speed" in data and "wind_direction" in data:
                    buffers["wind_speed"].append(data)

                # Check if any buffer is ready for aggregation
                for sensor_type, buffer in buffers.items():
                    if len(buffer) >= self.aggregation_window:
                        # Calculate averages
                        avg_data = {}
                        for key in buffer[0].keys():
                            if key not in ["sensor_id", "timestamp"]:
                                avg_data[key] = round(sum(d[key] for d in buffer) / len(buffer), 2)

                        # Create the aggregated message
                        aggregated_data = {
                            **avg_data,
                            "timestamp": datetime.now().isoformat(),
                            "data_points": len(buffer)
                        }

                        # Log the aggregation
                        self.logger.info(f"✅ Aggregated data ({sensor_type}): {aggregated_data}")
                        print(f"✅ Aggregated data ({sensor_type}): {aggregated_data}")
                        self.send_to_central_server(aggregated_data)

                        # Clear the buffer for this sensor type
                        buffers[sensor_type].clear()

            except Exception as e:
                self.logger.error(f"Error during aggregation: {e}")
                print(f"❌ Error during aggregation: {e}")

    
    if not self.forwarding_enabled:
        self.logger.info("🚫 Skipping data transmission due to low battery.")
        return
        
    def send_to_central_server(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.central_server_ip, self.central_server_port))
                s.sendall((json.dumps(data) + "\n").encode())
                self.logger.info("Sent aggregated data to central server")
        except Exception as e:
            self.logger.error(f"❌ Failed to send data to central server: {e}")
            print(f"❌ Failed to send data to central server: {e}")
            
    def simulate_battery(self):
        import time
        while True:
            try:
                self.battery_level -= 1  # her döngüde %1 azalsın
                if self.battery_level <= self.battery_threshold:
                    if self.forwarding_enabled:
                        self.logger.warning("🔋 Battery low! Entering Return-to-Base mode.")
                        print("🔋 Battery low! Entering Return-to-Base mode.")
                        self.forwarding_enabled = False
                elif self.battery_level < 100:
                    self.battery_level += 0.5  # yavaş yavaş şarj oluyor
                    if not self.forwarding_enabled and self.battery_level > self.battery_threshold + 10:
                        self.forwarding_enabled = True
                        self.logger.info("🔋 Battery recharged. Resuming data transmission.")
                        print("🔋 Battery recharged. Resuming data transmission.")
    
                time.sleep(5)  # her 5 saniyede bir batarya güncellemesi
    
            except Exception as e:
                self.logger.error(f"❌ Battery simulation error: {e}")
                break




def main():
    config = load_config()
    logger = create_logger(config["log_file"])
    drone_server = DroneServer(config, logger)

    server_thread = threading.Thread(target=drone_server.start)
    server_thread.daemon = True
    server_thread.start()

    DroneGUI(drone_server)

if __name__ == "__main__":
    main()
