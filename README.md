# Smart Pool Control System – Group 13

This project is an Internet of Things (IoT) based Smart Pool Control System developed as a university group project. It enables real-time monitoring and automation of various pool-related functions using Raspberry Pi, MQTT, sensors, actuators and Home Assistant.

---

## Project Purpose

The system is designed to:

- Monitor **water temperature**, **pH level**, **water level**, **light intensity**, **motion** and **time display**
- Control actuators such as **LEDs**, **servo motors**, **camera** and **display**
- Visualize data via **Home Assistant**
- Use **MQTT** as a communication protocol to connect distributed components

---

## How the System Works

The Raspberry Pi serves as the central hub. Each sensor or actuator is connected to a Python script (located in the `final_scripts` folder) that either publishes data or listens for control messages via MQTT.

### Workflow:

1. **Sensors** (e.g., temperature, pH, light) publish readings via MQTT.
2. **Subscribers** (e.g., display, motors) listen and act based on MQTT messages.
3. **Home Assistant** displays sensor values.

---

## Folder: `final_scripts`

This folder contains all final working scripts divided into publishers and subscribers:

| Script                         | Description |
|--------------------------------|-------------|
| `B_Servo_Subscriber.py`        | Controls a servo motor (e.g. for water inflow control) |
| `B_Waterlevel_Publisher.py`    | Publishes water level data from an ultrasonic sensor |
| `E_TimeSignal_Publisher.py`    | Sends time signals for scheduling |
| `E_TimeSignal_Subscriber.py`   |  |
| `H_Camera_Subscriber.py`       | Captures images on motion detection |
| `H_Distance_Publisher.py`      | Publishes distance data from sensor |
| `H_ph_publisher.py`            | Publishes pool pH value readings |
| `L_Display_Subscriber.py`      | Displays incoming data on an e-paper display |
| `L_Temp_Publisher.py`          | Publishes pool temperature (DHT sensor) |
| `L_Temperature_Publisher.py`   | Alternative version of the temperature publisher |
| `R_Light_Publisher.py`         | Publishes ambient light level |
| `R_Light_Subscriber.py`        | Controls lighting based on received light values |
| `h_led+servo_subscriber.py`    | Controls LED and servo together (e.g. for pH regulation) |

Each script connects to a local MQTT broker and communicates via structured topics such as `pool/temperature/value` or `pool/ph/control`.

---

## Requirements

### Hardware

- Raspberry Pi 4
- Raspberry Pi 5
- Temperature Sensor (DS18B20)
- pH Sensor (GAOQHOU)
- Ultrasonic Sensor (HC-SR04)
- Photocell Sensor
- Slide Switch 
- Motion Sensor (VL6180X)
- E-paper Display
- Raspberry Pi Camera Board v2
- LEDs, Servo Motors
- Breadboard, Power Supply

### Software

- Python 3
- MQTT Broker (Mosquitto)
- Home Assistant
- Python Libraries:
  - `paho-mqtt`
  - `Adafruit_DHT`
  - `RPi.GPIO`
  - `pigpio`
  - `opencv-python`
  -  etc...
    
---

## Getting Started

### 1. Set up the MQTT Broker

Install the MQTT broker on the homeassistant.

### 2. Run Sensor/Actuator Scripts
Run each script individually on your Raspberry Pi (for example):

``python3 final_scripts/L_Temp_Publisher.py
python3 final_scripts/L_Display_Subscriber.py``

### 3. Connect Home Assistant
Set up MQTT integration in Home Assistant and add sensors using MQTT topics published by the scripts.

---

### Authors
| Name               | ID       | Module(s)                 |
| ------------------ | -------- | ------------------------- |
| Lea Tuschner       | 12208053 | Temperature + Display     |
| Evelyn Chea        | 12023171 | Time signal + automation  |
| Hanna Schwaiger    | 12211249 | pH sensor + LED + Servo   |
| Lejla Becirovic    | 12213605 | Water level + Servo       |
| Hermine Stöttinger | 12211105 | Motion detection + Camera |
| Ricarda Humer      | 12025965 | Photocell + Light control |

---

### License
This project was developed as part of a university course and is intended for educational use.

---



