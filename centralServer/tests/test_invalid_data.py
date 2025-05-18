import unittest
import socket
import threading
import time
from server import data_queue

class TestInvalidData(unittest.TestCase):
    def test_invalid_json(self):
        # Create a client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # Connect to the server
            client_socket.connect(("127.0.0.1", 6000))
            client_socket.sendall(b'INVALID_JSON\n')
            time.sleep(1)  # Give the server time to process

            # Ensure no invalid data is added to the queue
            self.assertTrue(data_queue.empty())

        finally:
            client_socket.close()

if __name__ == "__main__":
    unittest.main()
