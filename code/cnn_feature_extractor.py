import numpy as np
import pickle
import os
import torch
import torch.nn as nn
from util.utils import *

def convert_to_im_num(idx, array_num, max_per_array):
    return array_num * max_per_array + idx + 1

def create_feature_matrix(data):
    data = np.transpose(data, (0, 3, 1, 2))
    print(data.shape)
    feats = []
    bs = 10
    start = 0
    end = start + bs
    while start < data.shape[0]:
        batch = convert_array_to_Variable(data[start:end])
        f = model(batch)
        feats.append(f)
        start = end
        end = start + bs
        if start % 50 == 0:
            print("Processed {} ims".format(start))
    feature_matrix = torch.cat(feats, 0)
    feature_matrix = feature_matrix.data.numpy()
    print(feature_matrix.shape)
    return feature_matrix

def convert_to_dict(feature_matrix):
    feats = {}
    for i in range(feature_matrix.shape[0]):
        key = convert_to_im_num(i, 0, 570)
        feature_vec = feature_matrix[i]
        feats[key] = feature_vec
    return feats


if __name__=="__main__":
    npy_path = '/Users/pratheeksha/School/SEA-Project/data/test/images_numpy'
    feat_path = '/Users/pratheeksha/School/SEA-Project/data/test/features'
    model = load_model()
    all_feats = []
    for m in os.listdir(npy_path):
        m_num = str(m[:-4])
        data = np.load(os.path.join(npy_path, m))
        feature_matrix = create_feature_matrix(data)
        np.save(os.path.join(feat_path, m_num), feature_matrix)
        print("Saved feature matrix {}".format(m_num))
        all_feats.append(feature_matrix)
    all_feats = np.concatenate(tuple(all_feats), axis=0)
    print(all_feats.shape)
    np.save(os.path.join(feat_path, "all_feats"), all_feats)
    print("Saved all features in one matrix")
    feats_dict = convert_to_dict(all_feats)
    pickle.dump(feats_dict, open(os.path.join(feat_path, "feat_dict.p"), 'wb'))
    print("Saved feature dictionary")








