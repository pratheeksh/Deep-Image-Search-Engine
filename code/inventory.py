import getpass
import hashlib

MAX_PORT = 49123
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
            (MAX_PORT - MIN_PORT) + MIN_PORT
NUM_VEC_INDEX_SERVERS = 10
NUM_OBJ_INDEX_SERVERS = 10
NUM_TXT_INDEX_SERVERS = 10
NUM_DOC_SERVERS = 10
MAX_NUM_RESULTS = 10
INDEX_VEC_SERVER_PORTS = []
INDEX_OBJ_SERVER_PORTS = []
INDEX_TXT_SERVER_PORTS = []
DOC_SERVER_PORTS = []
TITLE_BONUS = 10.0

WORKER_THREAD_COUNT = 10
WORKER_PORTS = []
NUM_KD_TREES = 3 # Not sure which counter does what so defined my own

def init_ports():
    for i in range(NUM_VEC_INDEX_SERVERS):
        port = BASE_PORT + i + 1
        INDEX_VEC_SERVER_PORTS.append(port)
    for i in range(NUM_OBJ_INDEX_SERVERS):
        port = BASE_PORT + NUM_VEC_INDEX_SERVERS + i + 1
        INDEX_OBJ_SERVER_PORTS.append(port)
    for i in range(NUM_TXT_INDEX_SERVERS):
        port = BASE_PORT + NUM_VEC_INDEX_SERVERS + \
               NUM_OBJ_INDEX_SERVERS + i + 1
        INDEX_TXT_SERVER_PORTS.append(port)
    for i in range(NUM_DOC_SERVERS):
        port = BASE_PORT + NUM_VEC_INDEX_SERVERS + \
               NUM_OBJ_INDEX_SERVERS + \
               NUM_TXT_INDEX_SERVERS + i + 1
        DOC_SERVER_PORTS.append(port)
    for i in range(WORKER_THREAD_COUNT):
        port = BASE_PORT + NUM_VEC_INDEX_SERVERS + \
               NUM_OBJ_INDEX_SERVERS + \
               NUM_TXT_INDEX_SERVERS + \
               DOC_SERVER_PORTS +i + 1
        WORKER_PORTS.append(port)



def main():
    init_ports()
    print("Base port: {}".format(BASE_PORT))
    print("Index vec servers: {}".format(INDEX_VEC_SERVER_PORTS))
    print("Index object servers: {}".format(INDEX_OBJ_SERVER_PORTS))
    print("Index text servers: {}".format(INDEX_TXT_SERVER_PORTS))
    print("Doc servers: {}".format(DOC_SERVER_PORTS))
    print("Max num results: {}".format(MAX_NUM_RESULTS))
    print("Title boost: {}".format(TITLE_BONUS))


if __name__ == "__main__":
    main()
