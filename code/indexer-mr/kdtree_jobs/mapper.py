import json
import pickle
import sys
from io import BytesIO

buffer = BytesIO()
for data in sys.stdin.buffer:
    buffer.write(data)
buffer.seek(0)
input_feats = pickle.load(buffer)
for k in input_feats:
    val = input_feats[k].tolist()

    print("%s\t%s" % (k, json.dumps(val)))
