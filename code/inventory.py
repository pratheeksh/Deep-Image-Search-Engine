import getpass
import hashlib

MAX_PORT = 49123
MIN_PORT = 10000
#HOSTNAME = "http://localhost"
HOSTNAME =  "http://ec2-54-200-53-153.us-west-2.compute.amazonaws.com"
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
            (MAX_PORT - MIN_PORT) + MIN_PORT

NUM_INDEX_SERVERS = 25
NUM_TXT_INDEX_SERVERS = 10
NUM_DOC_SERVERS = 10
MAX_NUM_RESULTS = 30
INDEX_SERVER_PORTS = []
TXT_INDEX_SERVER_PORTS = []
DOC_SERVER_PORTS = []
TXT_MULT = 20
TO_DISPLAY = 10
TITLE_BONUS = 10.0
WORKER_THREAD_COUNT = 8
WORKER_PORTS = []

'''
DOCS_STORE = "data/biggertest/docs/docshard_%d.p"
TREE_STORE = "data/biggertest/features"
TEXT_STORE = "data/biggertest/indices"
'''
DOCS_STORE = "data/FlickrData2/docs/docshard_%d.p"
TREE_STORE = "data/FlickrData2/features/new_feats"
TEXT_STORE = "data/FlickrData2/indices"
IM_RESIZE_DIMS = (227, 227)
# NUM_KD_TREES = 3
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
