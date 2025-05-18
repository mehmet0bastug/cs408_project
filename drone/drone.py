import socket
import threading
import json
import os
import logging
from datetime import datetime
from collections import deque

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def create_logger(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")
    return logging.getLogger("Drone")

class DroneServer:
    def __init__(self, config, logger):
        self.server_port = config["server_port"]
        self.central_server_ip = config["central_server_ip"]
        self.central_server_port = config["central_server_port"]
        self.battery_threshold = config["battery_threshold"]
        self.data_forward_interval = config["data_forward_interval"]
        self.aggregation_window = config["aggregation_window"]
        self.logger = logger
        self.data_queue = deque(maxlen=self.aggregation_window)
        self.lock = threading.Lock()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", self.server_port))
        server_socket.listen()

        self.logger.info(f"Drone server listening on port {self.server_port}")
        print(f"Drone server listening on port {self.server_port}")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        self.logger.info(f"New connection from {client_address}")

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Decode the incoming data
                message = data.decode()
                sensor_data = json.loads(message)

                # Log the incoming data
                self.logger.info(f"Received data from {sensor_data['sensor_id']}: {sensor_data}")
                print(f"From {sensor_data['sensor_id']}: {sensor_data}")

                # Add to aggregation queue
                self.add_to_queue(sensor_data)

            except Exception as e:
                self.logger.error(f"Error with client {client_address}: {e}")
                break

        client_socket.close()
        self.logger.info(f"Connection closed with {client_address}")

    def add_to_queue(self, data):
        with self.lock:
            self.data_queue.append(data)
            self.check_for_anomalies(data)

            # Check if the aggregation window is full
            if len(self.data_queue) == self.aggregation_window:
                self.aggregate_and_forward()

    def check_for_anomalies(self, data):
        temp = data["temperature"]
        humidity = data["humidity"]
        sensor_id = data["sensor_id"]

        # Simple anomaly detection
        if temp < -30 or temp > 60:
            self.logger.warning(f"Temperature anomaly from {sensor_id}: {temp}°C")
            print(f"⚠️ Temperature anomaly from {sensor_id}: {temp}°C")
        
        if humidity < 0 or humidity > 100:
            self.logger.warning(f"Humidity anomaly from {sensor_id}: {humidity}%")
            print(f"⚠️ Humidity anomaly from {sensor_id}: {humidity}%")

    def aggregate_and_forward(self):
        with self.lock:
            # Calculate averages
            avg_temp = round(sum(d["temperature"] for d in self.data_queue) / len(self.data_queue), 2)
            avg_humidity = round(sum(d["humidity"] for d in self.data_queue) / len(self.data_queue), 2)

            # Create the aggregated message
            aggregated_data = {
                "average_temperature": avg_temp,
                "average_humidity": avg_humidity,
                "timestamp": datetime.now().isoformat(),
                "data_points": len(self.data_queue)
            }

            # Log the aggregation
            self.logger.info(f"Aggregated data: {aggregated_data}")
            print(f"✅ Aggregated data: {aggregated_data}")

            # Clear the data queue
            self.data_queue.clear()

            # (Optional) Forward to the central server (we'll implement this next)

def main():
    config = load_config()
    logger = create_logger(config["log_file"])

    drone_server = DroneServer(config, logger)
    drone_server.start()

if __name__ == "__main__":
    main()
