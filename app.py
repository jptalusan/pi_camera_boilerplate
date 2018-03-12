#!/usr/bin/env python
from importlib import import_module
import os
import time, datetime
from flask import Flask, render_template, Response
import paho.mqtt.client as mqtt
import base64
import json
from flask_socketio import SocketIO

latest_timestamp = ""

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

async_mode = None

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
broker_address="localhost"
client = mqtt.Client("P1") #create new instance
client.connect(broker_address) #connect to broker

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def capture_frame(frame):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S')
    global latest_timestamp
    if latest_timestamp != st:
        latest_timestamp = st
    else:
        return
    #fileName = latest_timestamp
    fileName = 'test.jpg'

    send_data = base64.b64encode(frame)
    base64_string = send_data.decode('utf-8')
    data = {"image": base64_string, "time_sent": latest_timestamp}
    client.publish('image/file', json.dumps(data))
    #client.publish('image/file', latest_timestamp)

test = True
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if toggle == True:
            capture_frame(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

toggle = False

@socketio.on('button_pressed')
def handle_mqtt_unsubscribe(data):
    print("Button pressed!")
    global toggle
    toggle = not toggle

if __name__ == '__main__':
    #app.run(host='192.168.2.7', port=5000, threaded=True)
    socketio.run(app, host='192.168.2.7', port=5000, debug=True, use_reloader=True)
