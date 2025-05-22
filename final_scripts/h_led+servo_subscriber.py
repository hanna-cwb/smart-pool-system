import time
import board
import busio
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from adafruit_pca9685 import PCA9685
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/servo+led"

# Hardware Setup
LED_PIN = 27
SERVO_CHANNEL = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50

# Steuerfunktionen
def activate_servo():
    pca.channels[SERVO_CHANNEL].duty_cycle = 0x5000 #default 0x6000

def deactivate_servo():
    pca.channels[SERVO_CHANNEL].duty_cycle = 0x0000

# MQTT Callback
def on_connect(client, userdata, flags, rc):
    print("MQTT verbunden.")
    client.subscribe("sensor/ph_value")

def on_message(client, userdata, msg):
    try:
        ph = float(msg.payload.decode())
        print(f"Empfangen: pH = {ph}")
        if ph > 7.5:
            GPIO.output(LED_PIN, GPIO.HIGH)
            activate_servo()
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            deactivate_servo()
    except ValueError:
        print("Ungültiger pH-Wert.")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

mqttc.username_pw_set(username="mqtt-user", password="mqtt")
# Register Event Handlers
mqttc.on_connect = on_connect
#mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
  
try:
    # Connect to MQTT Broker
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    
    # Start the network loop
    mqttc.loop_forever()

except Exception as e:
    logging.error(f"MQTT Error: {e}")  
    GPIO.cleanup()
    pca.deinit()
      