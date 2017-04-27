# Lists all keys in the feature vector pickle files

import pickle
import os

path = '/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/biggertest/features'
for f in os.listdir(path):
    data = pickle.load(open(os.path.join(path, f), 'rb'))
    keys = sorted(list(data.keys()))
    print("Keys for feature pickle file {}".format(f))
    print(keys)