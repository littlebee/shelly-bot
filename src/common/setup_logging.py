import os
import sys
import logging

LOG_LEVEL = logging.INFO
env_log_level = os.getenv('LOG_LEVEL')
if env_log_level == 'DEBUG':
    LOG_LEVEL = logging.DEBUG
elif env_log_level == "WARN":
    LOG_LEVEL = logging.WARN


def setup_logging(file_name):
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(filename=file_name,
                        level=LOG_LEVEL,
                        format=log_format)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_handler)
