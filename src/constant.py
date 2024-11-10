"""Contains global configurations of this project"""

import os


BASE_DIR = os.path.dirname(__file__)  # e.g. /path-to-project/src

PUBLIC_DIR = f"{BASE_DIR}/../public"  # e.g. /src/../public

LOG_ADDRESS = f"{BASE_DIR}/../requests.log"  # e.g. /src/../file.txt
