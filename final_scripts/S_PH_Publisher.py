import time
import board
import busio
import paho.mqtt.client as mqtt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/ph"

# Initialize I2C-Connection
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
channel = AnalogIn(ads, ADS.P0)

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# Calibration: 2.667 V = pH 7
def voltage_to_ph(voltage):
    ph = 7 - ((voltage - 2.667) * 6)
    return round(ph, 2)
 
try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_start()

    print("Start measuring...")

    while True: 
        voltage = channel.voltage
        ph_value = voltage_to_ph(voltage)
        print(f"Publishing: pH = {ph_value}, Voltage = {voltage:.3f} V")
        mqttc.publish("/sensor/ph", ph_value)
        time.sleep(2)

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()