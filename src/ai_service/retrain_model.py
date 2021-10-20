# /usr/bin/env python3
import os
import time
import json
import pickle
import cv2
import face_recognition
from imutils import paths as imutils_paths

import paths


def retrain_model():
    image_paths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))
    image_paths.sort()
    processed_paths = []
    if os.path.exists(paths.TRAINER_PROCESSED_FILE_PATH):
        with open(paths.TRAINER_PROCESSED_FILE_PATH, 'r') as file:
            for line in file.readlines():
                processed_paths.append(line.strip())

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
        face_locations = face_recognition.face_locations(image)
        for top, right, bottom, left in face_locations:
            frame = image[top:bottom, left:right]
            # Resize frame of video to 1/4 size
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color
            rgb_small_frame = small_frame[:, :, ::-1]

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb_small_frame)

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

    with open(paths.TRAINER_PROCESSED_FILE_PATH, "w") as file:
        file.write('\n'.join(processed_paths) + '\n')


if __name__ == '__main__':
    retrain_model()
