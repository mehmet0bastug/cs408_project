import unittest
import socket
import threading
import json
import time
from server import data_queue

class TestDataReception(unittest.TestCase):
    def test_data_reception(self):
        # Create a client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client_socket.connect(("127.0.0.1", 6000))
            message = {"sensor_id": "test_sensor", "value": 42}
            client_socket.sendall((json.dumps(message) + "\n").encode())
            time.sleep(1)  # Give the server time to process

            # Check if data was received
            self.assertFalse(data_queue.empty())
            received_data = data_queue.get()
            self.assertEqual(received_data["sensor_id"], "test_sensor")
            self.assertEqual(received_data["value"], 42)

        finally:
            client_socket.close()

if __name__ == "__main__":
    unittest.main()
