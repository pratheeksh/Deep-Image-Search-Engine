import os

import pickle

input_dir = "/home/ubuntu/SEA-Project/data/FlickrData2/features/new_feats"

files = [f for f in os.listdir(os.path.join(os.curdir, input_dir)) if '.out' in os.path.splitext(f)]
total = 0
for f in files:
    obj = pickle.load(open(input_dir + "/" + f, "rb"))
    file_names = list(obj.keys())[0].split()

    print("Num keys in this tree: ", len(file_names))
    total += len(file_names)
print("Total number of files indexed ", total)

