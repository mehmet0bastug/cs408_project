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

def generate_wind_speed_data(sensor_id, speed_range, direction_range, mode):
    if mode == "extreme":
        speed = random.choice([random.uniform(50, 100), random.uniform(0, 2)])
        direction = random.uniform(0, 360)
    elif mode == "disconnect":
        if random.random() < 0.2:
            return None
        speed = round(random.uniform(speed_range[0], speed_range[1]), 2)
        direction = round(random.uniform(direction_range[0], direction_range[1]), 2)
    else:
        speed = round(random.uniform(speed_range[0], speed_range[1]), 2)
        direction = round(random.uniform(direction_range[0], direction_range[1]), 2)

    return {
        "sensor_id": sensor_id,
        "wind_speed": speed,
        "wind_direction": direction,
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
    speed_range = config["speed_range"]
    direction_range = config["direction_range"]
    mode = config["data_mode"]

    logger = create_logger(sensor_id)

    while True:
        try:
            sock = connect_to_drone(drone_ip, drone_port, logger)

            while True:
                data = generate_wind_speed_data(sensor_id, speed_range, direction_range, mode)

                if data is None:
                    logger.warning(f"Simulating random disconnect for {sensor_id}")
                    print(f"🔌 Simulating random disconnect for {sensor_id}")
                    sock.close()
                    time.sleep(config["reconnect_interval"])
                    break

                message = json.dumps(data)
                sock.sendall((message + "\n").encode())
                logger.info(f"Data sent: {message}")
                print(f"Data sent: {message}")
                time.sleep(interval)

        except Exception as e:
            logger.error(f"Error during data transmission: {e}")
            time.sleep(config["reconnect_interval"])

if __name__ == "__main__":
    main()
