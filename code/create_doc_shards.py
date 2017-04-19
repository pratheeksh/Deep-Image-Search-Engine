'''
Creates doc shards index from metadata.
Docs are hashed by doc id. 
'''
import os
from code.inventory import *
from util.utils import *
import pickle
import random
from nltk.corpus import stopwords
import re
import math
import logging
import pprint

log = logging.getLogger(__name__)

DATA_PATH = '/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/test/metadata'
DOC_PATH = '/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/test/docs'

def init_doc_shards():
    doc_shards = []
    for i in range(NUM_DOC_SERVERS):
        doc_shards.append({})
    return doc_shards

def load_metadata_file(path):
    data = pickle.load(open(path, 'rb'))
    log.info("Loaded metadata from {}".format(path))
    return data

def process_doc(doc, doc_id, doc_shard):
    # TO DO: Add title
    text = clean_text(doc['text'])
    new_doc = {
    'filename' : doc['filename'],
    'text' : text,
    'tags' : doc['tags'],
    'flickr_url' : doc['flickr_URL'],
    'image_url' : doc['image_url']
    }
    doc_shard[doc_id] = new_doc

def process_file(path, doc_shards):
    data = load_metadata_file(path)
    processed_docs = 0
    for doc_id in data:
        idx = doc_id % NUM_DOC_SERVERS
        doc_shard = doc_shards[idx]
        doc = data[doc_id]
        process_doc(doc, doc_id, doc_shard)
        processed_docs += 1
        if processed_docs % 20 == 0:
            log.info("Processed {} docs".format(processed_docs))
    log.info("Processed {} docs".format(processed_docs))
    return doc_shards, processed_docs

def save_doc_shards(doc_shards):
    for i in range(len(doc_shards)):
        name = "docshard_" + str(i) + ".p"
        pickle.dump(doc_shards[i], open(os.path.join(DOC_PATH, name), 'wb'))
    log.info("Written all doc shards to disk")

def main():
    doc_shards = init_doc_shards()
    total_docs = 0
    for f in os.listdir(DATA_PATH):
        if ".DS" in f:
            log.info("Skipping {}".format(f))
        else:
            log.info("Processing {}".format(f))
            path = os.path.join(DATA_PATH, f)
            doc_shards, num_processed_docs = process_file(path, doc_shards)
            total_docs += num_processed_docs
    log.info("{} docs in total".format(total_docs))
    save_doc_shards(doc_shards)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()