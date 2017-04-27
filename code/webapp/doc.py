from tornado import web
import json, re

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
            title, text = self._documents[int(doc_id)]
            result = {'doc_id': doc_id,
                      'title': title,
                      'url': self._get_url_from_title(title),
                      'snippet': self._get_snippet(text, dq)}
            results.append(result)
        self.finish(json.dumps({'results': results}))

    def _get_snippet(self, text, query):
        # MD - This is unnecessary
        lower_text = text.lower()
        lower_query = query.lower()
        emphasizable_terms = [pot for pot in lower_query.split() if pot in lower_text and len(pot) > 1]
        if len(emphasizable_terms) == 0: return '...'
        snippet_start_term = query if lower_query in lower_text else emphasizable_terms[0]
        term_start = lower_text.find(snippet_start_term)
        min_snippet_start = term_start - 200
        snippet_start = 0 if min_snippet_start <= 0 else lower_text.find(' ', min_snippet_start)
        max_snippet_end = term_start + len(snippet_start_term) + 200
        snippet_stop = len(text) if max_snippet_end >= len(text) else lower_text.rfind(' ', snippet_start, max_snippet_end) + 1
        snippet = text[snippet_start:snippet_stop]
        if len(emphasizable_terms) > 0:
            snippet = re.sub(r'(\b' + r'\b|\b'.join([re.escape(t) for t in emphasizable_terms]) + r'\b)', r'<strong>\1</strong>', snippet, flags=re.IGNORECASE)
        if snippet_start > 0:
            snippet = '...' + snippet
        if snippet_stop < len(text):
            snippet = snippet + '...'
        return snippet

    def _get_url_from_title(self, title):
        return 'http://en.wikipedia.org/wiki/' + title.replace(' ', '_')

