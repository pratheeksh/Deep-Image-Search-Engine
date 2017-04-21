import json
import pickle
import sys

import numpy as np
from scipy.spatial import KDTree

feats = []
keys = []
data = map(lambda x: x.strip().split('\t'), sys.stdin)
for k, feat_vecs in data:
    feat_vecs = np.array(json.loads(feat_vecs))
    feats.append(feat_vecs)
    keys.append(k)
feats = np.array(feats)
T = KDTree(np.array(feats))
pickle.dump(dict(" ".join(keys), T), sys.stdout.buffer)
