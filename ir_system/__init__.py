import json
from pprint import pprint

import hazm

from .preprocessing import map_dict, remove_stop_words


class IR:
    def __init__(self, collection_path: str):
        with open(collection_path, 'r') as fp:
            self.collection: dict = json.load(fp)

    def preprocess(self, stop_words=True):
        collection = self.collection
        collection = map_dict(lambda d: d['content'], collection)
        collection = map_dict(hazm.Normalizer().normalize, collection)
        collection = map_dict(hazm.word_tokenize, collection)
        collection = map_dict(lambda l: list(map(hazm.Lemmatizer().lemmatize, l)), collection)
        if stop_words:
            collection = map_dict(remove_stop_words, collection)
        pprint(collection)
        return collection
