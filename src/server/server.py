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
import psutil

from flask import Flask, Response, send_from_directory
from flask_cors import CORS

import cv2
from camera_opencv import Camera
from base_camera import BaseCamera
from face_detect import FaceDetect
from trainer import Trainer
from engagement import Engagement

app = Flask(__name__)
CORS(app, supports_credentials=True)

camera = Camera()
face_detect = FaceDetect(camera)
trainer = Trainer()
# this starts a thread that engages with the huuuumans
engagement = Engagement(camera, face_detect, trainer)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        frame = frame.copy()
        frame = face_detect.augment_frame(frame)
        frame = engagement.augment_frame(frame)
        jpeg = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/stats')
def send_stats():
    return {
        "cpuPercent": psutil.cpu_percent(),

        "capture": BaseCamera.stats(),
        "faceDetect": FaceDetect.stats(),
        "engagement": Engagement.stats(),
        "trainer": Trainer.stats()
    }


@app.route('/pauseEngagement')
def pause_engagement():
    Engagement.pause_engagement()
    return {"status": "paused"}


@app.route('/resumeEngagement')
def resume_engagement():
    Engagement.resume_engagement()
    return {"status": "resumed"}


@app.rount('/retrain')
def retrain():


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
