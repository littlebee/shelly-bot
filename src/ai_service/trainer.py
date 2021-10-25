"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import os
import sys
import time
import threading
import pickle
import numpy
import logging

import multiprocessing as mp
from imutils import paths as imutils_paths
from functools import partial

from ai_service.retrain_model import train_image
from ai_service import paths

# number of retrain processes to launch
NUM_PROCS = 2

logger = logging.getLogger(__name__)


def default_encodings_data():
    return {'encodings': [], 'names': [], 'image_paths': []}


class Trainer:
    thread = None  # background thread that reads faces detected
    times_read = 0
    started_at = 0
    # default initial encodings data in case a client calls
    # get_encodings_data() before the pickle finishes loading
    # on startup
    encodings_data = default_encodings_data()
    # used to prompt the trainer thread to run _retrain_model()
    retrain_needed_event = threading.Event()

    # used by stats()
    # time it took to run retrain_model.py in seconds
    last_retrain_duration = 0
    # time it took to load the encodings from the pickle
    last_load_duration = 0
    # number of images last retrain
    last_num_retrained = 0

    # multiprocessing worker pool and queue allocated at thread start
    pool = None
    result_queue = None

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

    def trigger_retrain_all(self):
        Trainer.encodings_data = default_encodings_data()
        self.trigger_retrain()

    @classmethod
    def stats(cls):
        fps = 0
        if cls.last_retrain_duration > 0:
            fps = cls.last_num_retrained / cls.last_retrain_duration

        return {
            "lastLoad": {
                "duration": cls.last_load_duration,
            },
            "lastRetrain": {
                "duration": cls.last_retrain_duration,
                "count": cls.last_num_retrained,
                "fps": fps
            },
            "totals": {
                "encodings": len(cls.encodings_data['encodings']),
                "uniqueFaces": len(numpy.unique(numpy.array(cls.encodings_data['names']))),
                "uniqueFiles": len(numpy.unique(numpy.array(cls.encodings_data['image_paths']))),
            }
        }

    @classmethod
    def _thread(cls):
        logger.info('Starting trainer thread.')
        cls.started_at = time.time()

        # In case a retrain request comes in while loading...
        cls.retrain_needed_event.clear()
        cls._load_encodings_from_file()

        cls.pool = mp.Pool(processes=NUM_PROCS)
        cls.result_queue = mp.Manager().Queue()

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

            logger.info(
                f"Trainer updated from {paths.ENCODINGS_FILE_PATH} in {cls.last_load_duration}s")
        logger.info(
            f"loaded {len(cls.encodings_data['encodings'])} encodings, {len(cls.encodings_data['names'])} names, and {len(cls.encodings_data['image_paths'])} image paths")

    @classmethod
    def _save_encodings_to_file(cls):
        logger.info(
            f"saving {len(cls.encodings_data['encodings'])} encodings, {len(cls.encodings_data['names'])} names, and {len(cls.encodings_data['image_paths'])} image paths")
        with open(paths.ENCODINGS_FILE_PATH, 'wb') as fp:
            pickle.dump(cls.encodings_data, fp,
                        protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def _find_untrained_file_paths(cls):
        image_paths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))
        processed_paths = cls.encodings_data['image_paths']
        untrained_paths = [
            value for value in image_paths if value not in processed_paths]
        untrained_paths.sort()
        return untrained_paths

    @classmethod
    def _handle_retrain_result(cls, result):
        if not result:
            return

        logger.info(
            f"got result from queue with {len(result['encodings'])} encodings for {result['name']} at {result['image_path']}")

        if len(result['encodings']) == 0:
            cls.encodings_data['image_paths'].append(result['image_path'])
        else:
            for encoding in result['encodings']:
                cls.encodings_data['encodings'].append(encoding)
                cls.encodings_data['names'].append(result['name'])
                cls.encodings_data['image_paths'].append(
                    result['image_path'])

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
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # os.system(f"python3 {dir_path}/retrain_model.py")

        untrained_file_paths = cls._find_untrained_file_paths()
        num_untrained = len(untrained_file_paths)
        logger.info(f"found {num_untrained} untrained paths")
        # prod_x has only one argument x (y is fixed to 10)
        train_image_partial = partial(train_image, queue=cls.result_queue)
        async_map = cls.pool.map_async(
            train_image_partial, untrained_file_paths)

        while not async_map.ready():
            result = None
            try:
                result = cls.result_queue.get(True, .25)
            except:
                pass
            cls._handle_retrain_result(result)

        while not cls.result_queue.empty():
            cls._handle_retrain_result(cls.result_queue.get())

        cls.last_retrain_duration = time.time() - time_started
        cls.last_num_retrained = num_untrained
        last_retrain_fps = num_untrained / cls.last_retrain_duration
        logger.info(
            f"retraining complete.  duration={cls.last_retrain_duration} fps={last_retrain_fps} ")

        cls._save_encodings_to_file()
