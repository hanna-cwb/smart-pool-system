import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# GPIO configuration
GPIO.setmode(GPIO.BCM)
LED_PIN = 16
GPIO.setup(LED_PIN, GPIO.OUT)

# MQTT configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/light"

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed with return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to MQTT Topic: {MQTT_TOPIC} with qos {granted_qos}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    logging.info(f"Message received: {message}")
    
    if message == "on":
        GPIO.output(LED_PIN, GPIO.HIGH)
        logging.info("LED turned ON")
    elif message == "off":
        GPIO.output(LED_PIN, GPIO.LOW)
        logging.info("LED turned OFF")
    else:
        logging.warning(f"Unknown command received: {message}")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set("mqtt-user", "mqtt")
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message

try:
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqttc.loop_forever()

except KeyboardInterrupt:
    logging.info("Measurement stopped by user.")
except Exception as e:
    logging.error(f"MQTT Error: {e}")
finally:
    mqttc.loop_stop()
    mqttc.disconnect()
    GPIO.cleanup()
