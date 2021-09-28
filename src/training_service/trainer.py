"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import os
import time
import threading
import pickle
import json
import numpy

from imutils import paths as imutils_paths
import commons.paths as paths


class Trainer:
    thread = None  # background thread that reads faces detected
    times_read = 0
    started_at = 0
    # default initial encodings data in case a client calls
    # get_encodings_data() before the pickle finishes loading
    # on startup
    encodings_data = {"encodings": [], "names": []}

    # these get saved and restored to data/faces_process.json
    processed_paths = set()

    # used to prompt the trainer thread to run _retrain_model()
    retrain_needed_event = threading.Event()

    # used by stats()
    # time it took to run retrain_model.py in seconds
    last_retrain_duration = 0

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
            "lastRetrainTime": cls.last_retrain_duration
        }

    @classmethod
    def _thread(cls):
        print('Starting encoding file watch thread.')
        Trainer.started_at = time.time()

        # In case a retrain request comes in while loading...
        Trainer.retrain_needed_event.clear()
        cls._load_encodings_from_file()
        cls._load_processed_paths_from_file()

        while True:
            cls.retrain_needed_event.wait()
            cls.retrain_needed_event.clear()
            cls._retrain_model()
            time.sleep(0)

    @classmethod
    def _load_encodings_from_file(cls):
        cls.last_modified = os.path.getmtime(paths.ENCODINGS_FILE_PATH)
        new_encodings_data = pickle.loads(
            open(paths.ENCODINGS_FILE_PATH, "rb").read(), encoding='latin1')

        Trainer.times_read += 1
        cls.encodings_data = new_encodings_data
        print(f"Trainer updated from {paths.ENCODINGS_FILE_PATH}")
        # print(f"encodings data {cls.encodings_data}")

    @classmethod
    def _load_processed_paths_from_file(cls):
        if os.path.exists(paths.TRAINER_PROCESSED_FILE_PATH):
            with open(paths.TRAINER_PROCESSED_FILE_PATH, 'r') as file:
                cls.processed_paths = json.load(file)["paths"]

    @classmethod
    def _retrain_model(cls):
        time_started = time.time()

        unprocessed_paths = cls._get_unprocessed_paths()
        chunks = numpy.array_split(unprocessed_paths, 4)
        print(f"got chunks {chunks}")
        cls.last_retrain_duration = time.time() - time_started

    @classmethod
    def _get_unprocessed_paths(cls):
        image_paths = set(imutils_paths.list_images(paths.FACES_DATA_DIR))
        return list(image_paths - set(cls.processed_paths)).sort()
