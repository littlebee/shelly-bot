#!/usr/bin/env python3
"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/app.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""

import os
import threading
import time

from flask import Flask, Response, send_from_directory
from flask_cors import CORS

from camera_opencv import Camera
from base_camera import BaseCamera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
CORS(app, supports_credentials=True)

camera = Camera()


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/stats')
def send_stats():
    now = time.time()
    total_time = now - BaseCamera.started_at
    frames_read = BaseCamera.frames_read
    frames_read_per_second = frames_read / total_time
    return {
        "framesRead": frames_read,
        "totalTime": total_time,
        "framesReadPerSecond": frames_read_per_second,
    }


@app.route('/<path:filename>')
def sendgen(filename):
    return send_from_directory(dir_path, filename)


@app.route('/')
def index():
    return send_from_directory(dir_path, 'index.html')


class webapp:
    def __init__(self):
        self.camera = camera

    def thread(self):
        app.run(host='0.0.0.0', threaded=True)

    def startthread(self):
        # Define a thread for FPV and OpenCV
        fps_threading = threading.Thread(target=self.thread)
        # 'True' means it is a front thread,it would close when the mainloop() closes
        fps_threading.setDaemon(False)
        fps_threading.start()  # Thread starts


flask_app = webapp()
flask_app.startthread()
