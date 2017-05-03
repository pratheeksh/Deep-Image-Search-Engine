import argparse
import json
import os
import threading
import time
import urllib.request
from multiprocessing.pool import ThreadPool

from code import inventory

inventory.init_ports()

parser = argparse.ArgumentParser(description='Coordinator for the map reduce apis')
parser.add_argument('--mapper_path', type=str, default='./kdtree_jobs/mapper.py',
                    help='location of the mapper')
parser.add_argument('--reducer_path', type=str, default='./kdtree_jobs/reducer.py',
                    help='location of the mapper')
parser.add_argument('--job_path', type=str, default='../data/test/features',
                    help='location of the job(which files to read)')
parser.add_argument('--num_reducers', type=int, default=1,
                    help='Number of reducers')
args = parser.parse_args()

start = time.time()
map_task_ids = []
list_lock = threading.Lock()

worker_servers = [inventory.HOSTNAME + ":" + str(p) for p in inventory.WORKER_PORTS]

print(len(worker_servers))
print(worker_servers)


# assert(len(worker_servers) == inventory.WORKER_THREAD_COUNT)
def thread_helper(is_mapper, urls):
    pool = ThreadPool(inventory.WORKER_THREAD_COUNT)
    results = pool.map(urllib.request.urlopen, urls)

    pool.close()
    pool.join()
    for r in results:
        fetch_url(r, is_mapper)


def read_input_files():
    files = [f for f in os.listdir(os.path.join(os.curdir, args.job_path)) if '.in' in os.path.splitext(f)]
    urls = []
    print(len(files))
    for i, file in enumerate(files):
        urls.append(get_mapper_url(worker_servers[i % inventory.WORKER_THREAD_COUNT], file))
    thread_helper(True, urls)


def reduce_helper():
    urls = []

    for i in range(args.num_reducers):
        urls.append(get_reducer_url(worker_servers[i % inventory.WORKER_THREAD_COUNT], i))
    thread_helper(False, urls)


def fetch_url(url_handler, is_mapping):
    html = url_handler.read()
    encoding = url_handler.info().get_content_charset('utf-8')
    status_object = json.loads(html.decode(encoding))
    if status_object['status'] == "success":
        if is_mapping:
            with list_lock:
                map_task_ids.append(status_object['map_task_id'])


def get_reducer_url(server, reducer_ix):
    map_id_list = ','.join(str(e) for e in map_task_ids)

    return server + "/reduce?reducer_path=" + args.reducer_path.strip() + "&map_task_ids=" + map_id_list + "&reducer_ix=" + str(
        reducer_ix) + "&job_path=" + args.job_path.strip()


def get_mapper_url(server, file_name):
    return server + "/map?mapper_path=" + args.mapper_path.strip() + "&input_file=" + args.job_path.strip() + "/" + file_name + \
           "&num_reducers=" + str(args.num_reducers).strip()


if __name__ == '__main__':
    read_input_files()
    reduce_helper()
