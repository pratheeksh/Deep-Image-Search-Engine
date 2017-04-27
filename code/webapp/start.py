import tornado, pickle, logging, urllib
from tornado.ioloop import IOLoop
from tornado import web, gen, process, httpserver, httpclient, netutil
from . import inventory, index
from itertools import chain
from collections import defaultdict
import json, sys, os

NUM_RESULTS = 10
SETTINGS = {'static_path': inventory.WEBAPP_PATH}
SETTINGS = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), inventory.WEBAPP_PATH),
            "template_path": os.path.join(os.path.dirname(__file__), inventory.WEBAPP_PATH)
        }
log = logging.getLogger(__name__)

class Web(web.RequestHandler):
    def head(self):
        self.finish()

    @gen.coroutine
    def get(self):
        q = self.get_argument('q', None)
        if q is None:
            return

        # Fetch postings from index servers
        http = httpclient.AsyncHTTPClient()
        responses = yield [http.fetch('http://%s/index?%s' % (server, urllib.parse.urlencode({'q': q})))
                           for server in inventory.servers['index']]
        # Flatten postings and sort by score
        postings = sorted(chain(*[json.loads(r.body.decode())['postings'] for r in responses]),
                          key=lambda x: -x[1])[:NUM_RESULTS]

        # Batch requests to doc servers
        server_to_doc_ids = defaultdict(list)
        doc_id_to_result_ix = {}
        for i, (doc_id, _) in enumerate(postings):
            doc_id_to_result_ix[doc_id] = i
            server_to_doc_ids[self._get_server_for_doc_id(doc_id)].append(doc_id)
        responses = yield self._get_doc_server_futures(q, server_to_doc_ids)

        # Parse outputs and insert into sorted result array
        result_list = [None] * len(postings)
        for response in responses:
            for result in json.loads(response.body.decode())['results']:
                result_list[doc_id_to_result_ix[int(result['doc_id'])]] = result

        self.finish(json.dumps({'num_results': len(result_list), 'results': result_list}))

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
    num_procs = inventory.NUM_INDEX_SHARDS 
    task_id = process.fork_processes(num_procs, max_restarts=0)
    port = inventory.BASE_PORT + task_id
    if task_id == 0 : 
        app = httpserver.HTTPServer(tornado.web.Application([
                (r'/search', Web),
                (r'/(.*)', tornado.web.StaticFileHandler, {"path" : SETTINGS["static_path"], "default_filename": "index.html"})
            ], **SETTINGS))
        log.info('Front end is listening on %d', port)
    else:
        if task_id < inventory.NUM_INDEX_SHARDS:
            shard_ix = task_id 
            data = None #pickle.load(open(inventory.POSTINGS_STORE % (shard_ix), 'rb'))
            app = httpserver.HTTPServer(web.Application([(r'/index', index.Index, dict(data=data))]))
            log.info('Index shard %d listening on %d', shard_ix, port)
        else:
            print("TODO : Load doc servers")
            sys.exit()
            '''
            shard_ix = task_id - inventory.NUM_INDEX_SHARDS - 1
            data = None #pickle.load(open(inventory.DOCS_STORE % (shard_ix), 'rb'))
            app = httpserver.HTTPServer(web.Application([(r'/doc', doc.Doc, dict(data=data))]))
            log.info('Doc shard %d listening on %d', shard_ix, port)
            '''
    app.add_sockets(netutil.bind_sockets(port))
    IOLoop.current().start()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()
