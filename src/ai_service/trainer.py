"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import os
import sys
import time
import threading
import pickle

from imutils import paths as imutils_paths
import paths


class Trainer:
    thread = None  # background thread that reads faces detected
    times_read = 0
    started_at = 0
    # default initial encodings data in case a client calls
    # get_encodings_data() before the pickle finishes loading
    # on startup
    encodings_data = {"encodings": [], "names": []}
    # used to prompt the trainer thread to run _retrain_model()
    retrain_needed_event = threading.Event()

    # used by stats()
    # time it took to run retrain_model.py in seconds
    last_retrain_duration = 0
    # time it took to load the encodings from the pickle
    last_load_duration = 0

    def __init__(self):
        if Trainer.thread is None:
            Trainer.thread = threading.Thread(target=self._thread)
            Trainer.thread.start()

    # Returns the last encoding data without waiting for any
    # retraining in progress

    def get_encodings_data(self):
        return Trainer.encodings_data

    # After new data/faces/face-n dirs are added, this method
    # is called.  When the event is set, the trainer thread
    # is either sleeping waiting on the event or currently
    # retraining.
    #
    # It doesn't matter how far ahead or how many times this
    # is called while the trainer is training.  When retraining
    # completes the trainer thread will immediately return from
    # event.wait and retrain again.
    #
    # There is a possibility that the trainer will get a partial
    # set of frames for a face since the Engagement thread is
    # possibly copying files to a face dir, but that should just make
    # for one or two weak / lower confidence face encodings which
    # will self correct on the next iteration of retrain_model()
    def trigger_retrain(self):
        Trainer.retrain_needed_event.set()

    @classmethod
    def stats(cls):
        return {
            "lastRetrainDuration": cls.last_retrain_duration,
            "lastLoadDuration": cls.last_load_duration
        }

    @classmethod
    def _thread(cls):
        print('Starting encoding file watch thread.')
        Trainer.started_at = time.time()

        # In case a retrain request comes in while loading...
        Trainer.retrain_needed_event.clear()
        Trainer._load_encodings_from_file()

        while True:
            cls.retrain_needed_event.wait()
            cls.retrain_needed_event.clear()
            cls._retrain_model()
            time.sleep(0)

    @classmethod
    def _load_encodings_from_file(cls):
        if os.path.exists(paths.ENCODINGS_FILE_PATH):
            time_started = time.time()
            cls.last_modified = os.path.getmtime(paths.ENCODINGS_FILE_PATH)
            new_encodings_data = pickle.loads(
                open(paths.ENCODINGS_FILE_PATH, "rb").read(), encoding='latin1')

            cls.times_read += 1
            cls.encodings_data = new_encodings_data
            cls.last_load_duration = time.time() - time_started

            print(
                f"Trainer updated from {paths.ENCODINGS_FILE_PATH} in {cls.last_load_duration}s")

    @classmethod
    def _retrain_model(cls):
        time_started = time.time()
        # calling the retrain_model function directly from
        # this thread and process caused a seg fault.
        # I suspect that calling face_locations() and
        # face_encodings() from face_recognition package
        # are not thread safe.
        #
        # See comment on this commit:
        # https://github.com/littlebee/shelly-bot/commit/1d18f1d26bdc0912bafb0fb7a3e480f88026a29d
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.system(f"python3 {dir_path}/retrain_model.py")
        cls.last_retrain_duration = time.time() - time_started
        cls._load_encodings_from_file()
