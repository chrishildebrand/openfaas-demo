from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import pika
from datetime import datetime
import logging
import time
from functools import partial
import json

class RMQBatcher():
    def __init__(self, host, port, uname, passw, run_http_server=False, http_server_port=80):
        self._host = host
        self._port = port
        self._uname = uname
        self._passw = passw

        self._connection = None

        self._read_channel = None
        self._write_channel = None

        self._num_msg_complete = 0
        self._num_batch_complete = 0

        self._batch_start = None

        if run_http_server:
            self.startThreadedHttpServer(port=http_server_port)

    @property
    def connection(self):
        if self._connection is None or not self._connection.is_open:
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                credentials=pika.PlainCredentials(self._uname, self._passw))
        )
        return self._connection

    @property
    def read_channel(self):
        if self._read_channel is None or not self._read_channel.is_open:
            self._read_channel = self.connection.channel()
        return self._read_channel

    @property
    def write_channel(self):
        if self._write_channel is None or not self._write_channel.is_open:
            self._write_channel = self.connection.channel()
        return self._write_channel

    @property
    def num_msg_complete(self):
        return self._num_msg_complete

    @property
    def num_batch_complete(self):
        return self._num_batch_complete

    @property
    def process_starttime(self):
        return self._process_starttime

    @property
    def elapsed(self):
        if self._batch_start is not None:
            elapsed = datetime.utcnow() - self._batch_start
            elapsed_seconds = elapsed.seconds + (elapsed.microseconds / 1000000)
        else:
            elapsed_seconds = 0.0
        return elapsed_seconds

    @property
    def timed_out(self):
        return self.elapsed > self._seconds

    @property
    def batch_full(self):
        return len(self._batch) >= self._batch_size

    def on_message(self, channel, method_frame, header_frame, body):
        self._batch[method_frame.delivery_tag] = json.loads(body)

        if self.timed_out or self.batch_full:
            self._forward_batch(channel=channel)

    def _forward_batch(self, channel):
        all_messages = [message for message_set in self._batch.values() for message in message_set]
        logging.getLogger(__name__).info("Forwarding %d batched messages after %f seconds." % (len(all_messages), self.elapsed))

        self._send(json.dumps(all_messages, indent=2))
        for delivery_tag in self._batch.keys():
            channel.basic_ack(delivery_tag=delivery_tag)

        self._num_msg_complete += len(all_messages)
        self._num_batch_complete += 1
        self._batch.clear()

        time.sleep(30)
        self._batch_start = datetime.utcnow()
        time.sleep(3)

    def _send(self, message):
        logging.getLogger(__name__).info("Publishing batch to %s/%s" % (self._exchange, self._write_queue))
        self.write_channel.basic_publish(exchange=self._exchange, routing_key=self._write_queue, body=message)

    def start(self, read_queue, write_queue, exchange, batch_size, seconds):

        self._write_queue = write_queue
        self._exchange = exchange
        self._batch_size = batch_size
        self._seconds = seconds

        self._batch = {}

        currTime = datetime.utcnow()
        self._batch_start = currTime
        self._process_starttime = currTime


        logging.getLogger(__name__).info("Consuming from: %s" % read_queue)
        self.read_channel.basic_consume(read_queue, self.on_message)
        try:
            self.read_channel.start_consuming()
        except KeyboardInterrupt:
            self.read_channel.stop_consuming()

        self._connection.close()

    class StatusRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, batcher, *args, **kwargs):
            self._batcher = batcher
            super().__init__(*args, **kwargs)

        def do_GET(self):
            self.send_response(200)
            self.end_headers()

            self.wfile.write(("Processed %d messages in %d batches since %s." % (self._batcher.num_msg_complete, self._batcher.num_batch_complete, self._batcher.process_starttime)).encode())

        def do_POST(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(("Processed %d messages in %d batches since %s." % (self._batcher.num_msg_complete, self._batcher.num_batch_complete, self._batcher.process_starttime)).encode())

        def log_message(self, format, *args):
            logger = logging.getLogger(__name__)
            logger.info("%s - %s" % (self.address_string(), format % args))

    def runHttpServer(self, port=80):
        handler = partial(RMQBatcher.StatusRequestHandler, self)
        server = HTTPServer(('0.0.0.0', port), handler)

        logging.getLogger(__name__).info("Starting HTTP server on port %d." % port)
        server.serve_forever()

    def startThreadedHttpServer(self, port=80):
        http_thread = threading.Thread(target=self.runHttpServer, args=(port,), daemon=True)
        http_thread.start()