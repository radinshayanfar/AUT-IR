import json
import logging
import pickle

import hazm

from .indexer import InvertedIndex
from .preprocessing import map_dict, remove_stop_words


class IR:
    def __init__(self, collection_path: str):
        self.index = None
        self.tokenized_collection = None
        with open(collection_path, 'r') as fp:
            self.collection: dict = json.load(fp)

    def preprocess(self, stop_words=True):
        collection = self.collection
        collection = map_dict(lambda d: d['content'], collection)
        logging.info('Normalizing collection')
        collection = map_dict(hazm.Normalizer().normalize, collection)
        logging.info('Tokenizing collection')
        collection = map_dict(hazm.word_tokenize, collection)
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
        with open(file_path, 'wb') as fp:
            pickle.dump(self.index, fp)

    def load_index(self, file_path: str):
        with open(file_path, 'rb') as fp:
            self.index = pickle.load(fp)
