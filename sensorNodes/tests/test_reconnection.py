import unittest
import socket
import json
import os
import time

class TestSensorReconnection(unittest.TestCase):
    def test_reconnection(self):
        # Base directory for sensor nodes
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
        sensor_dirs = ["AirQualityNode", "NoiseLevelNode", "TemperatureHumidityNode", "WindSpeedNode"]
        
        for sensor_dir in sensor_dirs:
            try:
                # Construct the full path to the config file
                config_path = os.path.join(base_dir, sensor_dir, "config.json")
                
                # Load the config file
                with open(config_path, "r") as file:
                    config = json.load(file)

                # Simulate reconnection attempts
                for attempt in range(config.get("reconnect_attempts", 3)):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            sock.connect((config["drone_ip"], config["drone_port"]))
                            break  # Exit the loop if the connection is successful
                        finally:
                            sock.close()
                    except Exception as e:
                        if attempt == config.get("reconnect_attempts", 3) - 1:
                            self.fail(f"Reconnection test failed for {sensor_dir}: {e}")
                        time.sleep(config.get("reconnect_interval", 5))

            except FileNotFoundError as e:
                self.fail(f"Config file not found for {sensor_dir}: {e}")
            except Exception as e:
                self.fail(f"Reconnection test failed for {sensor_dir}: {e}")

if __name__ == "__main__":
    unittest.main()
