import json
import pickle

import numpy as np
from tornado import web
from code import inventory


class Index(web.RequestHandler):
    def initialize(self, shard_id):
        self.kd_tree_dict = pickle.load(open(inventory.TREE_STORE + "/pca_" + str(shard_id) + ".out", "rb"))
        self.file_names = list(self.kd_tree_dict.keys())[0].split()
        self.kd_tree = self.kd_tree_dict[list(self.kd_tree_dict.keys())[0]]
        self.pca = pickle.load(open(inventory.TREE_STORE + "/pca_model_" + str(shard_id) + ".out", "rb"))

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(self.pca.transform(feature_vector), k=10)
        return scores.flatten(), keys.flatten()

    def head(self):
        self.finish()

    def get(self):

        query = json.loads(self.get_argument('featvec', ''))
        query = query[1:len(query)-1]
        featvec = [float(x) for x in query.split(',')]
        scores, keys = self.get_knn_image_feats(featvec)
        top_k_scores = []
        for i in range(len(scores)):
            # top_k_scores.append((scores[i], self.file_names[keys[i]]))
            key = self.file_names[keys[i]]
            key = int(key.split(".")[0])
            top_k_scores.append((key, scores[i]))
        results = sorted(top_k_scores)
        self.finish(json.dumps({'postings': results[:max(len(results), inventory.MAX_NUM_RESULTS)]}))
