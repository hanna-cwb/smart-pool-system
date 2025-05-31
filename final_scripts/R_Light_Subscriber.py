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

# MQTT client configuration
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.username_pw_set("mqtt-user", "mqtt")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker successfully")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed, return code: {rc}")

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

# Register event handlers
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    logging.info("Program stopped by user")
except Exception as e:
    logging.error(f"Error: {e}")
finally:
    GPIO.cleanup()
