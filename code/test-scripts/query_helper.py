from code import inventory
from util.image_processing_fns import *
from util.utils import *

IM_RESIZE_DIMS = (227, 227)
kd_tree_base = "/Users/pratheeksha/School/SEA-Project/data/test/features"

model = load_model()


def process_input(image):
    image = resizeImageAlt(image, IM_RESIZE_DIMS)
    image = convertImageToArray(image)
    image = check_and_pad(image, IM_RESIZE_DIMS)
    image =  np.transpose(image, (2, 0, 1))
    image = convert_array_to_Variable(np.array([image]))
    feature_vector = model(image)
    return feature_vector.data.numpy().reshape((4096,))


class Query:
    def __init__(self, shard_id):
        self.kd_tree_dict = pickle.load(open(kd_tree_base + "/" + str(shard_id) + ".out", "rb"))
        self.file_names = list(self.kd_tree_dict.keys())[0].split()
        self.kd_tree = self.kd_tree_dict[list(self.kd_tree_dict.keys())[0]]

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(feature_vector, k=10)
        # top_k = {self.file_names[i]: self.feat_vecs[i] for i in keys}
        return scores, keys


# Whatever is under main will need to
# move to start.py in the get section
def main():
    top_k_scores = []
    query_instances = [Query(i) for i in range(inventory.NUM_KD_TREES)]
    feat = process_input(getImage("11.jpg", "/Users/pratheeksha/School/SEA-Project/data/test/images/"))

    for query in query_instances:
        scores, keys = query.get_knn_image_feats(feat)
        for i in range(len(scores)):
            top_k_scores.append((scores[i], query.file_names[keys[i]]))

    results = sorted(top_k_scores)
    for v, k in results[:10]:
        print(k, v)

if __name__ == '__main__':
    main()
