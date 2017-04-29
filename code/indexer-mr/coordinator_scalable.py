'''
Source: Matt Doherty, sea assignments, assignment 2, coordinator.py
'''
import json, urllib.request, urllib.parse, glob, argparse, os.path
from tornado.ioloop import IOLoop
from tornado import web, gen, httpclient
import inventory

WORKERS = inventory.servers['worker']

class Runner(web.RequestHandler):
    def head(self):
        self.finish()

    @gen.coroutine
    def get(self):
        job_path = self.get_argument('job_path')
        num_reducers = int(self.get_argument('num_reducers'))
        yield Job(**{k: self.get_argument(k) for k in self.request.arguments}).run_coroutine()
        self.write('<pre>')
        for filename in [os.path.join(job_path, '%d.out') % i for i in range(num_reducers)]:
            self.write(filename + ":\n" + open(filename, 'r').read() + '\n')
        self.finish()

class Job:
    def __init__(self, **job_args):
        self._job_args = job_args

    def run(self):
        return IOLoop.current().run_sync(self.run_coroutine)

    @gen.coroutine
    def run_coroutine(self):
        http_client = httpclient.AsyncHTTPClient()
        http_client.configure(None, defaults=dict(connect_timeout=2000, request_timeout=2000, max_clients=100000))
        map_task_ids = yield self._run_mapper(http_client)
        reduced = yield self._run_reducer(http_client, map_task_ids)
        raise gen.Return(reduced)

    @gen.coroutine
    def _run_mapper(self, http_client):
        input_files = glob.glob(self._job_args['job_path'] + '/*.in')
        params = [urllib.parse.urlencode(dict([('input_file', input_file)] +
                                              list(self._job_args.items())))
                  for input_file in input_files]
        futures = [http_client.fetch('http://%s/map?%s' % (WORKERS[i % len(WORKERS)], p))
                   for i, p in enumerate(params)]
        raw_responses = yield futures
        parsed_responses = [json.loads(r.body.decode()) for r in raw_responses]
        assert len([r for r in parsed_responses if r['status'] not in {'noinput', 'success'}]) == 0
        map_task_ids = [r['map_task_id'] for r in parsed_responses]
        raise gen.Return(map_task_ids)

    @gen.coroutine
    def _run_reducer(self, http_client, map_task_ids):
        num_reducers = int(self._job_args['num_reducers'])
        params = [urllib.parse.urlencode(dict([('reducer_ix', i),
                                               ('map_task_ids', ','.join(map_task_ids))] +
                                              list(self._job_args.items())))
                  for i in range(num_reducers)]
        futures = [http_client.fetch('http://%s/reduce?%s' % (WORKERS[i % len(WORKERS)], p))
                   for i, p in enumerate(params)]
        raw_responses = yield futures
        parsed_responses = [json.loads(r.body.decode()) for r in raw_responses]
        assert len([r for r in parsed_responses if r['status'] != 'success']) == 0
        raise gen.Return(dict(enumerate(parsed_responses)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mapper_path', required=True)
    parser.add_argument('--reducer_path', required=True)
    parser.add_argument('--job_path', required=True)
    parser.add_argument('--num_reducers', type=int, required=True)
    args = parser.parse_args()
    Job(**vars(args)).run()