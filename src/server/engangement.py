"""

This class engages with the huuuumans.

When face_detect.py detects new faces, the thread this class creates responds
in several ways.

If a single unidentified face is in the faces data, start the process of gathering
their name and images of them to be used to retrain the ML model.

Unless the above info gathering process is running, give shout outs to any
faces that are recognized and identified from previous gathering + retraining .
"""
import os
from sys import path
import time
import threading
import face_recognition
import cv2

import paths
import speech
from event import Event
from trainer import Trainer
from hearing import listen_for_name


class Engagement:
    thread = None  # background thread that reads faces detected
    frames_read = 0
    started_at = 0
    face_detect = None
    trainer = Trainer()
    # total saved since started
    faces_saved = 0
    # new faces saved for current new face engagement
    new_faces_saved = 0
    # array of {"name": "face_24", "aabb": (267, 460, 329, 398)}
    last_known_faces = []

    def __init__(self, face_detect):
        Engagement.face_detect = face_detect
        if Engagement.thread is None:
            Engagement.thread = threading.Thread(target=self._thread)
            Engagement.thread.start()

    def augment_frame(self, frame):
        # Display the results
        for known_face in Engagement.last_known_faces:
            name = known_face["name"]
            (top, right, bottom, left) = known_face["aabb"]
            # Draw a box around the face
            cv2.rectangle(frame, (left, top),
                          (right, bottom), (0, 255, 255), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        .8, (0, 255, 255), 2)
        return frame

    @classmethod
    def _thread(cls):
        print('Starting engagement thread.')
        cls.started_at = time.time()

        while True:
            faces = cls.face_detect.get_next_faces()
            frame = cls.face_detect.last_frame
            names = cls.get_names_for_faces(faces, frame)

            cls.frames_read += 1

            if len(faces) == 1 and len(names) == 0:
                cls.engage_new_face(faces[0], frame)
            else:
                for name in names:
                    speech.say_hello(name)

            time.sleep(0)

    @classmethod
    def get_names_for_faces(cls, faces, frame):
        # get frame, run face detection on it and update Engagement.face
        encodingData = cls.trainer.get_encodings_data()

        encodings = face_recognition.face_encodings(frame, faces)
        names = []
        known_faces = []

        # attempt to match each face in the input image to our known encodings
        for index, encoding in enumerate(encodings):
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
                known_faces.append({
                    "name": name,
                    "aabb": faces[index]
                })

        print(f"found known faces: {known_faces}")
        cls.last_known_faces = known_faces

        return names

    @classmethod
    def engage_new_face(cls, face, frame):
        print(f"Engaging new face: {face}")

        os.system(f"rm -Rf {paths.TMP_DATA_DIR}/*")
        cls.new_faces_saved = 0

        cls.save_face_in_frame(face, frame)
        speech.introduce_yourself()
        if not listen_for_name():
            speech.request_name_again()
            if not listen_for_name():
                return

        speech.let_me_get_a_look_at_you()

        for i in range(0, 8):
            print(f"capturing images. round {i}")
            speech.pose_for_me()
            num_saved = cls.save_five_faces()
            if num_saved == 0:
                speech.where_did_you_go()
                num_saved = cls.save_five_faces()
                if num_saved == 0:
                    speech.rejection()
                    return

        name = cls.create_face_files()
        speech.nice_to_meet_you(name)

        cls.trainer.trigger_retrain()

        time.sleep(20)

    @classmethod
    def save_five_faces(cls):
        print(f"attempting to save 5 face shots...")
        actual_saves = 0
        for i in range(0, 4):
            faces = cls.face_detect.get_next_faces()
            frame = cls.face_detect.last_frame
            speech.play_camera_snap()
            if len(faces) == 1:
                names = cls.get_names_for_faces(faces, frame)
                # we need a single unrecognized face
                if len(names) == 0:
                    actual_saves += 1
                    cls.save_face_in_frame(faces[0], frame)
                else:
                    print(
                        f"face {i} not saved: expected unknown face, got ({names}). ignoring.")
            else:
                print(
                    f"face {i} not saved: expected 1 face, got {len(faces)}. ignoring.")

        return actual_saves

    @classmethod
    def save_face_in_frame(cls, face, frame):
        path = f"{paths.TMP_DATA_DIR}/frame_{cls.new_faces_saved}.jpg"
        top, right, bottom, left = face
        image = frame[top:bottom, left:right]
        cv2.imwrite(path, image)
        print(f"saved face {path}")

        cls.faces_saved += 1
        cls.new_faces_saved += 1

    @classmethod
    def create_face_files(cls):
        face_number = len(os.listdir(paths.FACES_DATA_DIR))
        new_face_name = f"face_{face_number}"
        new_face_path = f"{paths.FACES_DATA_DIR}/{new_face_name}"

        os.system(f"mkdir -p {new_face_path}")
        os.system(f"cp -a {paths.TMP_DATA_DIR}/* {new_face_path}")

        return new_face_name
