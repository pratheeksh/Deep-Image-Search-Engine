import os
import numpy as np
from util.image_processing_fns import *

MAX_IMS_PER_ARRAY = 100
IM_PATH = '/Users/lauragraesser/Google Drive/NYU_Courses/sea-project/data/test/images/'
NUMPY_PATH = '/Users/lauragraesser/Google Drive/NYU_Courses/sea-project/data/test/images_numpy/'
IM_RESIZE_DIMS = (128, 128)
START_IM_NUM = 1
END_IM_NUM = 570

def convertImsToArray(path, start, end):
    print("Processing images from {} to {}".format(start, end))
    ims_as_arrays = []
    for i in range(start, end):
        filename = str(i) + ".jpg"
        im = getImage(filename, path)
        imr = resizeImageAlt(im, IM_RESIZE_DIMS)
        ima = convertImageToArray(imr)
        ima = check_and_pad(ima, IM_RESIZE_DIMS)
        assert ima.shape == (IM_RESIZE_DIMS[0], IM_RESIZE_DIMS[1], 3)
        ims_as_arrays.append(ima)
        if (i % 100 == 0):
            print('%d images processed' % i)
    ims_as_arrays_tuple = tuple(ims_as_arrays)
    im_array = np.stack(ims_as_arrays_tuple)
    return im_array


start = 1
end = min(start + MAX_IMS_PER_ARRAY, END_IM_NUM)
matrix_num = 0
while start < END_IM_NUM:
    array = convertImsToArray(IM_PATH, start, end)
    print(array.shape)
    fname = str(matrix_num)
    np.save(os.path.join(NUMPY_PATH, fname), array)
    print("Saved image matrix {}".format(matrix_num))
    matrix_num += 1 
    start = end
    end = min(start + MAX_IMS_PER_ARRAY, END_IM_NUM)

