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
MQTT_TOPIC = "/sensor/waterlevel"
MQTT_TOPIC_PUMP = "/sensor/pumpStatus"

# Threshold for waterlevel detection in cm
WATERLEVEL_THRESHOLD = 15

# Hardware Setup
SERVO_CHANNEL = 1

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50

# Servo Control Function
def set_servo_pulse(pca, channel, pulse_us):
    pulse_length = 1000000
    pulse_length //= pca.frequency
    pulse_scale = 65535 / pulse_length
    pwm_value = int(pulse_us * pulse_scale)
    pca.channels[channel].duty_cycle = pwm_value

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed with return code {rc}")

def on_message(client, userdata, msg):
    try:
        dist = float(msg.payload.decode())
        logging.info(f"Received distance: {dist} cm")
        if dist > WATERLEVEL_THRESHOLD:
            logging.info("Low water level - turning pump ON")
            mqttc.publish(MQTT_TOPIC_PUMP, "pump on")
            set_servo_pulse(pca, SERVO_CHANNEL, 1520)
        else:
            logging.info("High water level - turning pump OFF")
            mqttc.publish(MQTT_TOPIC_PUMP, "pump off")
            set_servo_pulse(pca, SERVO_CHANNEL, 1570)
    except ValueError:
        logging.error("Invalid distance value received.")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_forever()

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    set_servo_pulse(pca, SERVO_CHANNEL, 1570)
    pca.deinit()
    mqttc.loop_stop()
    mqttc.disconnect()