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
import time
import threading

import paths
import speech

import ai_service_client as ai
# from sensors import camera_distance

# in meters
MAX_DISTANCE_TO_ENGAGE = 1

# minimum number of pixels an unknown face must consume before
# we will engage.  This is about 3% of 640 x 480 on the logitech
# web cam
FACE_AREA_THRESHOLD = 10000

# maximum number of unknown faces, within range as determined above,
# that we will engage as a new face to be added.  The downside to
# more that one face in frame is that we will capture both faces as
# a single person.  The upside is that when people walk up to the
# bot as a couple or threesome (I've learned that's the majority),
# she won't ignore them
MAX_UNKNOWNS_TO_ENGAGE = 3

# number of seconds to sleep when a network error getting data
# from services
SLEEP_ON_SERVICE_ERROR = 2


class Engagement:
    thread = None  # background thread that reads new_faces detected
    head = None
    run_event = threading.Event()

    # where we are in the engagement process
    status = "starting"

    # these are used for Engagement.stats()
    started_at = 0
    last_recognized_at = 0

    def __init__(self, head):
        Engagement.head = head
        if Engagement.thread is None:
            Engagement.thread = threading.Thread(target=self._thread)
            Engagement.thread.start()

    @ classmethod
    def pause_engagement(cls):
        cls.run_event.clear()

    @ classmethod
    def resume_engagement(cls):
        cls.run_event.set()

    @ classmethod
    def stats(cls):
        now = time.time()

        return {
            "totalTime": now - cls.started_at,
            "status": cls.status
        }

    @ classmethod
    def _thread(cls):
        print('Starting engagement thread.')
        cls.started_at = time.time()
        cls.run_event.set()

        print('engagement thread: getting names...')
        ai.get_names()

        while True:
            if not cls.run_event.is_set():
                cls.status = "engagement paused"
                cls.last_known_faces = []
                cls.run_event.wait()

            cls.status = "getting new faces"
            next_faces_resp = ai.get_next_faces()
            if not next_faces_resp:
                # would only not work if the ai service is down
                # give it a rest and try again
                time.sleep(SLEEP_ON_SERVICE_ERROR)
                continue

            next_faces = next_faces_resp['data']
            num_next_faces = len(next_faces)
            print(
                f"engagement thread: got {num_next_faces} next faces: {next_faces}")

            num_known_faces = 0
            unknown_faces = []
            for next_face in next_faces:
                name = next_face['name']
                if name == 'unknown':
                    # ignore faces in the distance; we only care about
                    # those in range based on min area threshold
                    top, right, bottom, left = next_face["aabb"]
                    area = (bottom - top) * (right-left)
                    if area > FACE_AREA_THRESHOLD:
                        unknown_faces.append(next_face)
                    else:
                        print(
                            f"engagement thread: unknown face out of range: {area}sq aabb:{next_face['aabb']} ")
                else:
                    num_known_faces += 1
                    print(f"engagement thread: greeting {name}")
                    speech.say_hello([name])

            num_unknown_faces = len(unknown_faces)
            print(
                f"engagement thread: found {num_known_faces} known faces and {num_unknown_faces} unknown faces within range")

            if num_unknown_faces > 0 and num_unknown_faces <= MAX_UNKNOWNS_TO_ENGAGE:
                cls.engage_new_face()
            #

            #     single_unknown = num_new_faces == 1 and num_names == 0
            #     if camera_distance() <= MAX_DISTANCE_TO_ENGAGE:
            #         if single_unknown:
            #             cls.engagement_face = new_faces[0]
            #             cls.status = "engaging"
            #             cls.engage_new_face(new_faces[0], frame)
            #         elif num_names == 1:
            #             if not last_chatted_with or last_chatted_with != names[0]:
            #                 last_chatted_with = names[0]
            #                 speech.tell_me_a_funny_story(names[0])
            #     elif num_names > 0:
            #         cls.last_recognized_at = time.time()
            #         cls.recognized_faces += num_names
            #     else:
            #         speech.im_bored()
            #         cls.head.scan()
            # else:
            #     speech.im_bored()
            #     cls.head.scan()

            time.sleep(0.1)

    @ classmethod
    def engage_new_face(cls):
        print(f"engagement service: Engaging new face")
        speech.introduce_yourself()
        if not ai.get_spoken_name():
            speech.request_name_again()
            if not ai.get_spoken_name():
                speech.rejection()
                return

        speech.let_me_get_a_look_at_you()

        for i in range(0, 3):
            if not cls.is_still_unknown_face():
                speech.where_did_you_go()
                if not cls.is_still_unknown_face():
                    speech.rejection()
                    return

            print(f"capturing images. round {i}")
            speech.pose_for_me()
            speech.play_camera_snap()
            cls.save_frames(20)

        speech.and_im_spent()
        name = cls.create_face_files()
        speech.nice_to_meet_you(name)

        time.sleep(4)
        speech.i_need_a_nap()
        cls.head.sleep()

        cls.trainer.trigger_retrain()
        cls.status = "retraining"
        time.sleep(20)

    @ classmethod
    def is_still_unknown_face(cls):
        new_faces = cls.face_detect.get_next_faces()
        frame = cls.face_detect.last_frame
        speech.play_camera_snap()
        if len(new_faces) == 1:
            cls.engagement_face = new_faces[0]
            names = cls.get_names_for_faces(new_faces, frame)
            # we need a single unrecognized face
            if len(names) == 0:
                return camera_distance() <= MAX_DISTANCE_TO_ENGAGE

        return False
