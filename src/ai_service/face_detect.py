"""
This class detects faces in frames it gets from the camera object passed to
the constructor.

The get_faces method returns the bounding boxes for all faces last detected.

A thread is created that does the heavy lifting of detecting faces and updates
a class var that contains the last faces detected. This allows the thread providing
the video feed to stream at 30fps while face frames lag behind at 3fps (maybe upto 10?)
"""
import os
import time
import threading
import cv2
from face_recognition.api import face_distance
import numpy

# import faces
import face_recognition
from fps_stats import FpsStats


# if true, use face_recognition.face_distance to determin known faces
USE_FACE_DISTANCE = os.getenv('USE_FACE_DISTANCE') == '1' or False

if USE_FACE_DISTANCE:
    print('Using face_distance to determine known faces')


class FaceDetect:
    thread = None  # background thread that reads frames from camera
    camera = None
    last_faces = []
    last_frame = []
    fps_stats = FpsStats()
    last_dimensions = {}
    total_faces_detected = 0

    detected_event = threading.Event()
    pause_event = threading.Event()

    def __init__(self, camera, trainer):
        FaceDetect.trainer = trainer
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
        for face in self.get_faces():
            name = face["name"]
            top, right, bottom, left = face["aabb"]
            color = (0, 0, 255)

            if name != 'unknown':
                color = (255, 0, 0)

            # Draw a box around the face
            cv2.rectangle(frame, (left, top),
                          (right, bottom), color, 2)

            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        .4, color, 1)
        return frame

    def pause(self):
        FaceDetect.pause_event.clear()

    def resume(self):
        FaceDetect.pause_event.set()

    @classmethod
    def stats(cls):
        return {
            "lastDimensions": cls.last_dimensions,
            "fps": cls.fps_stats.stats(),
            "total_faces_detected": cls.total_faces_detected
        }

    @classmethod
    def _thread(cls):
        print('Starting face detection thread.')
        cls.fps_stats.start()

        # start running on start
        cls.pause_event.set()

        while True:
            cls.pause_event.wait()
            # get frame, run face detection on it and update FaceDetect.last_faces
            frame = cls.last_frame = cls.camera.get_frame()

            # Not sure why but the recommended change below caused it to perform worse.
            # I don't think it's necessary if the model is also trained with BGR images?

            # Resize frame of video to 1/4 size
            # Convert the image from BGR color
            # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # rgb_small_frame = frame[:, :, ::-1]

            new_faces = face_recognition.face_locations(frame)

            cls.last_faces = cls.get_names_for_faces(new_faces, cls.last_frame)

            cls.fps_stats.increment()
            cls.last_dimensions = cls.last_frame.shape

            num_faces = len(cls.last_faces)
            if num_faces > 0:
                cls.detected_event.set()  # send signal to clients
                cls.total_faces_detected += num_faces

            time.sleep(0)

    @classmethod
    def get_names_for_faces(cls, new_faces, frame):

        encodingData = cls.trainer.get_encodings_data()
        encodings = face_recognition.face_encodings(frame, new_faces)

        named_faces = []

        # attempt to match each face in the input image to our known encodings
        for index, encoding in enumerate(encodings):
            name = 'unknown'
            if USE_FACE_DISTANCE:
                face_distances = face_recognition.face_distance(
                    encodingData["encodings"], encoding)
                best_match_index = numpy.argmin(face_distances)
                if face_distances[best_match_index] < 0.65:
                    name = encodingData["names"][best_match_index]
            else:
                matches = face_recognition.compare_faces(
                    encodingData["encodings"], encoding)
                # check to see if we have found a match
                if True in matches:
                    matched_indexes = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matched_indexes:
                        name = encodingData["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number of votes
                    name = max(counts, key=counts.get)

            named_faces.append({
                "name": name,
                "aabb": new_faces[index]
            })

        print(f"found faces: {named_faces}")

        return named_faces
