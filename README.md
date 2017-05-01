# SEA-Project

This is a reverse image and text search engine. User can search a repository of images and their metadata using an image, text queries, or a combination of both. Currently this only supports loading an image into the search engine via an image url.

![ImageSearch](data/ImageSearch.png)

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

Point the search engine to the images, doc shards and index shards with the following variables in `inventory.py`

- `DOCS_STORE`: this folder should hold all the doc shards in the format `dochard_0.p`
- `TREE_STORE` : this folder should hold all the kd tree indices of feature vectors in the format `0.out`
- `TEXT_STORE` : this folder should hold all the text indices and tf-df index in the format `index_txt_0.p` and `tf_idf_index.p`

Make sure that `NUM_DOC_SERVERS`, `NUM_INDEX_SERVERS`, and `NUM_TXT_INDEX_SERVERS` match the number of shards stored in the corresponding folders above

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
python -m code.webapp.start
```
and navigate to the port that the frontend is listening on (this will be printed to standard out once everything has started up).

## Getting flickr data

flickr_scaper.py parses the XML files available a part of the MVSO dataset, checks if an image exists for a datapoint, and if it does, downloads the images and saves the metadat

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
- IM_PATH = 'sea-project/data/test/images/'
- NUMPY_PATH = 'sea-project/data/test/images_numpy/'
- IM_RESIZE_DIMS = 224
- START_IM_NUM = 1 # corresponds to test data
- END_IM_NUM = 570 # corresponds to test data

```shell
python -m utils.convert_ims_to_numpy --im_per_array MAX_IMS_PER_ARRAY --im_path  IM_PATH --npy_path NUMPY_PATH  
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
* Images as a numpy matrix
* Image features as a numpy matrix
    - Option to store and compare multiple the results of multiple feature extractors
* Doc shards for storing the document data
* Index shards for storing the text indices
* Trees for storing the image features

## How to build the full dataset

1. Assumes images are stored in the image folder and their corresponding metadata is in the metadata folder
2. Create numpy arrays from the images and store in images_numpy. See converting images to numpy section above.
```shell
python -m util.convert_ims_to_numpy --im_per_array MAX_IMS_PER_ARRAY --im_path  IM_PATH --npy_path NUMPY_PATH  
--start_im START_IM_NUM --end_im  END_IM_NUM --im_resize IM_RESIZE_DIMS
```
3. Extract the image features. Assumes there are n numpy arrays containing the images in the images_numpy folder 
```shell
python -m code.feature-extractor.cnn_feature_extractor --npy_path NPY_PATH --feat_path FEAT_PATH
```
To list the keys in each dict
```shell
python -m code.feature-extractor.check_key_conversion
```
Note: To convert from matrix number and row index to image number:

image number = matrix_number * MAX_IMS_PER_MATRIX + row index + 1

4. Build kd trees from features. Assumes there are n feat_vec_i.in files in the features folder. Stores the results as .out files in the features folder.
Start workers to run the map reduce job.

```shell
python -m code.indexer-mr.workers
```
Run coordinator to create kd-trees and create feature index shards.

```shell
 python -m code.indexer-mr.coordinator --mapper_path code/indexer-mr/kdtree_jobs/mapper.py  
 --reducer_path code/indexer-mr/kdtree_jobs/reducer.py --job_path PATH_TO_FEAT_VECS --num_reducers 10
 ```
5. Create doc shards from metadata. Assumes there are n data_i.p files in the metadata folder and that the number of doc shards is set in the code.inventory with variable `NUM_DOC_SERVERS`. Doc shards are sharded by `DOC ID`
```shell
python -m code.create_doc_shards --data_path DATA_PATH --doc_path DOC_PATH
```
6. Create text index shards from metadata. Assumes there are n data_i.p files in the metadata folder and that the number of text index shards is set in the code.inventory with variable `NUM_TXT_INDEX_SERVERS`. Text indices are sharded by `DOC ID`
```shell
python -m code.indexer_text --data_path DATA_PATH --idx_path IDX_PATH
```
## Issues we ran into
1. https://github.com/tornadoweb/tornado/issues/1753
2. Pytorch set up on linserv - core dumped due to gcc version. Problem caused by AMD instead of Intel CPUs which stuggle to work with pytorch. Have to install pytorch from source. 
4. Tree recursion depth pickle error due to the size of kd tree
5. Edge case normalization is a bit buggy
6. Mercer works fine with pytorch but can't run webapp.
7. Problems with image upload feature - Tornado had issues with uploading bigger images. So resorted to using jquery to upload the image to the server and then query. There is a  roundtrip time of 2-3 seconds. 
8. Querying images with a heavy black background pulled up predominantly black images. The hypothesis is that the Alexnet model learns colours better that shapes/objects. Have fixed this by removing almost-black images from query results
9. Cannot handle 4 channel images . Need error handling for that


## Successes yay!
1. Feature extraction and similarity worked out very well, alexnet extracts features very fast as well.
2. KD trees give very good results, and qulity of results obtained in log n time are comparable to linear time search
3. Text + image search in any combination works very well, and fast.
4. UI looks nice and is user friendly.
6. We were able to load from disk using simlinks very seamlessly.
