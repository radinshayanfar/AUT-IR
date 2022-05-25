import json
import logging
import pickle

import hazm

from .indexer import InvertedIndex, PostingsList
from .query import BooleanQuery, RankedQuery
from .utils import map_dict, remove_stop_words


class IR:
    def __init__(self, collection_path: str):
        self.index = None
        self.tokenized_collection = None
        with open(collection_path, 'r') as fp:
            self.collection: dict = json.load(fp)

    def preprocess(self, stem=True, stop_words=True):
        logging.info('preprocessing collection')

        collection = self.collection
        collection = map_dict(lambda d: d['content'], collection)
        logging.info('Normalizing collection')
        collection = map_dict(hazm.Normalizer().normalize, collection)
        logging.info('Tokenizing collection')
        collection = map_dict(hazm.word_tokenize, collection)
        if stem:
            logging.info('Stemming collection')
            collection = map_dict(lambda l: list(map(hazm.Stemmer().stem, l)), collection)
        if stop_words:
            logging.info('Removing stop words')
            collection = map_dict(remove_stop_words, collection)
        self.tokenized_collection = collection

    def build_index(self):
        self.index: InvertedIndex = InvertedIndex(self.tokenized_collection)
        self.index.index_collection()

    def save_index(self, file_path: str):
        logging.info('saving index')
        with open(file_path, 'wb') as fp:
            pickle.dump(self.index, fp)

    def load_index(self, file_path: str):
        with open(file_path, 'rb') as fp:
            self.index = pickle.load(fp)

    def posting_result_to_title(self, results: PostingsList) -> list:
        out = []
        for posting in results.p_list:
            doc_id = str(posting.doc_id)
            doc = self.collection[doc_id]
            out.append({'id': doc_id, 'title': doc['title'], 'url': doc['url']})

        return out

    def boolean_query(self, query_string: str) -> list:
        q = BooleanQuery(query_string, self.index)
        results = q.get_results()
        results.p_list.sort(reverse=True)
        if len(results) > 5:
            results.p_list = results.p_list[:5]

        return self.posting_result_to_title(results)

    def ranked_query(self, query_string: str) -> list:
        q = RankedQuery(query_string, self.index, len(self.collection))
        results = q.get_results()
        if len(results) > 5:
            results.p_list = results.p_list[:5]
        return self.posting_result_to_title(results)
