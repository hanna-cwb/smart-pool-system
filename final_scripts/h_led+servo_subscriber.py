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
MQTT_TOPIC = "/sensor/ph"

# Hardware Setup
LED_PIN = 17
SERVO_CHANNEL = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=0x41)
pca.frequency = 50

def set_servo_pulse(pca, channel, pulse_us):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= pca.frequency  # us per period
    pulse_scale = 65535 / pulse_length
    pwm_value = int(pulse_us * pulse_scale)
    pca.channels[channel].duty_cycle = pwm_value
    
# Steuerfunktionen
def activate_servo():
    #pca.channels[SERVO_CHANNEL].duty_cycle = 0x6000 #default 0x6000
    set_servo_pulse(pca, SERVO_CHANNEL, 1580)

def deactivate_servo():
    pca.channels[SERVO_CHANNEL].duty_cycle = 0x0000

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    print("MQTT verbunden.")
    client.subscribe("/sensor/ph")
    
def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to MQTT Topic: {MQTT_TOPIC} with QoS {granted_qos}")

def on_message(client, userdata, msg):
    try:
        ph = float(msg.payload.decode())
        print(f"Received: pH = {ph}")
        if ph > 7.24:
            GPIO.output(LED_PIN, GPIO.HIGH)
            activate_servo()
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            deactivate_servo()
    except ValueError:
        print("Unvalid pH-Value.")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
  
try:
    while True:
        # Connect to MQTT Broker
        mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
        mqttc.loop_forever()

      
except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    deactivate_servo()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    pca.deinit()
    mqttc.loop_stop()
    mqttc.disconnect()