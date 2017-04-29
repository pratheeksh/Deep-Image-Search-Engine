import getpass
import hashlib

MAX_PORT = 49123
MIN_PORT = 10000
HOSTNAME = "http://localhost"
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
            (MAX_PORT - MIN_PORT) + MIN_PORT + 100
NUM_INDEX_SERVERS = 20
NUM_TXT_INDEX_SERVERS = 10
NUM_DOC_SERVERS = 10
MAX_NUM_RESULTS = 30
INDEX_SERVER_PORTS = []
TXT_INDEX_SERVER_PORTS = []
DOC_SERVER_PORTS = []
TXT_MULT = 20
TO_DISPLAY = 10
TITLE_BONUS = 10.0
WORKER_THREAD_COUNT = 10
WORKER_PORTS = []
DOCS_STORE = "data/biggertest/docs/docshard_%d.p"
TREE_STORE = "data/biggertest/features"
TEXT_STORE = "data/biggertest/indices"
IM_RESIZE_DIMS = (227, 227)
NUM_KD_TREES = 3
WEBAPP_PATH = "static/"

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
    for i in range(NUM_TXT_INDEX_SERVERS):
        port = BASE_PORT + NUM_INDEX_SERVERS + NUM_DOC_SERVERS + WORKER_THREAD_COUNT + i + 1
        TXT_INDEX_SERVER_PORTS.append(port)
    print("Frontend port: {}".format(BASE_PORT))
    print("Index server ports: {}".format(INDEX_SERVER_PORTS))
    print("Doc server ports: {}".format(DOC_SERVER_PORTS))
    print("Worker ports: {}".format(WORKER_PORTS))
    print("Index txt server ports: {}".format(TXT_INDEX_SERVER_PORTS))

if __name__ == "__main__":
    init_ports()
