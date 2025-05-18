import unittest
import socket
import threading
import time
from server import data_queue

class TestThreadManagement(unittest.TestCase):
    def test_multiple_connections(self):
        def send_test_message():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect(("127.0.0.1", 6000))
                client_socket.sendall(b'{"sensor_id": "test_thread", "value": 99}\n')
            finally:
                client_socket.close()

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=send_test_message)
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Check if all messages were received
        received_count = 0
        while not data_queue.empty():
            data_queue.get()
            received_count += 1
        
        self.assertEqual(received_count, 5)

if __name__ == "__main__":
    unittest.main()
