import torch
import torch.utils.data as data
from PIL import Image
import os
import os.path
import errno
import torch
import json
import codecs
import numpy as np
from torchvision import transforms
from os import listdir
from os.path import isfile, join


class FLICKR(data.Dataset):
    raw_folder = 'raw'

    processed_folder = 'processed'
    training_file = 'training.pt'
    test_file = 'test.pt'
    def __init__(self, root, train=True, transform=None, target_transform=None, download=False):
	print("Loading data from {}".format( root))
	self.root = root
        self.transform = transform
        self.target_transform = target_transform
        self.train = train  # training set or test set	
	if not self._check_exists():
            raise RuntimeError('Dataset not found.' +
                               ' You can use download=True to download it')
	if self.train:
            self.train_data = self.__getfiles__(root, 'im')
	    self.index = self.train_data.keys()
	    self.train_captions = self.__getfiles__(root + '/meta/tags/', 'tags') 
           
        else:
            self.test_data, self.test_labels = torch.load(os.path.join(root, self.processed_folder, self.test_file))

    def __getitem__(self, i):
        index = self.index[i]
	if self.train:
            img, caption  = self.__readimage__(self.train_data[index]), self.__readtext__(self.train_captions[index])
	    if self.transform is not None:
		img = img.resize((500,500), Image.BILINEAR)
		img = self.transform(img)
	return img, 1

    def __readimage__(self, filename):
	img = Image.open(filename).convert('RGB')	
	return img

    def __readtext__(self, filename):
	with open (filename, "r") as myfile:
            data=myfile.readlines()
        return data

    def __len__(self):
	if self.train:
            return 25000
        else:
            return 10000
	
    def __getfiles__(self, root, extn):
        l = len(extn)
        files = {}
	for f in listdir(root):
	    if isfile(join(root, f)):
	       id = f.split('.')[0][l:]
	       files[id] =  join(root, f) 
	return files


    def _check_exists(self):
	return os.path.exists(self.root)

def main():
    flickr_dataset = FLICKR(os.environ['dataset'], transform=transforms.Compose([
                       transforms.ToTensor()
                   ]))
    '''
    for i, index in enumerate(flickr_dataset.index):
        img, caption = flickr_dataset.__getitem__(i)
        print(img.size)
main()
`'''
