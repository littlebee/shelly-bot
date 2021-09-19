"""
This class detects faces in frames it gets from the camera object passed to
the constructor.

The get_faces method returns the bounding boxes for all faces last detected.

A thread is created that does the heavy lifting of detecting faces and updates
a class var that contains the last faces detected. This allows the thread providing
the video feed to stream at 30fps while face frames lag behind at 3fps (maybe upto 10?)
"""
import time
import threading
import cv2

import faces
from event import Event


class FaceDetect:
    thread = None  # background thread that reads frames from camera
    camera = None
    last_faces = []
    last_frame = []
    frames_read = 0
    started_at = 0
    last_dimensions = {}

    detected_event = Event()
    # we don't need the one to many event, a simple event will do
    pause_event = threading.Event()

    def __init__(self, camera):
        FaceDetect.camera = camera
        if FaceDetect.thread is None:
            FaceDetect.thread = threading.Thread(target=self._thread)
            FaceDetect.thread.start()

    def get_faces(self):
        return FaceDetect.last_faces

    def get_next_faces(self):
        FaceDetect.detected_event.wait()
        FaceDetect.detected_event.clear()
        return self.get_faces()

    def augment_frame(self, frame):
        # Display the results
        for top, right, bottom, left in self.get_faces():
            # Draw a box around the face
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (0, 0, 255), 2)
        return frame

    def pause(self):
        FaceDetect.pause_event.clear()

    def resume(self):
        FaceDetect.pause_event.set()

    @classmethod
    def stats(cls):
        now = time.time()
        total_time = now - cls.started_at
        return {
            "lastDimensions": cls.last_dimensions,
            "framesRead": cls.frames_read,
            "totalTime": total_time,
            "fps": cls.frames_read / total_time,
        }

    @classmethod
    def _thread(cls):
        print('Starting face detection thread.')
        cls.started_at = time.time()
        cls.pause_event.set()

        while True:
            # cls.pause_event.wait()
            # get frame, run face detection on it and update FaceDetect.last_faces
            cls.last_frame = cls.camera.get_frame().copy()
            cls.last_faces = faces.face_locations(cls.last_frame)
            cls.frames_read += 1
            cls.last_dimensions = cls.last_frame.shape

            # set the detected_event even if there are no faces so
            # engagement can remove box augmentations
            cls.detected_event.set()  # send signal to clients

            if len(cls.last_faces) > 0:
                print(f"Detected faces: {cls.last_faces}")

            time.sleep(0)
