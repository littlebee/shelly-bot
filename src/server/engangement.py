"""

This class engages with the huuuumans.

When face_detect.py detects new faces, the thread this class creates responds
in several ways.

If a single unidentified face is in the faces data, start the process of gathering
their name and images of them to be used to retrain the ML model.

Unless the above info gathering process is running, give shout outs to any
faces that are recognized and identified from previous gathering + retraining .
"""
import time
import threading
import face_recognition
import cv2

from event import Event
from encodings_file import EncodingsFile
from speech import Speech
from hearing import listen_for_name


class Engagement:
    thread = None  # background thread that reads faces detected
    frames_read = 0
    started_at = 0
    face_detect = None
    encodingsFile = None

    def __init__(self, face_detect):
        Engagement.face_detect = face_detect
        if Engagement.thread is None:
            Engagement.thread = threading.Thread(target=self._thread)
            Engagement.thread.start()

        if Engagement.encodingsFile is None:
            Engagement.encodingsFile = EncodingsFile()

    @classmethod
    def _thread(cls):
        print('Starting engagement thread.')
        Engagement.started_at = time.time()

        while True:
            faces = Engagement.face_detect.get_next_faces()
            frame = Engagement.face_detect.last_frame
            names = Engagement.get_names_for_faces(faces, frame)

            Engagement.frames_read += 1

            if len(faces) == 1 and len(names) == 0:
                Engagement.engage_new_face(faces[0], frame)
            else:
                for name in names:
                    Speech.say_hello(name)

            time.sleep(0)

    @classmethod
    def get_names_for_faces(cls, faces, frame):
        # get frame, run face detection on it and update Engagement.face
        encodingData = Engagement.encodingsFile.get_encodings_data()

        encodings = face_recognition.face_encodings(frame, faces)
        names = []

        # attempt to match each face in the input image to our known encodings
        for encoding in encodings:
            matches = face_recognition.compare_faces(encodingData["encodings"],
                                                     encoding)
            # check to see if we have found a match
            if True in matches:
                matched_indexes = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matched_indexes:
                    name = encodingData["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of votes
                name = max(counts, key=counts.get)

                # update the list of matched names
                names.append(name)

        return names

    @classmethod
    def engage_new_face(cls, face, frame):
        print(f"Engaging new face: {face}")

        Speech.introduce_yourself()
        if not listen_for_name():
            Speech.request_name_again()
            if not listen_for_name():
                return
