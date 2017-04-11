import os
from os import listdir
from os.path import isfile, join

mypath = os.environ['dataset']
print("Loading files from path {}", mypath)
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print(onlyfiles)



