#!/usr/bin/env python3
import os
import time
import cv2
import pickle
import face_recognition
import numpy

# last n seconds to use for fps calc
FPS_WINDOW = 60

# if true, use face_recognition.face_distance to determin known faces
USE_FACE_DISTANCE = os.getenv('USE_FACE_DISTANCE') == '1' or False

if USE_FACE_DISTANCE:
    print('Using face_distance to determine known faces')


class FpsStats(object):
    def __init__(self):
        self.start()

    # can call start after init, or pause and start for more accuracy
    def start(self):
        self.started_at = time.time()
        self.total_frames = 0
        self.floating_frames_count = 0
        self.floating_started_at = time.time()
        self.last_floating_fps = 0

    def increment(self):
        self.total_frames += 1
        self.floating_frames_count += 1

        fps_time = time.time() - self.floating_started_at
        if fps_time > FPS_WINDOW:
            self.last_floating_fps = self.floating_frames_count / fps_time
            self.floating_started_at = time.time()
            self.floating_frames_count = 0
            print(f"fps: {self.last_floating_fps}")

    def stats(self):
        now = time.time()
        total_time = now - self.started_at
        return {
            "totalFramesRead": self.total_frames,
            "totalTime": total_time,
            "overallFps": self.total_frames / total_time,
            "fpsStartedAt": self.floating_started_at,
            "floatingFps": self.last_floating_fps
        }


print('initializing VideoCapture')
camera = cv2.VideoCapture(0)  # , apiPreference=cv2.CAP_V4L2)
if not camera.isOpened():
    raise RuntimeError('Could not start camera.')

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

encodings_data = pickle.loads(
    open("data/encodings.pickle", "rb").read(), encoding='latin1')

fps_stats = FpsStats()

try:
    while True:
        _, img = camera.read()
        if img is None:
            print(
                "The camera has not read data, please check whether the camera can be used normally.")
            print(
                "Use the command: 'raspistill -t 1000 -o image.jpg' to check whether the camera can be used correctly.")
            break

        fps_stats.increment()

        new_faces = face_recognition.face_locations(img)
        num_new_faces = len(new_faces)
        print(f"found {num_new_faces} faces")

        names = []
        if num_new_faces > 0:
            encodings = face_recognition.face_encodings(img, new_faces)
            for encoding in encodings:
                if USE_FACE_DISTANCE:
                    face_distances = face_recognition.face_distance(
                        encodings_data["encodings"], encoding)
                    best_match_index = numpy.argmin(face_distances)
                    if face_distances[best_match_index] < 0.65:
                        names.append(encodings_data["names"][best_match_index])
                else:
                    matches = face_recognition.compare_faces(
                        encodings_data["encodings"], encoding)
                    # check to see if we have found a match
                    if True in matches:
                        matched_indexes = [
                            i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        for i in matched_indexes:
                            name = encodings_data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

                        # determine the recognized face with the largest number of votes
                        names.append(max(counts, key=counts.get))

        print(f"recognized {len(names)} faces")
except KeyboardInterrupt:
    pass

print('')
print(fps_stats.stats())
