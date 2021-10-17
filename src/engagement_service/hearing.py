import os

import paths
# import shell


# 3 seconds of audio at sample rate of 16000 equals about 96k
# after removing silence, wav file must be at least 15K to be valid
MIN_NAME_FILE_SIZE = 15000
RECORD_CMD = "arecord -d 3 --format=S16_LE --rate=16000 --file-type=wav"
REMOVE_SILENCE_CMD = "util/remove_silence.py 3 "


def listen_for_name():
    cmd = f"{RECORD_CMD} {paths.TMP_RAW_NAME_FILE} && {REMOVE_SILENCE_CMD} {paths.TMP_RAW_NAME_FILE} {paths.TMP_NAME_FILE}"
    os.system(cmd)
    print('hearing listened for name')

    if not os.path.exists(paths.TMP_NAME_FILE):
        return False

    fileSize = os.path.getsize(paths.TMP_NAME_FILE)
    return fileSize >= MIN_NAME_FILE_SIZE
