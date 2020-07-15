import os
import stat
import platform
import logging

root_dir = os.path.split(os.path.abspath(__file__))[0] + '/'
tmp_dir = 'tmp/'

SAMPLE_RATE = 44100
FRAME_INTERVAL = 50
SAMPLE_GAP = 50000


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def get_file_data(file_path):
    try:
        data = None
        f = open(file_path, 'r')
        if f is not None:
            data = f.read()
            f.close()

        if data is not None:
            return data.strip()
        else:
            return None
    except Exception as e:
        logging.error(e, exc_info=True)
        return None
