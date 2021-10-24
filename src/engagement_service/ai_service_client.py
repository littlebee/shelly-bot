import os
import time
import requests
import base64
import traceback
import paths

DEBUG_REQUESTS = os.getenv('DEBUG_REQUESTS') or False
DEBUG_RESPONSES = os.getenv('DEBUG_RESPONSES') or False


def get(endpoint):
    url = f"{paths.AI_SERVICE_URL}{endpoint}"
    if DEBUG_REQUESTS:
        print(f"ai client: requesting {url}")
    started_at = time.time()
    try:
        r = requests.get(url)
    except Exception as e:
        print('ai client: caught error on requests.get')
        print(traceback.format_exc())
        return None

    request_duration = time.time() - started_at
    resp = r.json()
    status = resp['status']
    if DEBUG_REQUESTS or DEBUG_RESPONSES:
        msg_data = {
            'url': url,
            'request_duration': request_duration,
            'total_duration': time.time() - started_at,
            'status': status,
        }
        if DEBUG_RESPONSES:
            msg_data['data'] = resp['data']

        print(f"got response. {msg_data}")

    if is_error_resp(resp, f"failed to get {endpoint}"):
        return None

    return resp


def get_names():
    # gets all of the names and recorded spoken names
    started_at = time.time()
    resp = get('names')

    # reset the data/names directory (rm and recreate)
    os.system(
        f"rm -Rf {paths.NAMES_DATA_DIR} && mkdir -p {paths.NAMES_DATA_DIR}")

    names = []
    for nameMeta in resp['data']:
        new_name = nameMeta['name']
        content = nameMeta['content']
        new_path = f"{paths.NAMES_DATA_DIR}/{new_name}"
        save_base64_content_as_mp3(content, new_path)
        names.append(new_name)

    duration = time.time() - started_at
    print(f"ai client: fetched and saved {len(names)} names in {duration}s")
    return names


def get_next_faces():
    return get('nextFaces')


def get_new_face():
    # remove and recreate the temp dir for the name
    os.system(
        f"rm -Rf {paths.TMP_DATA_DIR} && mkdir -p {paths.TMP_DATA_DIR}")
    return get('newFace')


def get_spoken_name():
    resp = get('acquireSpokenName')
    if not resp:
        return False

    save_base64_content_as_mp3(resp['data'], paths.TMP_DATA_DIR)
    return True


def get_images():
    return get('acquireImages')


def get_save_face():
    resp = get('saveNewFace')
    if not resp:
        return False

    name = resp['data']

    # move any mp3 we got for get_spoken_name into the correct
    # location in the names directory
    new_name_dir = f"{paths.NAMES_DATA_DIR}/{name}"
    os.system(f"mkdir -p {new_name_dir}")
    os.system(f"cp {paths.TMP_NAME_FILE} {new_name_dir}")

    return name


def get_ping():
    return get('ping')


def is_error_resp(resp, log_msg):
    if not resp or resp['status'] != 'ok':
        print(f"ai client: {log_msg}.  status: {resp and resp['status']}")
        return True

    return False


def save_base64_content_as_mp3(content, path):
    os.system(f"mkdir -p {path}")
    base64_bytes = content.encode()
    binary = base64.b64decode(base64_bytes)
    with open(f"{path}/name.mp3", 'wb') as file:
        file.write(binary)
