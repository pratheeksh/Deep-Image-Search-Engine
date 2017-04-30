import json
import pickle
import sys

import numpy as np
from scipy.spatial import KDTree

sys.setrecursionlimit(10000)
feats = []
keys = []
data = map(lambda x: x.strip().split('\t'), sys.stdin)
for k, feat_vecs in data:
    try:
        feat_vecs = np.array(json.loads(feat_vecs))
        feats.append(feat_vecs)
        keys.append(k)
    except:
        continue
feats = np.array(feats)
T = KDTree(np.array(feats), leafsize=20)
pickle.dump({" ".join(keys): T}, sys.stdout.buffer)
