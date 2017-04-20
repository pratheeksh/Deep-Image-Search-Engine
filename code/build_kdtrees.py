import argparse
import os
import pickle
from multiprocessing.pool import ThreadPool

import numpy as np
from scipy.spatial import KDTree

import inventory

parser = argparse.ArgumentParser(description='Generate kd-tree pickles in parallel')

parser.add_argument('--data_path', type=str, default='/Users/pratheeksha/School/SEA-Project/data/test/features',
                    help='location of the job(which files to read)')

parser.add_argument('--output_path', type=str, default='/Users/pratheeksha/School/SEA-Project/data/test/trees',
                    help='location of the job(which files to read)')
args = parser.parse_args()
num_kd_trees = 3  # inventory.NUM_VEC_INDEX_SERVERS


def convert_pickle_nparray(pickled_data):
    return np.load(open(os.path.join(os.curdir, args.data_path, pickled_data), "rb"))


def build_kd_tree(index_array, input_np_array):
    for i in index_array:
        tup = (input_np_array[i])

    kd_tree_data = np.vstack(tup)
    print('Building tree using scipy.spatial')
    T = KDTree(kd_tree_data)
    knn_1 = T.query(kd_tree_data[50], k=5)
    print(('KNN(1)           : ', knn_1))
    print('done.')
    return T


def main():
    files = [f for f in os.listdir(os.path.join(os.curdir, args.data_path)) if '.npy' in os.path.splitext(f)]
    input_np_arrays = thread_helper(convert_pickle_nparray, files, None)
    index_arrays = [[] for i in range(num_kd_trees)]
    for i, arr in enumerate(input_np_arrays):
        index_arrays[i % num_kd_trees].append(i)
    trees = thread_helper(build_kd_tree, index_arrays, input_np_arrays)
    for i, t in enumerate(trees):
        pickle.dump(t, open(os.path.join(os.curdir, args.output_path, str(i) + ".p"), "wb"))


def thread_helper(function, data, args):
    pool = ThreadPool(inventory.WORKER_THREAD_COUNT)
    if args is None:
        results = pool.map(lambda items: function(items), data)
    else:
        results = pool.map(lambda items: function(items, args), data)
    pool.close()
    pool.join()
    return results

if __name__=='__main__':
    main()