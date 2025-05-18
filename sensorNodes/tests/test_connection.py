import unittest
import socket
import json
import os

class TestSensorConnection(unittest.TestCase):
    def test_connection(self):
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

                # Attempt to connect to the drone server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((config["drone_ip"], config["drone_port"]))
                finally:
                    sock.close()

            except FileNotFoundError as e:
                self.fail(f"Config file not found for {sensor_dir}: {e}")
            except Exception as e:
                self.fail(f"Connection test failed for {sensor_dir}: {e}")

if __name__ == "__main__":
    unittest.main()
