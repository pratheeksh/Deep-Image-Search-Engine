from flask import Flask, render_template
import os
 
from flask import Flask, render_template, request, jsonify
IM_RESIZE_DIMS = (227, 227)

# create flask instance
app = Flask(__name__)
INDEX = os.path.join(os.path.dirname(__file__), 'index.csv')

# main route
@app.route('/')
def index():
    return render_template('index.html')
# search route
@app.route('/search', methods=['POST'])
def search():

    if request.method == "POST":
        print("Post method called")
        RESULTS_ARRAY = []

        # get url
        image_url = request.form.get('img')
        
        try:
            # load the query image and extract the feature vector
            from skimage import io as skimageio
            from skimage.transform import resize
            from code.cnn_feature_extractor import create_feature_matrix
            # read the image from the url  and resize HW to (227, 227)
            im = skimageio.imread(image_url)
            print("Loaded image size", im.shape)
            ima = resize(im, IM_RESIZE_DIMS)
            print("resized image size", ima.shape)
            batch = [ima] 
            # pass a batch with just the queried image to alexnet
            feature_vector = create_feature_matrix(batch, 10)
            

            # Send the feature vector to index server 
            
            return None
        except:

            # return error
            jsonify({"sorry": "Sorry, no results! Please try again."}), 500

# run!
if __name__ == '__main__':
    app.run('127.0.0.1', debug=False)
