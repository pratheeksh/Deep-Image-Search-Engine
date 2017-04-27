from tornado import web
import json, re, pickle
from . import inventory
class Doc(web.RequestHandler):
    def initialize(self, data):
        self._documents = data

    def head(self):
        self.finish()

    def get(self):
        did = self.get_argument('id', None)
        dids = did or self.get_argument('ids', '')
        dq = self.get_argument('q', '')
        results = []

        for doc_id in dids.split(','):
            doc = self._documents[int(doc_id)]
            result = {'doc_id': doc_id,
                      'text': doc['text'],
                      'filename': doc['filename'],
                      'image_url': doc['image_url']}
            results.append(result)
        self.finish(json.dumps({'results': results}))


    def _get_url_from_title(self, title):
        return 'http://en.wikipedia.org/wiki/' + title.replace(' ', '_')

