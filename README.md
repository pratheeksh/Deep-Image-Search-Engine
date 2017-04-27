# SEA-Project
SEA project repo

## Getting flickr data

flickr_scaper.py parses the XML files available a part of the MVSO dataset, checks if an image exists for a datapoint, and if it does, downloads the images and saves the metadat

Each example is assigned a unique integer key. This key is the name of the image file and the key to index into the metadata
Metadata is stored as a pickled python dict, images are saved as jpgs. Below is an example of the metadata stored:
```python
{102 : {'filename': '459.jpg',
             'flickr_URL': 'https://www.flickr.com/photos/jeffrt/10336878805/',
             'image_url': 'https://farm4.staticflickr.com/3758/10336878805_de94a043ba.jpg',
             'tags': ['nikon',
                      'd700',
                      '35mmf2afd',
                      'train',
                      'track',
                      'railroad',
                      'beam',
                      'wood',
                      'chair',
                      'orange',
                      'design',
                      'dof',
                      'sky',
                      'clouds',
                      'abandoned',
                      'broken',
                      'lonelychair',
                      'emptychair'],
             'text': 'Lovely Lonely ChairFound in an abandoned Train Car.',
             'title': 'Lonely chair'}
}
```

### Usage
in flickr_scraper.py set three PATH variables
1. path_data: location of the MVSO xml files
2. path_pickle: where to save the metadata
3. path_images: where to save the images

Then run
python flickr_scraper.py

A selection of examples from each pickle file are printed to the screen to allow for manual checking that keys correspond to the correct image files.

### Converting images to numpy

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

Experiments:
- AlexNet is used as a feature extractor to extract a feature vectore of dimension 4096 from each of the images. The results are stored in a feature dictionary `feat_dict.p` whose keys are the image numbers (can also be thought of as doc ids)

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

### How to build the full test dataset

1. Assumes images are stored in the image folder and their corresponding metadata is in the metadata folder
2. Create numpy arrays from the images and store in images_numpy. See converting images to numpy section above.
```shell
python -m utils.convert_ims_to_numpy --im_per_array MAX_IMS_PER_ARRAY --im_path  IM_PATH --npy_path NUMPY_PATH  
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
4. Build kd trees from features. Assumes there are n feat_vec_i.in files in the features folder
Start workers to run the map reduce job.

```shell
python -m code.indexer-mr.workers
```
Run coordinator to create kd-trees.

```shell
 python -m code.indexer-mr.coordinator --mapper_path code/indexer-mr/kdtree_jobs/mapper.py  --reducer_path code/indexer-mr/kdtree_jobs/reducer.py --job_path data/biggertest/features/ --num_reducers 10
 ```

5. Create feature index shards from KD trees
```shell
COMMAND
```
6. Create doc shards from metadata. Assumes there are n data_i.p files in the metadata folder and that the number of doc shards is set in the code.inventory with variable `NUM_DOC_SERVERS`. Doc shards are sharded by `DOC ID`
```shell
python -m code.create_doc_shards --data_path DATA_PATH --doc_path DOC_PATH
```
7. Create text index shards from metadata. Assumes there are n data_i.p files in the metadata folder and that the number of text index shards is set in the code.inventory with variable `NUM_TXT_INDEX_SERVERS`. Text indices are sharded by `DOC ID`
```shell
python -m code.indexer_text --data_path DATA_PATH --idx_path IDX_PATH
```

## To run the search engine

TO DO

Note: To convert from matrix number and row index to image number:

image number = matrix_number * MAX_IMS_PER_MATRIX + row index + 1
