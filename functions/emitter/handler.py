import base64
from datetime import datetime
import pika
import json
import os
import logging

try:
    from common import util
except ModuleNotFoundError:
    from .common import util

util._setup_logging()

def _send(exchange, routing_key, data, uname, passw, host, port):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.PlainCredentials(uname, passw))
    )
    channel = connection.channel()
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=data)
    connection.close()

def handle(req):
    uname, passw = util._getsecret('rabbitmqcreds').split(':')
    host = os.environ.get('rabbitmq_host')
    port = os.environ.get('rabbitmq_port')
    write_q = os.environ.get('rmq_write_queue')
    exchange = os.environ.get('rmq_exchange')

    message = "The current time is: %s " % datetime.now().isoformat()

    logging.getLogger(__name__).info("Submitting message: '%s'" % message)

    encoded_messages = [base64.b64encode(message.encode()).decode()]
    json_str = json.dumps(encoded_messages, indent=2)
    _send(exchange=exchange, routing_key=write_q, data=json_str.encode(), uname=uname, passw=passw, host=host, port=port)

    return json_str