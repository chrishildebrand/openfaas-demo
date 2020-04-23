import logging

def _getsecret(secret):
    with open("/var/openfaas/secrets/%s" % secret, 'r') as secretfile:
        secret_line = secretfile.readline()
    return secret_line

class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        return not (record.name == 'batcher.rmqbatcher' and 'GET /_/health HTTP/1.1' in record.msg)

def _setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    ch.addFilter(HealthCheckFilter())

    logger.addHandler(ch)