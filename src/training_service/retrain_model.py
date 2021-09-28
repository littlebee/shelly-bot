# /usr/bin/env python3
import os
import time
import json
import pickle
import cv2
from imutils import paths as imutils_paths

import commons.paths as paths
import commons.faces as faces

last_modified = 0
times_read = 0

# default initial encodings data in case a client calls
# get_encodings_data() before the pickle finishes loading
# on startup
encodings_data = {"encodings": [], "names": []}



def retrain_model():
    image_paths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))
    image_paths.sort()
    processed_paths = []
    if os.path.exists(paths.TRAINER_PROCESSED_FILE_PATH):
        with open(paths.TRAINER_PROCESSED_FILE_PATH, 'r') as file:
            processed_paths = json.load(file)["directories"]

    encodings_data = {
        "encodings": [],
        "names": []
    }
    if os.path.exists(paths.ENCODINGS_FILE_PATH):
        encodings_data = pickle.loads(
            open(paths.ENCODINGS_FILE_PATH, "rb").read(), encoding='latin1')

    time_started = time.time()
    images_already_processed = 0
    new_images_processed = 0
    # loop over the image paths
    for (i, image_path) in enumerate(image_paths):
        if image_path in processed_paths:
            images_already_processed += 1
            # print(f"skipping already processed path {image_path}")
            continue

        new_images_processed += 1
        processed_paths.append(image_path)
        # extract the person name from the image path
        print(f"retrain_model: processing image path {image_path}")
        name = image_path.split(os.path.sep)[-2]

        image = cv2.imread(image_path)
        face_locations = faces.face_locations(image)
        if len(face_locations) == 1:
            top, right, bottom, left = face_locations[0]
            image = image[top:bottom, left:right]
            # convert from BGR (OpenCV ordering) to RGB
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # compute the facial embedding for the face
            encodings = faces.face_encodings(rgb, face_locations)

            for encoding in encodings:
                encodings_data["encodings"].append(encoding)
                encodings_data["names"].append(name)

    run_time = time.time() - time_started
    fps = new_images_processed / run_time
    print(
        f"retrain_model: skipped {images_already_processed} images already in encodings")
    print(
        f"retrain_model: processed {new_images_processed} new images in {run_time}s.  ({fps} fps)")

    # save encodings data in pickle file for faster start up
    f = open(paths.ENCODINGS_FILE_PATH, "wb")
    f.write(pickle.dumps(encodings_data))
    f.close()

    f = open(paths.TRAINER_PROCESSED_FILE_PATH, "w")
    f.write(json.dumps({"directories": processed_paths}))
    f.close()


if __name__ == '__main__':
    load_encodings_from_file()
    retrain_model()
