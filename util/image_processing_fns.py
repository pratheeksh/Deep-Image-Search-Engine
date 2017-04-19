import os
import io
from io import BytesIO
import pickle
import PIL
from PIL import Image as PImage
import re
from pprint import pprint
import numpy as np
from IPython.display import Image, display

def resizeImage(image, size):
    image.thumbnail(size, PIL.Image.ANTIALIAS)
    return image

def resizeImageAlt(image, size):
    newim = image.resize(size, resample=PIL.Image.LANCZOS)
    return newim

def getImage(filename, path):
    fullname = os.path.join(path, filename)
    im = PImage.open(fullname)
    im.load()
    return im

def showImage(filename, path):
    fullname = os.path.join(path, filename)
    display(Image(filename=fullname))

def convertImageToArray(image):
    im_array = np.asarray(image, dtype="float64")
    return im_array

def checkImagePIL(array):
    array = np.asarray(array, dtype="uint8")
    im = PImage.fromarray(array, 'RGB')
    im.show()
    
def displayImageInline(array):
    array = np.asarray(array, dtype="uint8")
    im = PImage.fromarray(array, 'RGB')
    bio = BytesIO()
    im.save(bio, format='png')
    display(Image(bio.getvalue(), format='png', embed=True))

def check_and_pad(array, dims):
    print(array.shape)
    print(dims)
    pass