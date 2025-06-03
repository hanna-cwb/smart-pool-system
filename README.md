# Smart Pool Control System – Group 13

This project is an Internet of Things (IoT) based Smart Pool Control System developed as a university group project. It enables real-time monitoring and automation of various pool-related functions using Raspberry Pi 4, MQTT, sensors, actuators and Home Assistant on a Raspberry Pi 5.

---

## Project Purpose

The system is designed to:

- Monitor **water temperature**, **pH level**, **water level**, **light intensity**, **motion** and **time**
- Control actuators such as **LEDs**, **servo motors**, **camera** and **display**
- Visualize data via **Home Assistant**
- Use **MQTT** as a communication protocol to connect distributed components

---

## How the System Works

The Raspberry Pi 4 serves as the central hub. Each sensor or actuator is connected to a Python script (located in the `final_scripts` folder) that either publishes data or listens for control messages via MQTT.

### Workflow:

1. **Sensors** (e.g., temperature, pH, light) publish readings via MQTT.
2. **Subscribers/Actuators** (e.g., display, motors) listen and act based on MQTT messages.
3. **Home Assistant** displays sensor values.

---

## Folder: `final_scripts`

This folder contains all final working scripts divided into publishers and subscribers:

| Script                         | Topic | Description | 
|--------------------------------|-------------|-------------|
| `B_Servo_Subscriber.py`        | waterlevel, pumpStatus  | Controls a servo motor (e.g. for water inflow control) |
| `B_Waterlevel_Publisher.py`    | waterlevel | Publishes water level data from an ultrasonic sensor |
| `E_TimeSignal_Subscriber.py`   | timeSignal | Displays pump status based on received time-triggered messages |
| `E_TimeSignal_Publisher.py`    | timeSignal | Publishes scheduled on/off signals for simulated pump control |
| `H_Camera_Subscriber.py`       | distance, images | Captures images on motion detection and generates a video stream |
| `H_Distance_Publisher.py`      | distance | Publishes distance data from sensor |
| `L_Display_Subscriber.py`      | temperature | Displays incoming data on an e-paper display |
| `L_Temperature_Publisher.py`   | temperature, humidity | Alternative version of the temperature publisher |
| `R_Light_Subscriber.py`        | light | Controls lighting based on received light values |
| `R_Light_Publisher.py`         | light | Publishes ambient light level |
| `S_LedServo_Subscriber.py`     | ph, phPumpStatus | Controls LED and servo together (e.g. for pH regulation) |
| `S_PH_Publisher.py`            | ph | Publishes pool pH value readings |

Each script connects to a local MQTT broker and communicates via structured topics such as `sensor/temperature` or `sensor/distance`.

---

## Requirements

### Hardware

- Raspberry Pi 4 
- Raspberry Pi 5
- Homeassistant dinges TODO Hanna
- Servo HAT for Raspberry Pi
- Analog Digital Converter (1115 ADS Module)

- Temperature Sensor (DS18B20)
- pH Sensor (GAOQHOU)
- Ultrasonic Sensor (HC-SR04)
- Photocell Sensor (5506 LDR)
- Motion Sensor (VL6180X)
- E-paper Display (Waveshare 1.54 Inch) 
- Raspberry Pi Camera Board v2
- 2 Servo Motors (FeeTech FS5103R, DC Motor in Micro Servo Body)

- Slide Switch 
- LEDs
- Breadboards, Cables, Resistors

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
    
TODO komisches Git vom E Paper display
---

## Getting Started

### 1. Set up

#### a. Raspberry Pi 4

Wire the Raspberry Pi 4 and the needed components (actors, sensors, etc. )

Connect your device and the Raspberry Pi 4 via WLAN, ensure to use the correct IP address

```
ssh admin@192.168.8.113
```

Enable the needed Interfaces I2C and SPI in the Raspberry Configurations: 

```
sudo raspi-config
```
Interfacing Options > I2C > Enable

Interfacing Options > SPI > Enable

```
sudo reboot
```

Create and activate the virtual environment:

```
python3 -m venv vl6180x-env
source ~vl6180x-venv/bin/activate
```

Download needed packages in the venv environment
```
pip install ...
```

#### b. Raspberry Pi 5

Set Up the Homeassistant environment on the Raspberry Pi 5

Install the MQTT broker on the homeassistant.

Establish connection

Configure displays

TODO Hanna

### 2. Run Sensor/Actuator Scripts

Run each script individually on Raspberry Pi by executing the following command in seperate terminals on the device. Ensure that the connection is established and the venv environment is activated.

```
python3 B_Servo_Subscriber.py
```

### 3. Connect Home Assistant
Set up MQTT integration in Home Assistant and add sensors using MQTT topics published by the scripts.

---

### Authors
| Name               | ID       |
| ------------------ | -------- |
| Lea Tuschner       | 12208053 |
| Evelyn Chea        | 12023171 |
| Hanna Schwaiger    | 12211249 |
| Lejla Becirovic    | 12213605 |
| Hermine Stöttinger | 12211105 |
| Ricarda Humer      | 12025965 |

---

### License
This project was developed as part of a university course and is intended for educational use.

---

