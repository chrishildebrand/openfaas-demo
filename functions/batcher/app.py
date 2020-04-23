from batcher.rmqbatcher import RMQBatcher
from common import util
import os


if __name__ == '__main__':
    host = os.environ.get('rabbitmq_host')
    port = os.environ.get('rabbitmq_port')
    read_q = os.environ.get('rmq_read_queue')
    write_q = os.environ.get('rmq_write_queue')
    exchange = os.environ.get('rmq_exchange')
    batch_size = int(os.environ.get('batch_size'))
    seconds = int(os.environ.get('batch_seconds'))

    util._setup_logging()

    uname, passw = util._getsecret('rabbitmqcreds').split(':')

    batcher = RMQBatcher(host=host, port=port, uname=uname, passw=passw, run_http_server=True, http_server_port=8080)
    batcher.start(read_queue=read_q, write_queue=write_q, exchange=exchange, batch_size=batch_size, seconds=seconds)