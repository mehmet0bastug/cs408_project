import socket
import json
import time

def simulate_sensor(sensor_id, port=5000, num_messages=15, delay=1):
    HOST = "127.0.0.1"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, port))
        print(f"🔌 {sensor_id} connected to drone.")

        for i in range(num_messages):
            data = {
                "sensor_id": sensor_id,
                "temperature": 20 + i % 5,
                "humidity": 50 + (i % 10),
                "timestamp": time.time()
            }
            message = json.dumps(data) + "\n"
            sock.sendall(message.encode())
            print(f"📤 {sensor_id} sent: {data}")
            time.sleep(delay)

        sock.close()
        print(f"🔌 {sensor_id} disconnected.")

    except Exception as e:
        print(f"❌ {sensor_id} failed to connect/send: {e}")

if __name__ == "__main__":
    simulate_sensor("sensor1")
