# CS408 Project - Drone-Enabled Mobile Edge Computing for Environmental Monitoring

### **Project Members:**
- **Mehmet Barış Baştuğ**  
- **Eda Nur Demir**  
- **Mert Genc**  

---

### **📚 Project Overview**
This project focuses on building a simulated system for environmental monitoring using sensor nodes, a drone, and a central server. The primary goal is to develop a real-time data processing pipeline that collects environmental data, performs edge processing, and visualizes the results.

---

### **📁 Project Directory Structure**
cs408_project/
│
├── README.md
├── Configuration_Guide.md
├── .gitignore
│
├── SensorNodes/
│ ├── sensor.py
│ ├── config.json
│ ├── logs/
│ └── tests/
│
├── Drone/
│ ├── drone.py
│ ├── config.json
│ ├── logs/
│ └── tests/
│
├── CentralServer/
│ ├── server.py
│ ├── config.json
│ ├── gui.py (optional)
│ ├── logs/
│ └── tests/
│
└── docs/
├── Architecture_Diagram.png
├── Module_Descriptions.md
└── Test_Cases.md
---

### **📝 Project Components**

1. **Sensor Nodes (`SensorNodes/`)**
   - Simulate temperature and humidity sensors.
   - Support for normal, extreme, and disconnect modes.
   - Sends data to the drone server.

2. **Drone (`Drone/`)**
   - Acts as the edge processing unit.
   - Receives and aggregates sensor data.
   - Detects anomalies and forwards data to the central server.

3. **Central Server (`CentralServer/`)**
   - Collects processed data from the drone.
   - Provides real-time data visualization (optional).

4. **Documentation (`docs/`)**
   - Includes architecture diagrams and module descriptions.

---

### **⚙️ Configuration Files**

Each module has its own **`config.json`** file for flexible configuration. Refer to **`Configuration_Guide.md`** for detailed parameter descriptions.

---

### **🚀 Running the Project**

1. **Set Up the Directory Structure:**
   ```bash
   mkdir -p SensorNodes/logs SensorNodes/tests
   mkdir -p Drone/logs Drone/tests
   mkdir -p CentralServer/logs CentralServer/tests
   mkdir -p docs
   touch README.md Configuration_Guide.md .gitignore

2. **Run the Drone Server:**
    ```bash
   cd drone
   python3 drone.py


3. **Run the Sensor Node:**
    ```bash
   cd ../sensorNodes
   python3 sensor.py



