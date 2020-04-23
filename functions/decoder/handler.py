import logging
import json
import base64

try:
    from common import util
except ModuleNotFoundError:
    from .common import util

util._setup_logging()

def handle(req):
    json_data = json.loads(req)
    for entry in json_data:
        decoded = base64.b64decode(entry).decode()
        logging.getLogger(__name__).info(decoded)

    return decoded