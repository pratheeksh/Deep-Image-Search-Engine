import os, json
import pickle
from . import inventory
from tornado import web
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import linear_kernel
from util.utils import load_model, convert_array_to_Variable

kd_tree_base = "data/test/features"


class Query:
    def __init__(self, shard_id):
        self.kd_tree_dict = pickle.load(open(kd_tree_base + "/" + str(shard_id) + ".out", "rb"))
        self.file_names = list(self.kd_tree_dict.keys())[0].split()
        self.kd_tree = self.kd_tree_dict[list(self.kd_tree_dict.keys())[0]]

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(feature_vector, k=10)
        # top_k = {self.file_names[i]: self.feat_vecs[i] for i in keys}
        return scores, keys

class Index(web.RequestHandler):
    def initialize(self, model):
        self.model = model
        print("Model loaded ")


    def head(self):
        self.finish()

    def get_feature_vector(self, image_url):
        from skimage import io as skimageio
        from skimage.transform import resize

         # read the image from the url  and resize HW to (227, 227)
        im = skimageio.imread(image_url)
        print("Loaded image size", im.shape)
        image = resize(im, inventory.IM_RESIZE_DIMS)
        image =  np.transpose(image, (2, 0, 1))
        image = convert_array_to_Variable(np.array([image]))
        # pass a batch with just the queried image to alexnet
        feature_vector = self.model(image)
        print("Generated feature vector of size {}".format(feature_vector.data.numpy().shape))
        return feature_vector.data.numpy().reshape((4096,))

    def get(self):
        print("Received a Index request")
        query = self.get_argument('q', '')
        id = 1 #self.get_argument('id', 1)
        print("Image url queried {}".format(query))
        feat = self.get_feature_vector(query)
        query_obj = Query(id)
        scores, keys = query_obj.get_knn_image_feats(feat)
        print("Size of returned results {}".format(scores))
        top_k_scores = []
        for i in range(len(scores)):
            top_k_scores.append((scores[i], query_obj.file_names[keys[i]]))
        results = sorted(top_k_scores)
        self.finish(json.dumps({'postings': results[:10]}))

