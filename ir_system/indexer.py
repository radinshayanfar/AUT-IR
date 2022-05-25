import logging
import math
from typing import Dict

from tqdm.contrib import tqdm

from .utils import map_dict


class Posting:
    def __init__(self, doc_id: int, positions=None):
        if positions is None:
            positions = []
        self.doc_id: int = doc_id
        self.positions: list = positions

    def add_position(self, position: int):
        self.positions.append(position)

    def __len__(self):
        return self.positions.__len__()

    def __eq__(self, other):
        return self.__len__() == other.__len__()

    def __gt__(self, other):
        return self.__len__() > other.__len__()

    def __ge__(self, other):
        return self.__len__() > other.__len__()

    def __lt__(self, other):
        return self.__len__() < other.__len__()

    def __le__(self, other):
        return self.__len__() <= other.__len__()

    def __ne__(self, other):
        return self.__len__() != other.__len__()

    def __str__(self) -> str:
        return self.doc_id.__str__() + ', ' + str(self.__len__()) + ': ' + self.positions.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class PostingsList:
    def __init__(self):
        self.p_list: list = []
        self.length = 0

    def add_document(self, posting: Posting):
        self.p_list.append(posting)
        self.length += len(posting)

    def total_freq(self):
        return self.length

    def __getitem__(self, item) -> Posting:
        return self.p_list.__getitem__(item)

    def __len__(self):
        return self.p_list.__len__()

    def __str__(self) -> str:
        return self.p_list.__str__()

    def __repr__(self) -> str:
        return self.p_list.__repr__()


class InvertedIndex:
    CHAMPIONS_R = 200

    def __init__(self, tokenized_collection: dict):
        self.dictionary: Dict[str, PostingsList] = {}
        self.champions: Dict[str, PostingsList] = {}
        self.collection: dict = tokenized_collection
        self.lengths: Dict[int, float] = {}

    def index_collection(self):
        logging.info('building inverted index')
        for doc_id, tokens in tqdm(self.collection.items()):
            doc_index = self.index_document(doc_id)
            self.add_document_postings(doc_index)

        logging.info('calculating tf-idf vectors length')
        self.calculate_lengths()

        logging.info('building champions list')
        self.build_champions()

    def add_document_postings(self, doc_index: dict):
        for token, posting in doc_index.items():
            if token not in self.dictionary:
                self.dictionary[token] = PostingsList()
            self.dictionary[token].add_document(posting)

    def index_document(self, doc_id: str) -> dict:
        doc = self.collection[doc_id]
        out_postings: dict = {}
        for index, token in enumerate(doc):
            if token not in out_postings:
                out_postings[token] = Posting(int(doc_id))
            out_postings[token].add_position(index)

        return out_postings

    def calculate_lengths(self):
        for term, postings in tqdm(self.dictionary.items()):
            idf = math.log10(len(self.collection) / len(postings))
            for posting in postings:
                tfidf = (1 + math.log10(len(posting))) * idf
                self.lengths[posting.doc_id] = self.lengths.get(posting.doc_id, 0) + tfidf ** 2
        self.lengths = map_dict(math.sqrt, self.lengths)

    def build_champions(self):
        for term, postings in tqdm(self.dictionary.items()):
            champs = sorted(postings.p_list, reverse=True)
            champs = champs[:min(len(champs), InvertedIndex.CHAMPIONS_R)]
            champs.sort(key=lambda x: x.doc_id)
            champs_postings = PostingsList()
            champs_postings.p_list = champs
            self.champions[term] = champs_postings

    def get_postings(self, term: str, champions=False) -> PostingsList:
        if champions:
            return self.champions.get(term, PostingsList())
        return self.dictionary.get(term, PostingsList())

    def total_tokens(self):
        sum = 0
        for p in self.dictionary.values():
            sum += p.length
        return sum

    def __str__(self) -> str:
        return self.dictionary.__str__()

    def __repr__(self) -> str:
        return self.dictionary.__repr__()
