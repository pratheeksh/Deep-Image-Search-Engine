 [An Image Search Engine](#an-image-search-engine)
  * [Dependencies](#dependencies)
  * [To run the search engine](#to-run-the-search-engine)
  * [Getting flickr data](#getting-flickr-data)
    + [Usage](#usage)
  * [Converting images to numpy](#converting-images-to-numpy)
  * [Feature extraction](#feature-extraction)
  * [Searching images](#searching-images)
  * [Test data](#test-data)
  * [How to build the full dataset](#how-to-build-the-full-dataset)
  * [Issues we ran into](#issues-we-ran-into)
  * [Successes yay!](#successes-yay)
# An Image Search Engine

This is a reverse image and text search engine. User can search a repository of images and their metadata using an image, text queries, or a combination of both. Images can be uploaded either by copying an image url into the Image URL field, or by uploading an image.

![ImageSearch](data/samplesearch.png)

## Dependencies
- Python 3
- Tornado
- Pytorch
- Numpy
- Scipy
- requests
- IPython
- NLTK
- NLTK stopwords corpus

You can simply install them in your python environment by running

```shell
pip install -r requirements.txt
```

## To run the search engine

This assumes that all of the data has been prepared. See the section **How to build the full dataset** to prepare the data.

Make sure that `NUM_DOC_SERVERS`, `NUM_INDEX_SERVERS`, and `NUM_TXT_INDEX_SERVERS` match the number of shards stored in the relevant data folders.

Set up your static/images to point to the location of the images on the disk. If there already exists an images directory, clear it.
```shell
cd code/webapp/static/
rm -rf images
```
With `code/webapp/static/` as the cws, run below command to connect it to the biggertest dataset. (Or whichever image source you may choose)
```
ln -s ../../../data/biggertest/images/ images
```

Then from the root directory, run
```shell
python -m code.webapp.start --data_path PATH_TO_DATA_ROOT
```
and navigate to the port that the frontend is listening on (this will be printed to standard out once everything has started up).

Note

The initial run from the root directory would take  a couple of minutes, because the pretrained Alexnet model has to get downloaded from the pytorch website and get pickled to a local directory. Subsequent startups would load the pickled model file.

To run the search engine on the `test` or `biggertest` dataset which is completely provided in the repo set `PATH_TO_DATA_ROOT` to `data/test` or `data/biggertest`. Note please make sure that `static/images` points to the right location of images, as per the above instructions.

## Getting flickr data

flickr_scaper.py parses the XML files available a part of the MVSO dataset, checks if an image exists for a datapoint, and if it does, downloads the images and saves the metadata.

Each example is assigned a unique integer key. This key is the name of the image file and the key to index into the metadata
Metadata is stored as a pickled python dict, images are saved as jpgs. Below is an example of the metadata stored:
```python
Key = 88
{'filename': '88.jpg',
 'flickr_url': 'https://www.flickr.com/photos/81273124@N00/14734618908/',
 'image_url': 'https://farm4.staticflickr.com/3877/14734618908_182577aa1e.jpg',
 'tags': ['cameraobscura',
          'abandonedbuilding',
          'milwaukee',
          'pinhole',
          'pinholephotography',
          'canonmarkiii',
          'tiltshiftlens',
          'longexposure',
          'urbex',
          'urbanexploring',
          'brewcity',
          'canon5dmarkii',
          'canon5dmarkiii',
          'diyphotography',
          'diy'],
 'text': 'With in the 5th ward of Milwaukee, WI there has been a variety of '
         'changes. Many apartments, condos, restaurants, and bars have been '
         'added. The Courteen Seed Company building was created in 1913, and '
         "has been abandoned since 1960's. In 2006, there were plans to "
         'convert there warehouse to apartments/condos, yet minimal '
         'maintenance has been done.',
 'title': 'Courteen Seed Company VS The 5th Ward'}
```

### Usage
in flickr_scraper.py set three PATH variables
1. path_data: location of the MVSO xml files
2. path_pickle: where to save the metadata
3. path_images: where to save the images

Then run
python flickr_scraper.py

A selection of examples from each pickle file are printed to the screen to allow for manual checking that keys correspond to the correct image files.

## Converting images to numpy

Converts folder of images to numpy arrays of a fixed size. Each image is resized. Images are assumed to be in colour. The occasional image is grayscale, in which case the image is padded with zeros to make the dimensions compatible. 

Use the following command from the root folder to convert_ims_to_numpy

- MAX_IMS_PER_ARRAY = 100
- IM_PATH = '/data/test/images/'
- NUMPY_PATH = '/data/test/images_numpy/'
- IM_RESIZE_DIMS = 227
- START_IM_NUM = 1 # corresponds to test data
- END_IM_NUM = 570 # corresponds to test data

```shell
python -m util.convert_ims_to_numpy --im_per_array MAX_IMS_PER_ARRAY --im_path  IM_PATH --npy_path NUMPY_PATH  
--start_im START_IM_NUM --end_im  END_IM_NUM --im_resize IM_RESIZE_DIMS
```

Finally, to check the image conversion worked correctly, see check_im_to_matrix_conversion.ipynb

## Feature extraction

A convolutional neural network (AlexNet) is used as a feature extractor to extract a feature vectore of dimension 4096 from each of the images. The network is pretrained to classifiy ImageNet features and is used out of the box to this application. The outputs of the second to last layer are used as the image features. The results are stored in a feature dictionary `feat_dict.p` whose keys are the image numbers (can also be thought of as doc ids)

## Searching images

KD trees are used to store and efficiently search for similar feature vectors. When an image is loaded into the search engine, features are extracted from the image using AlexNet, then each KD tree is searched for a set of similar feature vectors.

## Test data

See data/test for a toy dataset of ~600 examples. See data/biggertest for a toy dataset of 2.5k examples. This larger dataset fixes the missing title in the metadata in the original toy dataset. Dataset consists of 
* Images
* Metadata
* Image features stored as a dictionary `doc id: feature vec`
* Image index shards for storing the image feature vectors in KD trees
* Doc shards for storing the document data
* Text index shards for storing the text indices

## How to build the full dataset

The root directory of the data is assumed to have the following structure 
* $ROOT_DATA_DIR/
   - images/
   - metadatata/
   - images_numpy/ (Empty folder which will later be populated with numpy arrays of images)
   - features/ (Empty folder which will later be populated with feature vectors of images)
   - indices/ (Empty folder which will later be populated with text indices)
   - docs/ (Empty fodler which will later be populated with doc shards)

Step 1:

Create numpy arrays from the images and store in images_numpy. See converting images to numpy section above.
```shell
python -m util.convert_ims_to_numpy --im_per_array MAX_IMS_PER_ARRAY --im_path  IM_PATH --npy_path NUMPY_PATH  
--start_im START_IM_NUM --end_im  END_IM_NUM --im_resize IM_RESIZE_DIMS
```
Step 2:

Extract the image features. Assumes there are n numpy arrays containing the images in the images_numpy folder 
```shell
python -m code.feature-extractor.cnn_feature_extractor --npy_path NPY_PATH --feat_path FEAT_PATH
```
Checking code to test if the above commands worked well: 
To list the keys in each dict
```shell
python -m code.feature-extractor.check_key_conversion
```

To retrieve the image index from the 'K'th row of the M'th numpy array.

image index = M * MAX_IMS_PER_MATRIX + K + 1

Step 3: 

Build KD-trees from feature vectors stored in FEAT_PATH. Assumes there are n feat_vec_i.in files in the features folder. Stores the results as .out files in the features folder.
Start workers to run the map reduce job.

```shell
python -m code.indexer-mr.workers
```
Run coordinator to create kd-trees and create feature index shards.

```shell
 python -m code.indexer-mr.coordinator --mapper_path code/indexer-mr/kdtree_jobs/mapper.py  
 --reducer_path code/indexer-mr/kdtree_jobs/reducer.py --job_path PATH_TO_FEAT_VECS --num_reducers 10
 ```
**Note to those who want to scale**

This MapReduce framework has issues. There is a [nasty tornado timeout bug](https://github.com/tornadoweb/tornado/issues/1753) that won't let you run this code for larger datasets. So, we wrote a quick script that processes files in batches and generates kd-tree pickles.
```shell
 #create pickles
 cd PATH_TO_FEAT_VECS
 python ../../../code/indexer-mr/kdtree_jobs/seq.py
 
 #go back to root directory
 cd ../../.. 
 ```

Step 4: 

Create doc shards which map a document id to its metadata like (filename, title, text, tags, flickr_url, image_url) from the metadata folder. Assumes there are n data_i.p files in the metadata folder and that the number of doc shards is set in the code.inventory with variable `NUM_DOC_SERVERS`. Doc shards are sharded by `DOC ID`
```shell
python -m code.create_doc_shards --data_path METADATA_PATH --doc_path DOC_PATH
```

Create text index shards from metadata. Assumes there are n data_i.p files in the metadata folder and that the number of text index shards is set in the code.inventory with variable `NUM_TXT_INDEX_SERVERS`. Text indices are sharded by `DOC ID`
```shell
python -m code.indexer_text --data_path METADATA_PATH --idx_path IDX_PATH
```

To run the search engine,from the root directory, run
```shell
python -m code.webapp.start
```

Note

The initial run from the root directory would take  a couple of minutes, because the pretrained Alexnet model has to get downloaded from the pytorch website and get pickled to alocal directory. Subsequent startups would load the pickled model file.

## Issues we ran into
1. https://github.com/tornadoweb/tornado/issues/1753
2. Tree recursion depth pickle error due to the size of kd tree
3. Edge case normalization is a bit buggy
4. Mercer works fine with pytorch but can't run webapp.
5. Problems with image upload feature - Tornado had issues with uploading bigger images. So resorted to using jquery to upload the image to the server and then query. There is a  roundtrip time of 2-3 seconds. 
6. Querying images with a heavy black background pulled up predominantly black images. The hypothesis is that the Alexnet model learns colours better that shapes/objects. Have fixed this by removing almost-black images from query results
7. Cannot handle 4 channel images . Need error handling for that


## Successes yay!
1. Feature extraction and similarity worked out very well, alexnet extracts features very fast as well.
2. KD trees give very good results, and qulity of results obtained in log n time are comparable to linear time search
3. Text + image search in any combination works very well, and fast.
4. UI looks nice and is user friendly.
5. We were able to load from disk using simlinks very seamlessly.
6. Fast . Images get fetched with a round trip query time of ~3 seconds
7. Multiple ways to input an image; URL and file upload
