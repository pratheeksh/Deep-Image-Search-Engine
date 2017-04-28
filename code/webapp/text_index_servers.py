from code.inventory import *
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
import socket
import pickle
import random
import json
import pprint

class IndexHolder:
    def __init__(self, index_id):
        self.index_id = index_id
        self.index = self.load_index(index_id)
        self.idf_idx = self.load_idf_idx()
        print("Finished loading index for server {}".format(self.index_id))
 
    def load_index(self, index_id):
        name = "data/biggertest/indices/index_txt_" + str(index_id) + ".p"
        return pickle.load(open(name, 'rb'))

    def load_idf_idx(self):
        name = "data/biggertest/indices/txt_idf_index.p"
        return pickle.load(open(name, 'rb'))

class IndexServer(tornado.web.RequestHandler):
    def initialize(self, index_holder, port, max_results):
        self.index_holder = index_holder 
        self.port = port
        self.max_results = max_results
 
    def get(self):
        query = self.get_arguments('q', True)
        print("Query is: {}".format(query))
        results = self.get_results(query)
        self.write(results)

    def merge_mult_queries(self, results_dict):
        queries = list(results_dict.keys())
        if len(queries) == 1:
            results = results_dict[queries[0]]
            # sort by score
            results = sorted(results, key=lambda x: -x[1])
            return results
        else:
            list1 = results_dict[queries[0]] 
            for i in range(1, len(queries)):
                list2 = results_dict[queries[i]]
                list1 = self.merge_pair_queries(list1, list2)
            list1 = sorted(list1, key=lambda x: -x[1])
            if len(list1) > self.max_results:
                list1 = list1[:self.max_results]
            return list1
    
    def merge_pair_queries(self, list1, list2):
        # Input = pairs of lists of format [[doc_id, score], [doc_id, score]]
        # Lists are assuemed to be sorted by ascending doc_id
        result = []
        i = 0
        j = 0
        end1 = len(list1)
        end2 = len(list2)
        while (i < end1 and j < end2):
            if list1[i][0] < list2[j][0]:
                result.append(list1[i])
                i += 1
            elif list1[i][0] == list2[j][0]:
                score = list1[i][1] + list2[j][1]
                doc_id = list1[i][0]
                result.append([doc_id, score])
                i += 1
                j += 1
            else:
                result.append(list2[j])
                j += 1
        if i == end1:
            # add rest of list2
            while j < end2:
                result.append(list2[j])
                j += 1
        else:
            # add rest of list1
            while i < end1:
                result.append(list1[i])
                i += 1
        return result

    def get_results(self, query):
            results_dict = {}
            for q in query:
                results = self.search_index(q)
                results_dict[q] = results
            
            final_results = self.merge_mult_queries(results_dict)
            results_dict = {'postings' : final_results}
            return results_dict

    def search_index(self, q):
        results = []
        if q in self.index_holder.index:
            idf_score = self.index_holder.idf_idx[q] 
            docs = self.index_holder.index[q]
            for doc_id in docs:
                score = docs[doc_id] * idf_score
                results.append([doc_id, score])
        results = sorted(results, key=lambda x: -x[1])
        if len(results) > self.max_results:
            results = results[:self.max_results]
        results = sorted(results, key=lambda x: x[0])
        return results

def load_indices():
    indices = []
    for i in range(NUM_TXT_INDEX_SERVERS):
        index = IndexHolder(i)
        indices.append(index)
    return indices

def init_servers():
    index_servers = []
    indices = load_indices()
    for i in range(NUM_TXT_INDEX_SERVERS):
        idx_s = tornado.web.Application([
            (r"/index", IndexServer, dict(index_holder=indices[i], 
                                          port=TXT_INDEX_SERVER_PORTS[i],
                                          max_results=MAX_NUM_RESULTS)),
             ])
        idx_s.listen(TXT_INDEX_SERVER_PORTS[i])
        name = "http://" + socket.gethostname() + ":"
        print("Index server {} listing on {}".format(i, name + str(TXT_INDEX_SERVER_PORTS[i])))
        index_servers.append(idx_s)
    return index_servers
    
def main():
    index_servers = init_servers()
    print("Servers ready")
    tornado.ioloop.IOLoop.current().start()


if __name__=="__main__":
    init_ports()
    main()