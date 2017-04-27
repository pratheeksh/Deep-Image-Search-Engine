import os
import numpy as np
from util.image_processing_fns import *
from util.utils import *
import argparse
import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--im_path', default='/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/test/images', type=str)
parser.add_argument('--npy_path', default='/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/test/images_numpy', type=str)
parser.add_argument('--im_per_array', default=100, type=int)
parser.add_argument('--start_im', default=1, type=int)
parser.add_argument('--end_im', default=570, type=int)
parser.add_argument('--im_resize', default=227, type=int)
opt = parser.parse_args()
print("-------------------Settings-----------------------")
pprint.pprint(opt)
print("-----------------------------------------------------")

MAX_IMS_PER_ARRAY = opt.im_per_array
IM_PATH = opt.im_path
NUMPY_PATH = opt.npy_path
IM_RESIZE_DIMS = (opt.im_resize, opt.im_resize)
START_IM_NUM = opt.start_im
END_IM_NUM = opt.end_im

def convertImsToArray(path, start, end):
    print("Processing images from {} to {}".format(start, end))
    ims_as_arrays = []
    for i in range(start, end):
        filename = str(i) + ".jpg"
        im = getImage(filename, path)
        imr = resizeImageAlt(im, IM_RESIZE_DIMS)
        ima = convertImageToArray(imr)
        ima = check_and_pad(ima, IM_RESIZE_DIMS)
        if ima.shape != (IM_RESIZE_DIMS[0], IM_RESIZE_DIMS[1], 3):
            print("WARNING: Missing image, indexes wont match")
            continue
        ims_as_arrays.append(ima)
        if (i % 100 == 0):
            print('%d images processed' % i)
    ims_as_arrays_tuple = tuple(ims_as_arrays)
    im_array = np.stack(ims_as_arrays_tuple)
    return im_array


start = 1
end = min(start + MAX_IMS_PER_ARRAY, END_IM_NUM + 1)
matrix_num = 0
while start < END_IM_NUM:
    array = convertImsToArray(IM_PATH, start, end)
    print(array.shape)
    fname = str(matrix_num)
    np.save(os.path.join(NUMPY_PATH, fname), array)
    print("Saved image matrix {}".format(matrix_num))
    matrix_num += 1 
    start = end
    end = min(start + MAX_IMS_PER_ARRAY, END_IM_NUM + 1)

