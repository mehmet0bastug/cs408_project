import unittest
from server import data_queue

class TestQueueHandling(unittest.TestCase):
    def test_queue_integrity(self):
        # Clear the queue before testing
        while not data_queue.empty():
            data_queue.get()
        
        # Simulate data reception
        test_data = {"sensor_id": "test_queue", "value": 123}
        data_queue.put(test_data)

        # Check the queue state
        self.assertFalse(data_queue.empty())
        received_data = data_queue.get()
        self.assertEqual(received_data, test_data)

if __name__ == "__main__":
    unittest.main()
