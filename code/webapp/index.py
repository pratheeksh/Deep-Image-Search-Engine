import json
import pickle

import numpy as np
from tornado import web
from code import inventory
kd_tree_base = inventory.TREE_STORE


class Index(web.RequestHandler):
    def initialize(self, shard_id):
        self.kd_tree_dict = pickle.load(open(kd_tree_base + "/" + str(shard_id) + ".out", "rb"))
        self.file_names = list(self.kd_tree_dict.keys())[0].split()
        self.kd_tree = self.kd_tree_dict[list(self.kd_tree_dict.keys())[0]]

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(feature_vector, k=10)
        return scores, keys

    def head(self):
        self.finish()

    def get(self):
        print("Received a Index request")
        query = json.loads(self.get_argument('q', ''))
        # id = 1  # self.get_argument('id', 1)
        scores, keys = self.get_knn_image_feats(np.fromstring(query))
        print("Size of returned results {}".format(scores))
        top_k_scores = []
        for i in range(len(scores)):
            top_k_scores.append((scores[i], self.file_names[keys[i]]))
        results = sorted(top_k_scores)
        self.finish(json.dumps({'postings': results[:10]}))
