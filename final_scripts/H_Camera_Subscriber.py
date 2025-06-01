import cv2
import time
import threading
from datetime import datetime
from picamera2 import Picamera2
from flask import Flask, Response
import paho.mqtt.client as mqtt
import logging
import os
import base64

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MQTT Configuration
MQTT_HOST = "192.168.8.137"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 5
MQTT_TOPIC = "/sensor/distance"
MQTT_IMG_TOPIC = "/sensor/images"

# Directory for saving photos
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "Images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Load the Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the Raspberry Pi camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")
picam2.start()
time.sleep(2)

# Initialize Flask app
app = Flask(__name__)

# Shared variable for the current frame
current_frame = None
frame_lock = threading.Lock()

# Generate frame for capturing
def generate_frame():
    global current_frame
    
    frame = picam2.capture_array(wait=True)
    with frame_lock:
        current_frame = frame.copy()

# Generate frames for the video stream
def generate_frames():
    global current_frame
    while True:
        frame = picam2.capture_array(wait=True)

        with frame_lock:
            current_frame = frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        frame = buffer.tobytes()
        
        # Yield the frame in a format that can be streamed over HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Define MQTT Event Handlers
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker successfully")
        if MQTT_TOPIC:
            client.subscribe(MQTT_TOPIC, qos=0)
        else:
            logging.warning("MQTT_TOPIC is empty. Subscription skipped.")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    logging.info(f"Subscribed to MQTT Topic: {MQTT_TOPIC} with QoS {granted_qos}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if message == "Capture":
        print("Received message: Capture")
        save_current_frame("mqtt_trigger")
    logging.info(f"Received Message: {msg.payload.decode()} from Topic: {msg.topic}")

def on_publish(client, userdata, mid):
    logging.info("Message Published successfully")

# Initialize MQTT Client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
mqttc.username_pw_set(username="mqtt-user", password="mqtt")
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
mqttc.on_publish = on_publish

def publish_image(filepath):
    with open(filepath, "rb") as img:
        b64img = base64.b64encode(img.read()).decode()
        mqttc.publish(MQTT_IMG_TOPIC, b64img)

# Frame saving
def save_current_frame(source):
    global current_frame
    
    generate_frame()
    with frame_lock:
        if current_frame is None:
            logging.warning("No frame available after calling generate_frames()")
            return
        logging.info("Frame now available")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{source}_{timestamp}.jpg"
        filepath = os.path.join(IMAGE_FOLDER, filename)
        
        success = cv2.imwrite(filepath, current_frame)

        logging.info(f"Foto saved at {filepath}")
        if success:
            publish_image(filepath)
            return filename
        else:
            logging.error("Error while saving foto")
            return False

# Define MQTT start
def start_mqtt():
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

# Route to stream the video
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app and MQTT
if __name__ == '__main__':
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
