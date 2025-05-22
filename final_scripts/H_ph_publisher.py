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

# I2C-Verbindung
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
channel = AnalogIn(ads, ADS.P0)

# Define on_connect event Handler
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
    else:
        logging.error(f"Failed to connect, return code {rc}")

# Define on_publish event Handler
def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

# Register Event Handlers
mqttc.on_connect = on_connect
#mqttc.on_publish = on_publish

# Kalibrierung: 2.667 V = pH 7
def voltage_to_ph(voltage):
    ph = 7 - ((voltage - 2.667) * 6)
    return round(ph, 2)
 
try:
    # Connect to MQTT Broker
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

    # Start MQTT loop to handle callbacks
    mqttc.loop_start()

    print("Starte Messung...")

    try:
      while True: 
        voltage = channel.voltage
        ph_value = voltage_to_ph(voltage)
        print(f"Publishing: pH = {ph_value}, Voltage = {voltage:.3f} V")
        mqttc.publish("/sensor/ph", ph_value)
        #mqttc.publish("sensor/ph_voltage", voltage)
        time.sleep(2)
    except KeyboardInterrupt:
      print("\nMessung beendet.")

    # Give some time for message to be sent before disconnecting
    mqttc.loop_stop()
    mqttc.disconnect()

except Exception as e:
    logging.error(f"Error: {e}")
   