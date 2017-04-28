import json

from tornado import web


class Doc(web.RequestHandler):
    def initialize(self, data):
        self._documents = data

    def head(self):
        self.finish()

    def get(self):

        did = self.get_argument('id', None)
        dids = did or self.get_argument('ids', '')
        results = []

        for doc_id in dids.split(','):
            print("Retrieving document for %d", int(doc_id), )
            doc = self._documents[int(doc_id)]
            result = {'doc_id': doc_id,
                      'text': doc['text'],
                      'filename': doc['filename'],
                      'image_url': doc['image_url']}
            results.append(result)
        self.finish(json.dumps({'results': results}))


