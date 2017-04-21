from scipy.spatial import KDTree

from util.image_processing_fns import *
from util.utils import *
import inventory
IM_RESIZE_DIMS = (227, 227)
kd_tree_base = "/Users/pratheeksha/School/SEA-Project/data/test/trees"
model = load_model()


def process_input(image):
    image = resizeImageAlt(image, IM_RESIZE_DIMS)
    image = convertImageToArray(image)
    image = check_and_pad(image, IM_RESIZE_DIMS)
    image = np.transpose(image, (2, 0, 1))
    image = convert_array_to_Variable(np.array([image]))
    feature_vector = model(image)
    return feature_vector.data.numpy().reshape((4096,))


class Query:
    def __init__(self, shard_id):
        self.kd_tree = pickle.load(open(kd_tree_base + "/" + str(shard_id) + ".p", "rb"))
        self.feat_vecs = np.load(open(kd_tree_base + "/" + str(shard_id) + ".npy", "rb"))
        self.file_names = np.load(open(kd_tree_base + "/" + str(shard_id) + ".fname", "rb"))

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(feature_vector, k=10)
        top_k = {self.file_names[i]: self.feat_vecs[i] for i in keys}
        return top_k


# Whatever is under main will need to
# move to start.py in the get section
def main():
    top_k_feats = []
    top_k_keys = []
    query_instances = [Query(i) for i in range(inventory.NUM_KD_TREES)]
    feat = process_input(getImage("451.jpg", "/Users/pratheeksha/School/SEA-Project/data/test/images/"))

    for query in query_instances:
        top_k = query.get_knn_image_feats(feat)
        for k in top_k:
            top_k_keys.append(k)
            top_k_feats.append(top_k[k])

    T = KDTree(np.array(top_k_feats))
    scores, keys = T.query(feat, k=10)
    for k in keys:
        print(top_k_keys[k])


if __name__ == '__main__':
    main()
