import socket
import json
import time
import random
import logging
import os
import datetime

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def create_logger(sensor_id):
    log_filename = f"logs/{sensor_id}.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(message)s")
    return logging.getLogger(sensor_id)

def generate_sensor_data(sensor_id, temp_range, humidity_range, mode):
    if mode == "extreme":
        # Generate extreme values
        temp = random.choice([random.uniform(-50, -30), random.uniform(60, 80)])
        humidity = random.choice([random.uniform(-10, 0), random.uniform(100, 150)])
    elif mode == "disconnect":
        # Return None to simulate a disconnect
        if random.random() < 0.2:  # 20% chance of disconnect
            return None
        temp = round(random.uniform(temp_range[0], temp_range[1]), 2)
        humidity = round(random.uniform(humidity_range[0], humidity_range[1]), 2)
    else:
        # Normal mode
        temp = round(random.uniform(temp_range[0], temp_range[1]), 2)
        humidity = round(random.uniform(humidity_range[0], humidity_range[1]), 2)

    return {
        "sensor_id": sensor_id,
        "temperature": temp,
        "humidity": humidity,
        "timestamp": datetime.datetime.now().isoformat()
    }

def connect_to_drone(drone_ip, drone_port, logger):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((drone_ip, drone_port))
            logger.info(f"Connected to drone at {drone_ip}:{drone_port}")
            return sock
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            time.sleep(5)

def main():
    config = load_config()
    sensor_id = config["sensor_id"]
    interval = config["interval"]
    drone_ip = config["drone_ip"]
    drone_port = config["drone_port"]
    temp_range = config["temperature_range"]
    humidity_range = config["humidity_range"]
    mode = config["data_mode"]

    logger = create_logger(sensor_id)

    while True:
        try:
            sock = connect_to_drone(drone_ip, drone_port, logger)

            while True:
                # Generate data based on the current mode
                data = generate_sensor_data(sensor_id, temp_range, humidity_range, mode)

                # Handle simulated disconnects
                if data is None:
                    logger.warning(f"Simulating random disconnect for {sensor_id}")
                    print(f"🔌 Simulating random disconnect for {sensor_id}")
                    sock.close()
                    time.sleep(10)  # Simulate a long disconnect
                    break  # Exit inner loop to reconnect

                # Send the data
                message = json.dumps(data)
                sock.sendall(message.encode())
                logger.info(f"Data sent: {message}")
                print(f"Data sent: {message}")
                time.sleep(interval)

        except Exception as e:
            logger.error(f"Error during data transmission: {e}")
            time.sleep(config["reconnect_interval"])

if __name__ == "__main__":
    main()
