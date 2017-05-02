import argparse
import json
import logging
import math
import os
import pickle
import urllib
from collections import defaultdict
from functools import lru_cache
from io import BytesIO
from itertools import chain

import numpy as np
import tornado
from PIL import Image
from tornado import web, gen, process, httpserver, httpclient, netutil
from tornado.ioloop import IOLoop

from code import inventory
from util.image_processing_fns import resizeImageAlt, convertImageToArray, getImage
from util.utils import convert_array_to_Variable, load_model, is_black
from . import index, doc, text_index_servers

inventory.init_ports()

index_servers = [inventory.HOSTNAME + ":" + str(p) for p in inventory.INDEX_SERVER_PORTS]
txt_index_servers = [inventory.HOSTNAME + ":" + str(p) for p in inventory.TXT_INDEX_SERVER_PORTS]
doc_servers = [inventory.HOSTNAME + ":" + str(p) for p in inventory.DOC_SERVER_PORTS]
NUM_RESULTS = inventory.MAX_NUM_RESULTS
TXT_MULT = inventory.TXT_MULT
TO_DISPLAY = inventory.TO_DISPLAY

SETTINGS = {
    "debug": False,
    "static_path": os.path.join(os.path.dirname(__file__), 'static/'),
    "template_path": os.path.join(os.path.dirname(__file__), 'templates/')
}
log = logging.getLogger(__name__)

counter = 0


class UploadHandler(tornado.web.RequestHandler):  # For Upload
    @gen.coroutine
    def post(self):
        print("Somthing recieved")
        file1 = self.request.files['0']
        filename = file1[0]['filename']
        filebody = file1[0]['body']
        with open('code/webapp/static/uploads/{}'.format(filename), 'wb') as f:
            f.write(filebody)
        f.close()
        print("File writen to uploads/", file1[0]['filename'])
        self.write(filename)


class Web(web.RequestHandler):
    def initialize(self, model):
        self.model = model

    def head(self):
        self.finish()

    @gen.coroutine
    def get_feature_vector(self, image_url, im2=None):
        if im2 == None:
            try:
                http = httpclient.AsyncHTTPClient()
                result = yield http.fetch(image_url)
                im2 = Image.open(BytesIO(result.body))
                # im2 = Image.open(requests.get(image_url, stream=True).raw)
            except OSError:
                print("error, cant process image")
                return
        im2 = resizeImageAlt(im2, inventory.IM_RESIZE_DIMS)
        im2 = convertImageToArray(im2)
        im2_np = np.transpose(np.array(im2), (2, 0, 1))
        im2 = convert_array_to_Variable(np.array([im2_np]))
        feature_vector = self.model(im2)
        return feature_vector.data.numpy().reshape((4096,))

    @lru_cache(maxsize=1024)
    @gen.coroutine
    def get(self):

        q = self.get_argument('img', None)
        qtxt = self.get_arguments('txt', True)[0].split()
        qupload = self.get_argument('load', "Empty")
        print("Upload image parameter for Rose is  ", qupload)  # For Upload
        if qupload != "Empty":  # For Upload
            try:
                qupload = Image.open('code/webapp/static/uploads/{}'.format(qupload))  # For Upload
                print("Loaded image from uploads", qupload)
            except:
                print("error, cant process image")
        # Lowercase query
        qtxt = [word.lower() for word in qtxt]
        print("Text  query is: {}".format(qtxt))
        if q == 'http://' and qupload == "Empty":
            print("Empty image query")
            postings = None
        else:
            if qupload != "Empty":  # For Upload
                feature_vector = yield self.get_feature_vector(image_url=None, im2=qupload)
            else:
                feature_vector = yield self.get_feature_vector(str(q))
            # Fetch postings from image index servers
            http = httpclient.AsyncHTTPClient()
            responses = yield [
                http.fetch('%s/index?%s' % (
                    server, urllib.parse.urlencode({'featvec': json.dumps(str(list(feature_vector)))})))
                for server in index_servers]
            # Flatten postings and sort by score
            postings = sorted(chain(*[json.loads(r.body.decode())['postings'] for r in responses]),
                              key=lambda x: x[1])[:NUM_RESULTS]
            # postings have the format {"postings": [[285, 53.61725232526324]} doc_id, score

            # Check if any of the returned images are black, and if they are
            # boost the distance by 100 to avoid showing as a result
            # COMMENT OUT between ======= to revert to old version
            # ===========================================
            for p in postings:
                fname = str(p[0]) + '.jpg'
                im = getImage(fname, inventory.IMAGES_STORE)
                b = is_black(im)
                if b:
                    print("Boosting image score")
                    p[1] += 100
            postings = sorted(postings, key=lambda x: x[1])
            # ================================================
            print("Postings list image search", postings)

        if len(qtxt) == 0:
            print("Empty text query")
            postings_txt = None
        else:
            # Fetch postings from text index servers if txt query exists
            http2 = httpclient.AsyncHTTPClient()
            params = {'q': qtxt}
            responses_txt = yield [
                http2.fetch('%s/index?%s' % (server, urllib.parse.urlencode(params, True)))
                for server in txt_index_servers]
            # Flatten postings and sort by score
            postings_txt = sorted(chain(*[json.loads(r.body.decode())['postings'] for r in responses_txt]),
                                  key=lambda x: -x[1])[:NUM_RESULTS]
            # postings have the format {"postings": [[285, 53.61725232526324]} doc_id, score
            print("Postings text search", postings_txt)

        if postings is None and postings_txt is None:
            print("Empty query")
            exit(1)
        elif postings is None:
            postings = postings_txt
            labels = ['Text'] * len(postings)
        elif postings_txt is None:
            pass
            labels = ['Image'] * len(postings)
        else:
            merged_list = {}
            common_ids = []
            for (doc_id, score) in postings:
                merged_list[doc_id] = [score, 'Image']
            for (doc_id, score) in postings_txt:
                score *= TXT_MULT  # To get to same scale
                if doc_id in merged_list:
                    merged_list[doc_id][0] += - score
                    merged_list[doc_id][1] = 'Both'
                else:
                    merged_list[doc_id] = [- score, 'Text']

            both = []
            text = []
            ims = []
            for doc_id in merged_list:
                score = merged_list[doc_id][0]
                label = merged_list[doc_id][1]
                if label == 'Both':
                    both.append([doc_id, score, label])
                elif label == 'Text':
                    text.append([doc_id, score, label])
                else:
                    ims.append([doc_id, score, label])
            both = sorted(both, key=lambda x: x[1])
            text = sorted(text, key=lambda x: x[1])
            ims = sorted(ims, key=lambda x: x[1])

            postings = []
            labels = []
            for i in both:
                postings.append([i[0], i[1]])
                labels.append(i[2])
                if len(postings) > 4:
                    break
            ims_to_add = math.ceil((TO_DISPLAY - len(postings)) / 2.0)
            print("Ims to add: {}".format(ims_to_add))
            for k, i in enumerate(ims):
                postings.append([i[0], i[1]])
                labels.append(i[2])
                if k >= ims_to_add - 1:
                    break
            for i in text:
                postings.append([i[0], i[1]])
                labels.append(i[2])
                if len(postings) >= TO_DISPLAY:
                    break

            print("Merged lists, long")
            print(postings)
            print(labels)
            print("both: {}".format(both))
            print("text: {}".format(text))
            print("ims: {}".format(ims))

        if len(postings) > TO_DISPLAY:
            postings = postings[:TO_DISPLAY]
            labels = labels[:TO_DISPLAY]

        print("Merged lists")
        print(postings)
        print(labels)

        # Batch requests to doc servers
        server_to_doc_ids = defaultdict(list)
        doc_id_to_result_ix = {}

        for i, (doc_id, _) in enumerate(postings):
            doc_id_to_result_ix[doc_id] = i
            l = labels[i]
            server_to_doc_ids[self._get_server_for_doc_id(doc_id)].append((doc_id, l))
        responses = yield self._get_doc_server_futures(server_to_doc_ids)

        # Parse outputs and insert into sorted result array
        result_list = [None] * len(postings)
        for response in responses:
            for result in json.loads(response.body.decode())['results']:
                result_list[doc_id_to_result_ix[int(result['doc_id'])]] = result
        log.info("Retrieved %d documents", len(result_list))
        self.write(json.dumps({'num_results': len(result_list), 'results': result_list}))

    def _get_doc_server_futures(self, server_to_doc_ids):
        http = httpclient.AsyncHTTPClient()
        futures = []
        for server, doc_ids in server_to_doc_ids.items():
            query_string = urllib.parse.urlencode({'ids': ','.join([str(x[0]) for x in doc_ids]),
                                                   'src': ','.join([x[1] for x in doc_ids]),
                                                   })
            print(query_string)
            futures.append(http.fetch('%s/doc?%s' % (server, query_string)))
        return futures

    def _get_server_for_doc_id(self, doc_id):

        return doc_servers[doc_id % len(doc_servers)]


class IndexDotHTMLAwareStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, path):
        if not path or path.endswith('/'):
            path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(path)


def main():
    num_procs = inventory.NUM_INDEX_SERVERS + inventory.NUM_TXT_INDEX_SERVERS + inventory.NUM_DOC_SERVERS + 1
    model = None
    try:
        model = pickle.load(open('data/model.p', 'rb'))
    except FileNotFoundError:
        model = load_model()
        pickle.dump(model, open('data/model.p', 'wb'))

    log.info('Model loaded %s', type(model))
    task_id = process.fork_processes(num_procs, max_restarts=5)

    if task_id == 0:
        port = inventory.BASE_PORT
        app = httpserver.HTTPServer(tornado.web.Application([
            (r'/search', Web, dict(model=model)),
            (r'/upload', UploadHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {"path": SETTINGS["template_path"],
                                                       "default_filename": "index.html"})
        ], **SETTINGS))
        log.info('Front end is listening on %d', port)
    else:
        if task_id <= inventory.NUM_INDEX_SERVERS:
            shard_ix = task_id - 1
            port = inventory.INDEX_SERVER_PORTS[shard_ix]
            app = httpserver.HTTPServer(web.Application([(r'/index', index.Index, dict(shard_id=shard_ix))]))
            log.info('Index image shard %d listening on %d', shard_ix, port)
        elif task_id <= inventory.NUM_INDEX_SERVERS + inventory.NUM_TXT_INDEX_SERVERS:
            shard_ix = task_id - inventory.NUM_INDEX_SERVERS - 1
            port = inventory.TXT_INDEX_SERVER_PORTS[shard_ix]
            index_holder = text_index_servers.IndexHolder(shard_ix)
            app = httpserver.HTTPServer(
                web.Application([
                    (r"/index", text_index_servers.IndexServer, dict(index_holder=index_holder,
                                                                     port=port,
                                                                     max_results=inventory.MAX_NUM_RESULTS)),
                ]))
            log.info('Index txt shard %d listening on %d', shard_ix, port)
        else:
            shard_ix = task_id - inventory.NUM_INDEX_SERVERS - inventory.NUM_TXT_INDEX_SERVERS - 1
            port = inventory.DOC_SERVER_PORTS[shard_ix]
            data = pickle.load(open(inventory.DOCS_STORE % (shard_ix), 'rb'))
            app = httpserver.HTTPServer(web.Application([(r'/doc', doc.Doc, dict(data=data))]))
            log.info('Doc shard %d listening on %d', shard_ix, port)

    app.add_sockets(netutil.bind_sockets(port))
    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        log.info("Shutting down services")
        IOLoop.current().stop()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Image search engine')
    parser.add_argument('--test', type=bool, default=True,
                        help='is test or prod')

    args = parser.parse_args()
    if args.test:
        data_path = inventory.test_data_path
    else:
        data_path = inventory.prod_data_path

    inventory.DOCS_STORE = os.path.join(data_path, "docs/docshard_%d.p")
    inventory.TREE_STORE = os.path.join(data_path, "features")
    inventory.TEXT_STORE = os.path.join(data_path, "indices")
    inventory.IMAGES_STORE = os.path.join(data_path, "images")
    print(inventory.DOCS_STORE, inventory.TREE_STORE, inventory.TEXT_STORE, inventory.IMAGES_STORE)
    main()
