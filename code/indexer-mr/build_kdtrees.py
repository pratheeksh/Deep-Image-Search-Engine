import argparse
import os
import pickle
import sys
from multiprocessing.pool import ThreadPool

import numpy as np
from scipy.spatial import KDTree

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import inventory

parser = argparse.ArgumentParser(description='Generate kd-tree pickles in parallel')

parser.add_argument('--data_path', type=str, default='/Users/pratheeksha/School/SEA-Project/data/test/features',
                    help='location of the job(which files to read)')

parser.add_argument('--output_path', type=str, default='/Users/pratheeksha/School/SEA-Project/data/test/trees',
                    help='location of the job(which files to read)')
args = parser.parse_args()
num_kd_trees = inventory.NUM_KD_TREES  # inventory.NUM_VEC_INDEX_SERVERS


def convert_pickle_nparray(pickled_data):
    return np.load(open(os.path.join(os.curdir, args.data_path, pickled_data), "rb"))


def build_kd_tree(index_array, input_np_array):
    kd_tree_data = []
    for i in index_array:
        kd_tree_data.extend(input_np_array[i])

    kd_tree_data = np.array(kd_tree_data)
    print(kd_tree_data.shape)
    print('Building tree using scipy.spatial')
    T = KDTree(kd_tree_data)
    # knn_1 = T.query(kd_tree_data, k=5)
    # print(('KNN(1)           : ', knn_1))
    print('done.')
    return T, kd_tree_data


def build_filename_map(index_array, input_np_array):
    count = 0
    file_names = dict()
    for i in index_array:
        for im_index in range(len(input_np_array[i])):
            file_names[count] = str(i * 100 + im_index) + ".jpg"
            count += 1
    print(count)
    return file_names


def main():
    files = [f for f in os.listdir(os.path.join(os.curdir, args.data_path)) if '.npy' in os.path.splitext(f)]
    files.pop()  # allfeats.npy

    input_np_arrays = thread_helper(convert_pickle_nparray, files, None)
    index_arrays = [[] for i in range(num_kd_trees)]

    for i, arr in enumerate(input_np_arrays):
        print(i, i % num_kd_trees)
        index_arrays[i % num_kd_trees].append(i)

    file_names = thread_helper(build_filename_map, index_arrays, input_np_arrays)

    trees = thread_helper(build_kd_tree, index_arrays, input_np_arrays)
    for i, vals in enumerate(trees):
        tree = vals[0]
        feat_vecs = vals[1]
        pickle.dump(tree, open(os.path.join(os.curdir, args.output_path, str(i) + ".p"), "wb"))
        pickle.dump(file_names[i], open(os.path.join(os.curdir, args.output_path, str(i) + ".fname"), "wb"))

        np.save(os.path.join(os.curdir, args.output_path, str(i) + ".npy"), feat_vecs)


def thread_helper(function, data, args):
    pool = ThreadPool(inventory.WORKER_THREAD_COUNT)
    if args is None:
        results = pool.map(lambda items: function(items), data)
    else:
        results = pool.map(lambda items: function(items, args), data)
    pool.close()
    pool.join()
    return results


if __name__ == '__main__':
    main()
