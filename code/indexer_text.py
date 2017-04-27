'''
Creates text index from metadata, using title, text, and tags  tokenized with stopwords removed
as the individual words
Titles are boosted by the Title Bonus
Counts are normalized by total number of tokens in a document
Docs are hashed across indices by doc id
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
import argparse

log = logging.getLogger(__name__)

def init_indices():
    indices = []
    for i in range(NUM_TXT_INDEX_SERVERS):
        indices.append({})
    return indices

def load_metadata_file(path):
    data = pickle.load(open(path, 'rb'))
    log.info("Loaded metadata from {}".format(path))
    return data

def tokenize_text(text):
    words = map(lambda s: s.lower().strip(), text.split(" "))
    words = [word for word in words if word]
    filt_words = [word for word in words if word not in stopwords.words('english')]
    filt_words = [word for word in filt_words if 'http://' not in word]
    return filt_words

def clean_and_tokenize(text):
    text = clean_text(text)
    text = tokenize_text(text)
    return text

def process_tokenized_text(tokenized_text, index, doc_id, 
                                                                    norm_unit, title_flag):
    for tok in tokenized_text:
        if tok not in index:
            index[tok] = {}
        if title_flag:
            if doc_id not in index[tok]:
                index[tok][doc_id] = norm_unit * TITLE_BONUS
            else:
                index[tok][doc_id] += norm_unit * TITLE_BONUS
        else:
            if doc_id not in index[tok]:
                index[tok][doc_id] = norm_unit
            else:
                index[tok][doc_id] += norm_unit

def add_to_IDF_index(all_text, idf_index):
    for word in all_text:
        if word not in idf_index:
            idf_index[word] = 1
        else:
            idf_index[word] += 1 

def normalize_idf_index(idf_index, total_docs):
    for key in idf_index:
        val = idf_index[key]
        idf_index[key] = math.log(total_docs / (val * 1.0))
    return idf_index

def process_doc(doc, doc_id, index, idf_index):
    '''Prepare three text fields'''
    if 'title' in doc:
        title = doc['title']
    else:
        title = ""
    if len(title) > 0:
        title_tok = clean_and_tokenize(title)
    else:
        title_tok = []
    text = doc['text']
    text_tok = clean_and_tokenize(text)
    tags = doc['tags']
    tags = [t.lower() for t in tags if t not in stopwords.words('english')]
    doc_length = len(text_tok) + len(tags) + len(title_tok)
    norm_unit = 1. / (doc_length * 1.)

    '''Process three text fields'''
    process_tokenized_text(title_tok, index, doc_id, norm_unit, True)
    process_tokenized_text(text_tok, index, doc_id, norm_unit, False)
    process_tokenized_text(tags, index, doc_id, norm_unit, False)
    unique_words = list(set(text_tok + tags + title_tok))
    add_to_IDF_index(unique_words, idf_index)

def process_file(path, indices, idf_index):
    data = load_metadata_file(path)
    processed_docs = 0
    for doc_id in data:
        idx = doc_id % NUM_TXT_INDEX_SERVERS
        index = indices[idx]
        doc = data[doc_id]
        process_doc(doc, doc_id, index, idf_index)
        processed_docs += 1
        if processed_docs % 20 == 0:
            log.info("Processed {} docs".format(processed_docs))
    log.info("Processed {} docs".format(processed_docs))
    return indices, processed_docs

def save_indices(indices, idf_index, idx_path):
    for i in range(len(indices)):
        name = "index_txt_" + str(i) + ".p"
        pickle.dump(indices[i], open(os.path.join(idx_path, name), 'wb'))
    pickle.dump(indices[i], open(os.path.join(idx_path, "txt_idf_index.p"), 'wb'))
    log.info("Written all indices to disk")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', default='/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/biggertest/metadata', type=str)
    parser.add_argument('--idx_path', default='/Users/lauragraesser/Google Drive/NYU_Courses/SEA-Project/data/biggertest/indices', type=str)
    opt = parser.parse_args()
    print("-------------------Settings-----------------------")
    pprint.pprint(opt)
    print("-----------------------------------------------------")
    text_indices = init_indices()
    idf_index = {}
    total_docs = 0
    for f in os.listdir(opt.data_path):
        if ".DS" in f:
            log.info("Skipping {}".format(f))
        else:
            log.info("Processing {}".format(f))
            path = os.path.join(opt.data_path, f)
            indices, num_processed_docs = process_file(path, text_indices, idf_index)
            total_docs += num_processed_docs
    log.info("{} docs in total".format(total_docs))
    idf_index = normalize_idf_index(idf_index, total_docs)
    save_indices(text_indices, idf_index, opt.idx_path)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
    main()