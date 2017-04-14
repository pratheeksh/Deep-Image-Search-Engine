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
             'text': 'Lovely Lonely ChairFound in an abandoned Train Car.'}
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

### Test data

See data/test for a toy dataset of ~600 examples. Dataset consists of 
* Images
* Metadata
* Images as a numpy matrix **pending**
* Image features as a numpy matrix **pending**
    - Option to store and compare multiple the results of multiple feature extractors

Note: The index of the matrix = images number - 1
