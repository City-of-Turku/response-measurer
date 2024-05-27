import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] <%(name)s> %(lineno)d: %(message)s',
    handlers=[
        logging.FileHandler('response-measurer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('response-measurer')

def load_settings(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            settings = json.load(file)
    except FileNotFoundError:
        exit("Missing settings file: settings.json")
    return settings
