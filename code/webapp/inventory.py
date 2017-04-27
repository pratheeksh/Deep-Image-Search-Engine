import hashlib, getpass

NUM_INDEX_SHARDS = 1
NUM_DOC_SHARDS = 10
MAX_PORT = 49152
MIN_PORT = 10000
BASE_PORT = int(hashlib.md5(getpass.getuser().encode()).hexdigest()[:8], 16) % \
    (MAX_PORT - MIN_PORT) + MIN_PORT

servers = {}
servers['web'] = ["127.0.0.1:%d" % (BASE_PORT)]
servers['index'] = ["127.0.0.1:%d" % (port)
  for port in range(BASE_PORT + 1,
                    BASE_PORT + 1 + NUM_INDEX_SHARDS)]
servers['doc'] = ["127.0.0.1:%d" % (port)
  for port in range(BASE_PORT + 1 + NUM_INDEX_SHARDS,
                    BASE_PORT + 1 + NUM_INDEX_SHARDS + NUM_DOC_SHARDS)]

DOCS_STORE = "data/test/docs/docshard_%d.p"
TREE_STORE = "data/test/trees/%d.p"
#WEBAPP_PATH = "webapp/"
IM_RESIZE_DIMS = (227, 227)
WEBAPP_PATH = "static/"
