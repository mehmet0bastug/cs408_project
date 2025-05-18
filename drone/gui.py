import tkinter as tk
import threading
import time
import json

class DroneGUI:
    def __init__(self, drone_server):
        self.drone = drone_server
        self.root = tk.Tk()
        self.root.title("Drone Monitor")
        self.root.geometry("450x320")

        self.battery_label = tk.Label(self.root, text="🔋 Battery: N/A", font=("Arial", 14))
        self.battery_label.pack(pady=10)

        self.status_label = tk.Label(self.root, text="🛰 Connected Sensors: N/A", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.data_label = tk.Label(self.root, text="📥 Last Data: None", font=("Arial", 10), wraplength=400, justify="left")
        self.data_label.pack(pady=10)

        self.anomaly_label = tk.Label(self.root, text="✅ No anomaly detected", font=("Arial", 10), fg="green")
        self.anomaly_label.pack(pady=10)

        # Arayüzü güncelleyen thread
        self.update_thread = threading.Thread(target=self.update_gui)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.root.mainloop()

    def update_gui(self):
        while True:
            try:
                # Batarya
                battery = getattr(self.drone, "battery_level", None)
                if battery is not None:
                    self.battery_label.config(text=f"🔋 Battery: {battery:.1f}%")
                else:
                    self.battery_label.config(text="🔋 Battery: N/A")

                # Sensör sayısı (şu an simüle edilmiyor)
                sensor_count = getattr(self.drone, "connected_sensors", "N/A")
                self.status_label.config(text=f"🛰 Connected Sensors: {sensor_count}")

                # Son veri
                last_data = getattr(self.drone, "last_data", None)
                if last_data:
                    self.data_label.config(text="📥 Last Data:\n" + json.dumps(last_data, indent=2))
                else:
                    self.data_label.config(text="📥 Last Data: None")

                # Anomali kontrolü
                if last_data and "temperature" in last_data:
                    if last_data["temperature"] > 60:
                        self.anomaly_label.config(text="🚨 High Temperature!", fg="red")
                    else:
                        self.anomaly_label.config(text="✅ No anomaly detected", fg="green")
                else:
                    self.anomaly_label.config(text="✅ No anomaly detected", fg="green")

                time.sleep(1)

            except Exception as e:
                print(f"[GUI Error] {e}")
                time.sleep(1)
