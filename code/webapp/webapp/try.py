import cv2
from skimage import io as skimageio
from skimage.transform import resize
from code.cnn_feature_extractor import create_feature_matrix


IM_RESIZE_DIMS = (227, 227)
image_url='http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/queries/103100.png'
im = skimageio.imread(image_url)
print("Loaded image size", im.shape)
ima = resize(im, IM_RESIZE_DIMS)

print("resized image size", ima.shape)
batch = [ima] 

feature_vector = create_feature_matrix(batch, 10)
