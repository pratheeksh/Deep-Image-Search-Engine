import pickle
import pprint

data = pickle.load(open("/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/biggertest/docs/docshard_0.p", 'rb'))
keys = list(data.keys())
keys = sorted(keys)

for i in range(10):
    print("Key = {}".format(keys[i]))
    pprint.pprint(data[keys[i]])


data = pickle.load(open("/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/biggertest/docs/docshard_8.p", 'rb'))
keys = list(data.keys())
keys = sorted(keys)

for i in range(10):
    print("Key = {}".format(keys[i]))
    pprint.pprint(data[keys[i]])