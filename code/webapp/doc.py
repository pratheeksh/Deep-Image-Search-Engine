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
        source = self.get_argument('src', 'None')
        sources = source.split(',')
        results = []

        for i, doc_id in enumerate(dids.split(',')):
            print("Retrieving document for %d", int(doc_id), )
            doc = self._documents[int(doc_id)]
            doc['text'] = str(doc['text'])[:max(400, len(str(doc['text'])))]
            result = {'doc_id': doc_id,
                      'title': doc['title'],
                      'text': doc['text'],
                      'flickr': doc['flickr_url'],
                      'image_url': doc['image_url'],
                      'source': sources[i],
                      'tags': ', '.join(doc['tags'])[:min(len(doc['text']), len(str(doc['tags'])))]}
            results.append(result)
        self.finish(json.dumps({'results': results}))
