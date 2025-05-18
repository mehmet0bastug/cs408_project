import unittest
import socket
import json
import threading
import time
from queue import Queue
from drone import DroneServer, load_config, create_logger


class TestDroneServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start the drone server in a separate thread
        config = load_config()
        logger = create_logger(config["log_file"])
        cls.drone_server = DroneServer(config, logger)
        cls.server_thread = threading.Thread(target=cls.drone_server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)  # Give the server time to start

    def test_client_connection(self):
        try:
            # Test client connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 5000))
            client_socket.sendall(b'{"sensor_id": "test_sensor", "temperature": 22.5, "humidity": 55.0}\n')
            client_socket.close()

            # Wait for the data to be processed
            time.sleep(1)
            
            # Check the data queue
            self.assertFalse(self.drone_server.data_queue.empty())
            data = self.drone_server.data_queue.get()
            self.assertEqual(data["sensor_id"], "test_sensor")
            self.assertEqual(data["temperature"], 22.5)
            self.assertEqual(data["humidity"], 55.0)

        except Exception as e:
            self.fail(f"Client connection test failed: {e}")

    def test_aggregation(self):
        try:
            # Send multiple messages to fill the aggregation window
            for _ in range(10):
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect(("127.0.0.1", 5000))
                message = json.dumps({"sensor_id": "test_sensor", "temperature": 20.0, "humidity": 50.0}) + "\n"
                client_socket.sendall(message.encode())
                client_socket.close()
                time.sleep(0.1)

            # Wait for the server to aggregate the data
            time.sleep(2)

            # Check if the data was aggregated correctly
            # This should print an aggregation message in the drone server log
            self.assertTrue(self.drone_server.data_queue.empty())

        except Exception as e:
            self.fail(f"Aggregation test failed: {e}")

    def test_battery_management(self):
        try:
            # Reduce the battery level to trigger return-to-base mode
            self.drone_server.battery_level = 10
            time.sleep(1)

            # Attempt to send a message, should be skipped
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 5000))
            message = json.dumps({"sensor_id": "test_sensor", "temperature": 25.0, "humidity": 60.0}) + "\n"
            client_socket.sendall(message.encode())
            client_socket.close()

            # Wait for the data to be processed
            time.sleep(1)

            # Check that no new data was added to the queue
            self.assertTrue(self.drone_server.data_queue.empty())

            # Recharge the battery
            self.drone_server.battery_level = 100
            time.sleep(1)

            # Send another message
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 5000))
            message = json.dumps({"sensor_id": "test_sensor", "temperature": 30.0, "humidity": 70.0}) + "\n"
            client_socket.sendall(message.encode())
            client_socket.close()

            # Wait for the data to be processed
            time.sleep(1)

            # Check that the data was added to the queue
            self.assertFalse(self.drone_server.data_queue.empty())
            data = self.drone_server.data_queue.get()
            self.assertEqual(data["temperature"], 30.0)
            self.assertEqual(data["humidity"], 70.0)

        except Exception as e:
            self.fail(f"Battery management test failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Stop the server
        cls.drone_server.forwarding_enabled = False
        time.sleep(1)  # Allow time for the server to shut down


if __name__ == "__main__":
    unittest.main()
