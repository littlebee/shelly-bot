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
import face_recognition
import cv2

from event import Event


class FaceDetect:
    thread = None  # background thread that reads frames from camera
    camera = None
    faces = []
    last_frame = []
    frames_read = 0
    started_at = 0
    last_dimensions = {}

    event = Event()

    def __init__(self, camera):
        FaceDetect.camera = camera
        if FaceDetect.thread is None:
            FaceDetect.thread = threading.Thread(target=self._thread)
            FaceDetect.thread.start()

    def get_faces(self):
        return FaceDetect.faces

    def get_next_faces(self):
        FaceDetect.event.wait()
        FaceDetect.event.clear()
        return self.get_faces()

    def augment_frame(self, frame):
        # Display the results
        for top, right, bottom, left in FaceDetect.faces:
            # Draw a box around the face
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (0, 0, 255), 2)
        return frame

    @classmethod
    def _thread(cls):
        print('Starting face detection thread.')
        FaceDetect.started_at = time.time()

        while True:
            # get frame, run face detection on it and update FaceDetect.faces
            FaceDetect.last_frame = FaceDetect.camera.get_frame()
            FaceDetect.faces = face_recognition.face_locations(
                FaceDetect.last_frame)
            FaceDetect.frames_read += 1
            FaceDetect.last_dimensions = FaceDetect.last_frame.shape

            FaceDetect.event.set()  # send signal to clients

            print(f"Detected faces: {FaceDetect.faces}")
            time.sleep(0)
