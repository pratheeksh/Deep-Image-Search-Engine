import os, json

from tornado import web
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import linear_kernel

class Index(web.RequestHandler):
    def initialize(self, data):
        self._posting_lists = data

    def head(self):
        self.finish()

    def get(self):
        query = self.get_argument('query', '')
        id = self.get_argument('id', 1)
        # load the kd tree 
        data = pickle.load(open(inventory.TREE_STORE % (id), 'rb'))
        print("Tree loaded")
        self.finish(json.dumps({'postings': postings}))

