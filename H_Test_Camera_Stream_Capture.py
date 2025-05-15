"""
Camara Testing Script using OpenCV and Flask Web Sever

Author: Patrick Dz.
Date: 12.03.2025

Added Capture and distance sensor

Author Hermine
Date 08.05.2025
"""

import cv2
import time
import threading
from datetime import datetime
from picamera2 import Picamera2
from flask import Flask, Response, jsonify

# Load the Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the Raspberry Pi camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 30
picam2.configure("preview")
picam2.start()

time.sleep(2)  # Allow camera to warm up

# Initialize Flask app
app = Flask(__name__)

# Shared variable for the current frame
current_frame = None
frame_lock = threading.Lock()

# Function to generate frames for the video stream
def generate_frames():
    global current_frame
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        
        # Convert to grayscale for face detection
        # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  
        # Detect faces
        # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        # Draw rectangles around faces
        # for (x, y, w, h) in faces:
        #    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        with frame_lock:
            current_frame = frame.copy()

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        # Convert to byte array
        frame = buffer.tobytes()
        
        # Yield the frame in a format that can be streamed over HTTP
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Route to stream the video
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# Route to capture foto
@app.route('/capture')
def capture_manual():
    return save_current_frame("manual")

# frame saving
def save_current_frame(source):
    with frame_lock:
        if current_frame is None:
            return jsonify({"error": "No frame available"}), 500
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"capture_{source}_{timestamp}.jpg"
        cv2.imwrite(filename, current_frame)
        print(f"[{source.upper()}] Foto gespeichert: {filename}")
        return jsonify({"message": f"Photo saved as {filename}"}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)