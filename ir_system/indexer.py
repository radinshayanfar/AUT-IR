from typing import Type, Dict
from tqdm.contrib import tqdm


class Posting:
    def __init__(self, doc_id: int, length=0):
        self.doc_id: int = doc_id
        self.positions: list = []
        self.length: int = length

    def add_position(self, position: int):
        self.positions.append(position)
        self.length += 1

    def __len__(self):
        return self.length

    def __str__(self) -> str:
        return self.doc_id.__str__() + ': ' + self.positions.__str__()

    def __repr__(self) -> str:
        return self.doc_id.__repr__() + ': ' + self.positions.__repr__()


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
        return self.dictionary[term]

    def __str__(self) -> str:
        return self.dictionary.__str__()

    def __repr__(self) -> str:
        return self.dictionary.__repr__()
