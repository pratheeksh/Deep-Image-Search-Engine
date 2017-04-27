import json
import logging
import os
import pickle
import urllib
from collections import defaultdict
from itertools import chain

import numpy as np
import tornado
from skimage import io as skimageio
from skimage.transform import resize
from tornado import web, gen, process, httpserver, httpclient, netutil
from tornado.ioloop import IOLoop

from util.utils import convert_array_to_Variable
from . import inventory, index, doc

NUM_RESULTS = 10

SETTINGS = {
    "debug": True,
    "static_path": os.path.join(os.path.dirname(__file__), 'static/'),
    "template_path": os.path.join(os.path.dirname(__file__), 'templates/')
}
log = logging.getLogger(__name__)


class Web(web.RequestHandler):
    def initialize(self, model):
        self.model = model

    def head(self):
        self.finish()

    def get_feature_vector(self, image_url):

        im = skimageio.imread(image_url)
        print("Loaded image size", im.shape)
        image = resize(im, inventory.IM_RESIZE_DIMS)
        image = np.transpose(image, (2, 0, 1))
        image = convert_array_to_Variable(np.array([image]))
        # pass a batch with just the queried image to alexnet
        feature_vector = self.model(image)
        print("Generated feature vector of size {}".format(feature_vector.data.numpy().shape))
        return feature_vector.data.numpy().reshape((4096,))

    @gen.coroutine
    def get(self):
        print("Query received")

        q = self.get_argument('img', None)
        if q is None:
            return
        feature_vector = self.get_feature_vector(q)
        # Fetch postings from index servers
        http = httpclient.AsyncHTTPClient()

        responses = yield [http.fetch('http://%s/index?%s' % (server, urllib.parse.urlencode({'q': feature_vector})))
                           for server in inventory.servers['index']]
        # Flatten postings and sort by score
        postings = sorted(chain(*[json.loads(r.body.decode())['postings'] for r in responses]),
                          key=lambda x: -x[0])[:NUM_RESULTS]
        # postings have the format {"postings": [[53.61725232526324, "285.jpg"]} score, id
        print(postings)
        # Batch requests to doc servers
        server_to_doc_ids = defaultdict(list)
        doc_id_to_result_ix = {}
        for i, (_, doc_name) in enumerate(postings):
            doc_id = int(doc_name.split('.')[0])
            doc_id_to_result_ix[doc_id] = i
            server_to_doc_ids[self._get_server_for_doc_id(doc_id)].append(doc_id)
        responses = yield self._get_doc_server_futures(q, server_to_doc_ids)

        # Parse outputs and insert into sorted result array
        result_list = [None] * len(postings)
        for response in responses:
            for result in json.loads(response.body.decode())['results']:
                result_list[doc_id_to_result_ix[int(result['doc_id'])]] = result
        print("Finished retrieving documents", result_list)
        self.write(json.dumps({'num_results': len(result_list), 'results': result_list}))

    def _get_doc_server_futures(self, q, server_to_doc_ids):
        http = httpclient.AsyncHTTPClient()
        futures = []
        for server, doc_ids in server_to_doc_ids.items():
            query_string = urllib.parse.urlencode({'ids': ','.join([str(x) for x in doc_ids]), 'q': q})
            futures.append(http.fetch('http://%s/doc?%s' % (server, query_string)))
        return futures

    def _get_server_for_doc_id(self, doc_id):
        servers = inventory.servers['doc']
        return servers[doc_id % len(servers)]


class IndexDotHTMLAwareStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, path):
        if not path or path.endswith('/'):
            path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(path)


def main():
    num_procs = inventory.NUM_INDEX_SHARDS + inventory.NUM_DOC_SHARDS + 1
    task_id = process.fork_processes(num_procs, max_restarts=0)
    port = inventory.BASE_PORT + task_id
    if task_id == 0:
        app = httpserver.HTTPServer(tornado.web.Application([
            (r'/search', Web),
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": SETTINGS["template_path"],
                                                       "default_filename": "index.html"})
        ], **SETTINGS))
        log.info('Front end is listening on %d', port)
    else:
        if task_id <= inventory.NUM_INDEX_SHARDS:
            shard_ix = task_id - 1
            model = pickle.load(open('data/model.p', 'rb'))
            print("Model loaded ", type(model))
            app = httpserver.HTTPServer(web.Application([(r'/index', index.Index, dict(shard_id=shard_ix))]))
            log.info('Index shard %d listening on %d', shard_ix, port)
        else:
            shard_ix = task_id - inventory.NUM_INDEX_SHARDS - 1
            data = pickle.load(open(inventory.DOCS_STORE % (shard_ix), 'rb'))
            app = httpserver.HTTPServer(web.Application([(r'/doc', doc.Doc, dict(data=data))]))
            log.info('Doc shard %d listening on %d', shard_ix, port)

    app.add_sockets(netutil.bind_sockets(port))
    IOLoop.current().start()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()
