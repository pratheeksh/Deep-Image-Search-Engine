import getpass
import hashlib

MAX_PORT = 49123
MIN_PORT = 10000
HOSTNAME = "http://localhost"
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
            (MAX_PORT - MIN_PORT) + MIN_PORT
NUM_INDEX_SERVERS = 10
NUM_DOC_SERVERS = 10
MAX_NUM_RESULTS = 10
INDEX_SERVER_PORTS = []
DOC_SERVER_PORTS = []
TITLE_BONUS = 10.0
WORKER_THREAD_COUNT = 10
WORKER_PORTS = []


def init_ports():
    for i in range(NUM_INDEX_SERVERS):
        port = BASE_PORT + i + 1
        INDEX_SERVER_PORTS.append(port)
    for i in range(NUM_DOC_SERVERS):
        port = BASE_PORT + NUM_INDEX_SERVERS + i + 1
        DOC_SERVER_PORTS.append(port)
    for i in range(WORKER_THREAD_COUNT):
        port = BASE_PORT + NUM_INDEX_SERVERS + NUM_DOC_SERVERS + i + 1
        WORKER_PORTS.append(port)


if __name__ == "__main__":
    init_ports()
