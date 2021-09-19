"""

This class engages with the huuuumans.

When face_detect.py detects new new_faces, the thread this class creates responds
in several ways.

If a single unidentified face is in the new_faces data, start the process of gathering
their name and images of them to be used to retrain the ML model.

Unless the above info gathering process is running, give shout outs to any
new_faces that are recognized and identified from previous gathering + retraining .
"""
import os
from sys import path
import time
import threading
import cv2
from face_recognition.api import face_locations

import paths
import speech
import faces
from trainer import Trainer
from hearing import listen_for_name


class Engagement:
    thread = None  # background thread that reads new_faces detected
    face_detect = None
    trainer = Trainer()

    # array of {"name": "face_24", "aabb": (267, 460, 329, 398)}
    # used to augment_frame
    last_known_faces = []
    # where we are in the engagement process
    status = "starting"
    # if we are engaging, the current face frame
    engagement_face = None

    # these are used for Engagement.stats()
    started_at = 0
    # total saved since started
    frames_saved = 0
    # new new_faces saved for current new face engagement
    new_frames_saved = 0
    # new_faces added to data since start
    faces_saved = 0
    # number of times we attempted to capture a single face during new engagement
    attempted_captures = 0
    # number of successful single face captures
    actual_captures = 0
    # number of recognized new_faces
    recognized_faces = 0

    def __init__(self, face_detect):
        Engagement.face_detect = face_detect
        if Engagement.thread is None:
            Engagement.thread = threading.Thread(target=self._thread)
            Engagement.thread.start()

    def augment_frame(self, frame):
        status = Engagement.status
        color = (0, 255, 255)

        if status == "engaging":
            color = (0, 255, 0)
            (top, right, bottom, left) = Engagement.engagement_face
            cv2.rectangle(frame, (left, top),
                          (right, bottom), color, 2)
        else:
            for known_face in Engagement.last_known_faces:
                name = known_face["name"]
                (top, right, bottom, left) = known_face["aabb"]
                # Draw a box around the face
                cv2.rectangle(frame, (left, top),
                              (right, bottom), color, 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                            .6, color, 2)

            cv2.putText(frame, status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        .8, color, 2)
        return frame

    @classmethod
    def stats(cls):
        now = time.time()
        captureRate = 0
        if cls.attempted_captures > 0:
            captureRate = cls.actual_captures / cls.attempted_captures

        return {
            "totalTime": now - cls.started_at,
            "framesSaved": cls.frames_saved,
            "newFramesSaved": cls.new_frames_saved,
            "facesSaved": cls.faces_saved,
            "capturesAttempted": cls.attempted_captures,
            "capturesSuccess": cls.actual_captures,
            "captureSuccessRate": captureRate,
            "recognizedFaces": cls.recognized_faces
        }

    @classmethod
    def _thread(cls):
        print('Starting engagement thread.')
        cls.started_at = time.time()

        while True:
            cls.status = "getting new faces"
            new_faces = cls.face_detect.get_faces()
            frame = cls.face_detect.last_frame
            cls.status = "getting names for faces"
            names = cls.get_names_for_faces(new_faces, frame)
            cls.status = "analyzing"
            num_names = len(names)
            if len(new_faces) == 1 and num_names == 0:
                cls.engagement_face = new_faces[0]
                cls.status = "engaging"
                cls.engage_new_face(new_faces[0], frame)
            elif num_names > 0:
                cls.recognized_faces += num_names

            cls.status = "resting"
            time.sleep(0.1)

    @classmethod
    def get_names_for_faces(cls, new_faces, frame):
        # get frame, run face detection on it and update Engagement.face
        encodingData = cls.trainer.get_encodings_data()

        cls.face_detect.pause()
        encodings = faces.face_encodings(frame, new_faces)
        names = []
        cls.last_known_faces = []

        # attempt to match each face in the input image to our known encodings
        for index, encoding in enumerate(encodings):
            matches = faces.compare_faces(encodingData["encodings"], encoding)
            cls.face_detect.resume()

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
                cls.last_known_faces .append({
                    "name": name,
                    "aabb": new_faces[index]
                })
                cls.status = "greeting"
                speech.say_hello(names)

        cls.face_detect.resume()
        print(f"found known faces: {names}")

        return names

    @ classmethod
    def engage_new_face(cls, face, frame):
        print(f"Engaging new face: {face}")

        os.system(f"rm -Rf {paths.TMP_DATA_DIR}/*")
        cls.new_frames_saved = 0

        cls.save_face_in_frame(face, frame)
        speech.introduce_yourself()
        if not listen_for_name():
            speech.request_name_again()
            if not listen_for_name():
                return

        speech.let_me_get_a_look_at_you()

        for i in range(0, 6):
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
        cls.status = "retraining"
        time.sleep(20)

    @ classmethod
    def save_five_faces(cls):
        print(f"attempting to save 5 face shots...")
        actual_saves = 0
        for i in range(0, 4):
            cls.attempted_captures += 1
            new_faces = cls.face_detect.get_next_faces()
            frame = cls.face_detect.last_frame
            speech.play_camera_snap()
            if len(new_faces) == 1:
                cls.engagement_face = new_faces[0]
                names = cls.get_names_for_faces(new_faces, frame)
                # we need a single unrecognized face
                if len(names) == 0:
                    actual_saves += 1
                    cls.actual_captures += 1
                    cls.save_face_in_frame(new_faces[0], frame)
                else:
                    print(
                        f"face {i} not saved: expected unknown face, got ({names}). ignoring.")
            else:
                print(
                    f"face {i} not saved: expected 1 face, got {len(new_faces)}. ignoring.")

        return actual_saves

    @ classmethod
    def save_face_in_frame(cls, face, frame):
        path = f"{paths.TMP_DATA_DIR}/frame_{cls.new_frames_saved}.jpg"
        top, right, bottom, left = face
        image = frame[top:bottom, left:right]
        cv2.imwrite(path, image)
        print(f"saved face {path}")

        cls.frames_saved += 1
        cls.new_frames_saved += 1

    @ classmethod
    def create_face_files(cls):
        face_number = len(os.listdir(paths.FACES_DATA_DIR))
        new_face_name = f"face_{face_number}"
        new_face_path = f"{paths.FACES_DATA_DIR}/{new_face_name}"

        os.system(f"mkdir -p {new_face_path}")
        os.system(f"cp -a {paths.TMP_DATA_DIR}/* {new_face_path}")

        cls.faces_saved += 1

        return new_face_name
