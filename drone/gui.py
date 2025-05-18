import tkinter as tk
import threading
import time
import random

class DroneGUI:
    def __init__(self, drone_server):
        self.drone = drone_server
        self.root = tk.Tk()
        self.root.title("Drone Monitor")
        self.root.geometry("400x300")

        self.battery_label = tk.Label(self.root, text="🔋 Battery: 100%", font=("Arial", 14))
        self.battery_label.pack(pady=10)

        self.status_label = tk.Label(self.root, text="🛰 Connected Sensors: 0", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.data_label = tk.Label(self.root, text="📥 Last Data: None", font=("Arial", 10), wraplength=350)
        self.data_label.pack(pady=10)

        self.anomaly_label = tk.Label(self.root, text="✅ No anomaly detected", font=("Arial", 10), fg="green")
        self.anomaly_label.pack(pady=10)

        # GUI güncelleyici thread
        self.update_thread = threading.Thread(target=self.update_gui)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.root.mainloop()

    def update_gui(self):
        while True:
            battery = self.drone.battery_level
            self.battery_label.config(text=f"🔋 Battery: {battery:.1f}%")

            # Sensör sayısı (aktif bağlantı listesi tutuyorsan kullan)
            sensor_count = getattr(self.drone, "connected_sensors", 0)
            self.status_label.config(text=f"🛰 Connected Sensors: {sensor_count}")

            # Son veri
            if hasattr(self.drone, "last_data"):
                self.data_label.config(text=f"📥 Last Data: {self.drone.last_data}")
            
            # Anomali (örneğin sıcaklık 60’tan fazlaysa)
            if hasattr(self.drone, "last_data"):
                d = self.drone.last_data
                if "temperature" in d and d["temperature"] > 60:
                    self.anomaly_label.config(text="🚨 High Temperature!", fg="red")
                else:
                    self.anomaly_label.config(text="✅ No anomaly detected", fg="green")

            time.sleep(1)
