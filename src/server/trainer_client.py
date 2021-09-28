"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import time
import threading
import websocket  # websocket-client pip

import paths


class TrainerClient:
    thread = None  # background thread that reads faces detected
    times_read = 0
    started_at = 0

    # used by stats()
    # time that
    last_retrain_time = 0
    ws = None

    def __init__(self):
        if TrainerClient.thread is None:
            TrainerClient.thread = threading.Thread(target=self._thread)
            TrainerClient.thread.start()

        self.ws = websocket.WebSocket()

    # Returns the last encoding data without waiting for any
    # retraining in progress

    def get_encodings_data(self):
        return TrainerClient.encodings_data

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
    def retrain_model(self):
        ws.send

    @classmethod
    def stats(cls):
        return {
            "lastRetrainTime": cls.last_retrain_time
        }

    @classmethod
    def _thread(cls):
        print('Starting encoding file watch thread.')
        cls.started_at = time.time()

    @classmethod
    def connect_to_service(cls):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://echo.websocket.org/",
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run
