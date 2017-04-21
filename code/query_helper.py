from util.image_processing_fns import *
from util.utils import *

IM_RESIZE_DIMS = (227, 227)
kd_tree_base = "/Users/pratheeksha/School/SEA-Project/data/test/trees"


class Query:
    def __init__(self, shard_id):
        self.kd_tree = pickle.load(open(kd_tree_base + "/" + str(shard_id) + ".p", "rb"))
        self.model = load_model()
        self.feat_vecs = np.load(open(kd_tree_base + "/" + str(shard_id) + ".npy", "rb"))
        self.file_names = np.load(open(kd_tree_base + "/" + str(shard_id) + ".fname", "rb"))

    def process_input(self, image):
        image = resizeImageAlt(image, IM_RESIZE_DIMS)
        image = convertImageToArray(image)
        image = check_and_pad(image, IM_RESIZE_DIMS)
        image = np.transpose(image, (2, 0, 1))
        image = convert_array_to_Variable(np.array([image]))
        feature_vector = self.model(image)
        return feature_vector.data.numpy().reshape((4096,))

    def get_knn_image_feats(self, feature_vector):
        scores, keys = self.kd_tree.query(feature_vector, k=10)
        top_k = {self.file_names[i]: self.feat_vecs[i] for i in keys}
        return top_k


query = Query(2)
feat = query.process_input(getImage("451.jpg", "/Users/pratheeksha/School/SEA-Project/data/test/images/"))
query.get_knn_image_feats(feat)
