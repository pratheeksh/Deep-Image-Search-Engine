'''
Code adapted from Evelina Bakhturina's code for scraping Flickr data as part of 
an NLP project, Sentiment Classification using Images and Label Embeddings
by Evelina Bakhturina, Abhinav Gupta, Laura Graesser, and Lakshay Sharma

The metadata source is the MVSO dataset.
'''

import string
import pickle
import os
import xml.etree.ElementTree as ET
import requests
import pprint

def build_url(photo):
    """
    Builds url to get image
    """
    if 'farm' in photo and 'secret' in photo and 'server' in photo and 'id' in photo:
        return "https://farm" + photo['farm'] + ".staticflickr.com/" + photo['server'] + "/" + photo['id'] + \
        "_" + photo['secret'] + ".jpg"
    return 'error'

def is_ready(url):
    """
    Checks if the image exists
    """
    if url == "error":
        return False
    try:
        r = requests.head(url)
        return r.status_code == 200 #200 - everything is fine, the image exists, 302 - the image was moved
    except requests.exceptions.RequestException as e:
        print("Error, skipping example: {}".format(e))
        return False # failed to connect
        
def get_image(url, name, path_to_save):
    """
    Downloads image
    """
    img_data = requests.get(url).content
    with open(path_to_save + name, 'wb') as handler:
        handler.write(img_data)

MIN_IN_TITLE = 1
MIN_IN_TITLE_AND_DESCR = 10
NUM_EXAMPLES_IN_PICKLE = 10000
path_data = '/Users/pratheeksha/School/SEA-Project/data/train/'  #folder that contains folders with xml files - create a folder with this anme for the scropt to work
path_pickle = '/Users/pratheeksha/School/SEA-Project/data/train/metadata'   #folder where you want to save pickle files - create a folder with this anme for the scropt to work
path_images = '/Users/pratheeksha/School/SEA-Project/data/train/images/'  #folder where you want to save images


data = {}
index_id = 0
count = 0
file_index = 0
files_total = 0
files_saved = 0
num_subdirs = 0
for subdir, dirs, files in os.walk(path_data):
    print('Processing subdirectory: {}'.format(subdir))
    num_from_subdir = 0
    num_subdirs += 1
    for file in files:
        if file.startswith("."):
            print("Skipping {}".format(file))
            pass
        else:
            files_total += 1
            example = {}
            url = ""
            tree = ET.parse(os.path.join(subdir, file))
            root = tree.getroot()
            for child in root:
                if child.tag == 'photo':
                    example['image_url'] = build_url(child.attrib)
            for child in root[0]:
                if child.tag == 'title' and child.text is not None and len(child.text.split()) > MIN_IN_TITLE and isinstance(child.text, str):
                    example['text'] = child.text
                if 'text' in example and child.tag == 'description' and child.text is not None and isinstance(child.text, str):
                    example['text'] += child.text
                if child.tag == "urls":
                    example['flickr_URL'] = child[0].text
                if child.tag == "tags":
                    tags = []
                    for ch in child:
                        tags.append(ch.text)
                    example['tags'] = tags
            if 'text' in example and len(example['text']) > MIN_IN_TITLE_AND_DESCR and is_ready(example['image_url']):
                index_id += 1
                example['filename'] = str(index_id) + '.jpg'
                get_image(example['image_url'], example['filename'], path_images)
                data[index_id] = example
                count += 1
                files_saved += 1
                num_from_subdir += 1
                if count == NUM_EXAMPLES_IN_PICKLE:
                    file_index += 1
                    pickle.dump(data, open(path_pickle + "data_" + str(file_index) + ".p", "wb" ) )
                    print("Select examples to check against images. From pickle file index {}".format(file_index))
                    keys = list(data.keys())
                    for k in range(10):
                            print("Key: {}".format(keys[k]))
                            pprint.pprint(data[keys[k]])
                    count = 0
                    data = {}

                if num_from_subdir >= 10:
                    break
    print("{} processed from current folder".format(num_from_subdir))
file_index += 1
pickle.dump(data, open(path_pickle + "data_" + str(file_index) + ".p", "wb" ) )
                
print("Total examples looked at: {}".format(files_total))
print("Num examples saved: {} from {} directories".format(files_saved, num_subdirs))