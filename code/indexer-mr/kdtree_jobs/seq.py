import os
import pickle
import sys

import numpy as np
from scipy.spatial import KDTree

sys.setrecursionlimit(10000)

input_dir = "/home/ubuntu/SEA-Project/data/FlickrData2/features"

files = [f for f in os.listdir(os.path.join(os.curdir, input_dir)) if '.in' in os.path.splitext(f)]
start = 0
for i in range(25):
    files_of_interest = files[start: start + 20]
    feats = []
    keys = []
    print("files processed ",len(files_of_interest), start, start+20)
    for input_file in files_of_interest:
        data = pickle.load(open(input_dir + "/" + input_file, "rb"))
        for k in data:
            try:
                feats.append(data[k])
                keys.append(k)
            except:
                continue
    feats = np.array(feats)
    T = KDTree(np.array(feats), leafsize=20)
    pickle.dump({" ".join(keys): T}, open( str(i) + ".out", "wb"))
    start += 20
    print(start)
