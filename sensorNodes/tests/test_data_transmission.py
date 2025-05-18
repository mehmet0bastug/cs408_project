import unittest
import socket
import json
import os
import time

class TestSensorDataTransmission(unittest.TestCase):
    def test_data_transmission(self):
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

                # Establish a connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.connect((config["drone_ip"], config["drone_port"]))

                    # Prepare a sample data packet based on the sensor type
                    sample_data = {"sensor_id": config["sensor_id"], "timestamp": "2025-05-18T19:45:00"}
                    
                    # Add sensor-specific fields
                    if "AirQuality" in sensor_dir:
                        sample_data.update({"co2": 400.0, "pm25": 15.0})
                    elif "NoiseLevel" in sensor_dir:
                        sample_data.update({"decibel": 60.0})
                    elif "TemperatureHumidity" in sensor_dir:
                        sample_data.update({"temperature": 25.5, "humidity": 60.0})
                    elif "WindSpeed" in sensor_dir:
                        sample_data.update({"wind_speed": 12.5, "wind_direction": 180.0})

                    # Send the data
                    message = json.dumps(sample_data) + "\n"
                    sock.sendall(message.encode())

                finally:
                    sock.close()

            except FileNotFoundError as e:
                self.fail(f"Config file not found for {sensor_dir}: {e}")
            except Exception as e:
                self.fail(f"Data transmission test failed for {sensor_dir}: {e}")

if __name__ == "__main__":
    unittest.main()
