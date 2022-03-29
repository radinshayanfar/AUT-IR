from typing import Type, Dict
from tqdm.contrib import tqdm


class InvertedIndex:
    def __init__(self, tokenized_collection: dict):
        self.dictionary: Dict[str, Term] = {}
        self.collection: dict = tokenized_collection

    def index_collection(self):
        for doc_id, tokens in tqdm(self.collection.items()):
            doc_index = self.index_document(doc_id)
            self.add_document_postings(doc_index)

    def add_document_postings(self, doc_index: dict):
        for token, posting in doc_index.items():
            if token not in self.dictionary:
                self.dictionary[token] = Term()
            self.dictionary[token].add_document(posting)

    def index_document(self, doc_id: str) -> dict:
        doc = self.collection[doc_id]
        out_postings: dict = {}
        for index, token in enumerate(doc):
            if token not in out_postings:
                out_postings[token] = Posting(int(doc_id))
            out_postings[token].add_position(index)

        return out_postings

    def __str__(self) -> str:
        return self.dictionary.__str__()

    def __repr__(self) -> str:
        return self.dictionary.__repr__()


class Posting:
    def __init__(self, doc_id: int):
        self.doc_id: int = doc_id
        self.positions: list = []

    def add_position(self, position: int):
        self.positions.append(position)

    def positions_count(self):
        len(self.positions)

    def __str__(self) -> str:
        return self.doc_id.__str__() + ': ' + self.positions.__str__()

    def __repr__(self) -> str:
        return self.doc_id.__repr__() + ': ' + self.positions.__repr__()


class Term:
    def __init__(self):
        self.postings_list: list = []

    def add_document(self, posting: Type[Posting]):
        self.postings_list.append(posting)

    def documents_count(self):
        len(self.postings_list)

    def __str__(self) -> str:
        return self.postings_list.__str__()

    def __repr__(self) -> str:
        return self.postings_list.__repr__()
