import os

KEYS_FILE_NAME = 'keys'
WYKOP_APP_KEY = 'aNd401dAPp'  # official wykop app key (from android app)
BASE_DIR = os.getcwd()
LOG_DIR = f'{BASE_DIR}/logs'
REPOSITORY_DIR = f'{BASE_DIR}/db'
LOG_FILE = f'{LOG_DIR}/wykop-taktyk.log'
REPOSITORY_FILE = f'{REPOSITORY_DIR}/observations.db'
