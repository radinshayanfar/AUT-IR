from typing import Type, Dict
from tqdm.contrib import tqdm


class Posting:
    def __init__(self, doc_id: int, positions=[]):
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

    def add_document(self, posting: Posting):
        self.p_list.append(posting)

    def __getitem__(self, item) -> Posting:
        return self.p_list.__getitem__(item)

    def __len__(self):
        return self.p_list.__len__()

    def __str__(self) -> str:
        return self.p_list.__str__()

    def __repr__(self) -> str:
        return self.p_list.__repr__()


class InvertedIndex:
    def __init__(self, tokenized_collection: dict):
        self.dictionary: Dict[str, PostingsList] = {}
        self.collection: dict = tokenized_collection

    def index_collection(self):
        for doc_id, tokens in tqdm(self.collection.items()):
            doc_index = self.index_document(doc_id)
            self.add_document_postings(doc_index)

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

    def get_postings(self, term: str) -> PostingsList:
        return self.dictionary.get(term, PostingsList())

    def __str__(self) -> str:
        return self.dictionary.__str__()

    def __repr__(self) -> str:
        return self.dictionary.__repr__()
