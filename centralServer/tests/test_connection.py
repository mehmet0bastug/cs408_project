import unittest
import socket
import threading
import json
import time
from server import data_queue

class TestServerConnection(unittest.TestCase):
    def test_basic_connection(self):
        # Create a client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client_socket.connect(("127.0.0.1", 6000))
            client_socket.sendall(b'{"sensor_id": "test_sensor", "value": 42}\n')
            time.sleep(1)  # Give the server time to process

            # Check if data was received
            self.assertFalse(data_queue.empty())
            data = data_queue.get()
            self.assertEqual(data["sensor_id"], "test_sensor")
            self.assertEqual(data["value"], 42)

        finally:
            client_socket.close()

if __name__ == "__main__":
    unittest.main()
