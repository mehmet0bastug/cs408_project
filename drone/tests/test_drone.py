import unittest
import socket
import json
import threading
import time
import sys
import os

# Ensure the parent directory is in the Python path for importing drone.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drone import DroneServer, load_config, initialize_logger

class TestDroneServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load configuration and initialize logger
        config = load_config()
        logger = initialize_logger(config["log_file"])

        # Start the drone server in a separate thread
        cls.drone_server = DroneServer(config, logger)
        cls.server_thread = threading.Thread(target=cls.drone_server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Give the server time to start
        time.sleep(2)

    def test_basic_connection(self):
        try:
            # Create a client socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("127.0.0.1", 5000))

            # Send a test message
            message = json.dumps({"sensor_id": "test_sensor", "temperature": 22.5, "humidity": 55.0}) + "\n"
            client_socket.sendall(message.encode())
            client_socket.close()

            # Wait for the server to process the message
            time.sleep(2)

            # Check if the message is in the data queue
            queue_contents = []
            while not self.drone_server.data_queue.empty():
                queue_contents.append(self.drone_server.data_queue.get())

            # Ensure at least one message was received
            self.assertTrue(len(queue_contents) > 0, "No messages received in the server queue.")

            # Check the content of the received message
            received_data = queue_contents[-1]
            self.assertEqual(received_data["sensor_id"], "test_sensor")
            self.assertEqual(received_data["temperature"], 22.5)
            self.assertEqual(received_data["humidity"], 55.0)

        except Exception as e:
            self.fail(f"Client connection test failed: {e}")

    @classmethod
    def tearDownClass(cls):
        # Stop the server
        cls.drone_server.forwarding_enabled = False
        time.sleep(1)  # Allow time for the server to shut down

if __name__ == "__main__":
    unittest.main()
