"""

This class engages with the huuuumans.

When face_detect.py detects new new_faces, the thread this class creates responds
in several ways.

If a single unidentified face is in the new_faces data, start the process of gathering
their name and images of them to be used to retrain the ML model.

Unless the above info gathering process is running, give shout outs to any
new_faces that are recognized and identified from previous gathering + retraining .
"""
import sys
import time
import threading
import logging

from engagement_service import speech
from engagement_service import ai_service_client as ai

logger = logging.getLogger(__name__)


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
        logger.info('Starting thread.')
        cls.started_at = time.time()
        cls.run_event.set()

        logger.info('getting names...')

        while not ai.get_names():
            speech.brain_malfunction()
            time.sleep(.25)

        while True:
            if not cls.run_event.is_set():
                cls.status = "engagement paused"
                cls.last_known_faces = []
                cls.run_event.wait()

            cls.status = "getting new faces"
            if cls.is_unknown_face():
                cls.engage_new_face()
            else:
                speech.im_bored()
                cls.head.scan()

            time.sleep(0.1)

    @ classmethod
    def engage_new_face(cls):
        logger.info(f"Engaging new face")
        ai.get_new_face()
        speech.introduce_yourself()
        if not ai.get_spoken_name():
            speech.request_name_again()
            if not ai.get_spoken_name():
                speech.rejection()
                return

        speech.let_me_get_a_look_at_you()

        for i in range(0, 3):
            if not cls.is_unknown_face(greet_known=False):
                speech.where_did_you_go()
                if not cls.is_unknown_face(greet_known=False):
                    speech.rejection()
                    return

            if not ai.get_images():
                speech.brain_malfunction()
                return

            logger.info(f"capturing images. round {i}")
            speech.pose_for_me()
            speech.play_camera_snap()
            time.sleep(1)

        name = ai.get_save_face()
        if not name:
            speech.brain_malfunction()
            return

        speech.and_im_spent()
        speech.nice_to_meet_you(name)

        time.sleep(4)
        speech.i_need_a_nap()
        cls.head.sleep()

        time.sleep(15)

    @ classmethod
    def is_unknown_face(cls, greet_known=True):
        next_faces_resp = ai.get_next_faces()
        if not next_faces_resp:
            speech.brain_malfunction()
            # would only not work if the ai service is down
            # give it a rest and try again
            time.sleep(SLEEP_ON_SERVICE_ERROR)
            return None

        next_faces = next_faces_resp['data']
        num_unknown_faces = cls.get_number_unknown(next_faces, greet_known)
        return num_unknown_faces > 0 and num_unknown_faces <= MAX_UNKNOWNS_TO_ENGAGE

    @classmethod
    def get_number_unknown(cls, next_faces, greet_known=False):
        num_known_faces = 0
        num_unknown_faces = 0
        for next_face in next_faces:
            name = next_face['name']
            if name == 'unknown':
                # ignore faces in the distance; we only care about
                # those in range based on min area threshold
                top, right, bottom, left = next_face["aabb"]
                area = (bottom - top) * (right-left)
                if area > FACE_AREA_THRESHOLD:
                    num_unknown_faces += 1
                else:
                    logger.info(
                        f"unknown face out of range: {area}sq aabb:{next_face['aabb']} ")
            else:
                num_known_faces += 1
                if greet_known:
                    speech.say_hello([name])

        if num_known_faces + num_unknown_faces > 0:
            logger.info(
                f"found {num_known_faces} known faces and {num_unknown_faces} unknown faces within range")
        else:
            logger.debug('found no faces. :(')
        return num_unknown_faces
