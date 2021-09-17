"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import os
import time
import threading
import pickle

import face_recognition
import cv2
from imutils import paths as imutils_paths
import paths

ENCODINGS_FILE_PATH = "data/encodings.pickle"


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
        Trainer.last_modified = os.path.getmtime(ENCODINGS_FILE_PATH)
        new_encodings_data = pickle.loads(
            open(ENCODINGS_FILE_PATH, "rb").read(), encoding='latin1')

        Trainer.times_read += 1
        Trainer.encodings_data = new_encodings_data
        print(f"Trainer updated from {ENCODINGS_FILE_PATH}")

    @classmethod
    def _retrain_model(cls):
        imagePaths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))

        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []

        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("trainer: processing image {}/{}".format(i + 1,
                                                           len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            # images are already cropped to a single face
            image = cv2.imread(imagePath)
            # convert from BGR (OpenCV ordering) to RGB
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb)

            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

        new_encodings_data = {"encodings": knownEncodings, "names": knownNames}

        # save encodings data in pickle file for faster start up
        f = open(ENCODINGS_FILE_PATH, "wb")
        f.write(pickle.dumps(new_encodings_data))
        f.close()

        # this is a reference assignment and should be
        # atomic.  when complete, the client(s) will
        # get updated encodings data via get_encodings_data()
        cls.encodings_data = new_encodings_data
