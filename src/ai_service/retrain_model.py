# /usr/bin/env python3
import os
import time
import logging

import cv2
import face_recognition

import multiprocessing as mp
from imutils import paths as imutils_paths

from ai_service import paths

logger = logging.getLogger(__name__)


def train_images(image_paths, queue):
    returnVal = []
    for image_path in image_paths:
        returnVal.append(train_image(image_path, queue=queue))
    logger.info(f"train_images: {returnVal}")
    return returnVal


def train_image(image_path, queue):

    # extract the person name from the image path
    name = image_path.split(os.path.sep)[-2]
    encodings_data = {
        "encodings": [],
        "name": name,
        "image_path": image_path
    }

    logger.info(f"train_image: {image_path}")
    image = cv2.imread(image_path)
    face_locations = face_recognition.face_locations(image)
    for top, right, bottom, left in face_locations:
        frame = image[top:bottom, left:right]
        # Resize frame of video to 1/4 size
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color
        rgb_frame = frame[:, :, ::-1]
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb_frame)
        for encoding in encodings:
            encodings_data["encodings"].append(encoding)

    if queue:
        queue.put(encodings_data)
        return None
    else:
        return encodings_data


if __name__ == '__main__':
    image_paths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))
    image_paths.sort()
    started_at = time.time()
    num_procs = int(os.getenv("NUM_PROCS") or '4')

    mp.set_start_method('spawn')

    if os.getenv('USE_MP_POOL') == '1':
        logger.info(f"Using multiprocessing pool with {num_procs} processes")
        with mp.Pool(num_procs) as p:
            p.map(train_image, image_paths)

    elif os.getenv('USE_DIRECT_CALL') == '1':
        logger.info('Using direct call for this process')
        train_images(image_paths)

    else:
        num_images = len(image_paths)

        logger.info(f"Using {num_procs} processes (sans pool)")

        imgs_per_chunk = int(num_images / num_procs)
        leftover_images = num_images % num_procs
        chunks = []
        for i in range(num_procs):
            chunk_start = i * imgs_per_chunk
            chunk = image_paths[chunk_start:chunk_start + imgs_per_chunk]
            logger.info(f"chunk: {chunk}")
            chunks.append(chunk)
        chunks[0] = chunks[0] + image_paths[num_images - leftover_images:]

        chunk_lengths = list(map(lambda chunk: len(chunk), chunks))
        logger.info(f"chunk lengths: {chunk_lengths}")

        processes = []
        for i in range(num_procs):
            p = mp.Process(target=train_images, args=(list(chunks[i]), ))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    total_time = time.time() - started_at
    num_image_paths = len(image_paths)
    logger.info(
        f"\nprocessed {num_image_paths} in {total_time}s  ({num_image_paths / total_time})")
