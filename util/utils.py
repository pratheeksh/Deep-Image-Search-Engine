import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms
from torch.autograd import Variable
import numpy as np

# From https://discuss.pytorch.org/t/how-to-extract-features-of-an-image-from-a-trained-model/119/3
def load_model():
    model = models.alexnet(pretrained=True)
    # remove last fully-connected layer
    new_classifier = nn.Sequential(*list(model.classifier.children())[:-1])
    model.classifier = new_classifier
    model = model.float()
    print(model)
    return model

def load_object_model():
    # Placeholder for more powerful model
    # Testing logic works
    model = models.alexnet(pretrained=True)
    model = model.float()
    print(model)
    return model

def check_and_pad(im, im_resize_dims):
    if im.ndim < 3 or not im.shape[2] == 3:
        if im.ndim < 3:
            im = np.expand_dims(im, axis=2)
        if im.shape[2] >= 3:
            print("Error")
            return -1
        else:
            pad = np.zeros((im_resize_dims[0], im_resize_dims[1], 3 - im.shape[2]))
            im = np.concatenate((im, pad), axis=2)
            return im
    return im

def normalize(data):
    transform = transforms.Normalize(
                    mean = [ 0.485, 0.456, 0.406 ],
                    std = [ 0.229, 0.224, 0.225 ])
    return transform(data).float()

def convert_array_to_Variable(array):
    array = array.astype('d')
    array = array / 255
    array = torch.from_numpy(array)
    array = normalize(array)
    return Variable(array)