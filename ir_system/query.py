import math
import re
from typing import Tuple, List, Union, Iterator, Dict, Any

import hazm

from . import InvertedIndex, utils, PostingsList
from .indexer import PostingsList, Posting
from .utils import remove_stop_words, map_dict


class Expression:
    def __init__(self, expr1, operator, expr2):
        self.expr1 = expr1
        self.expr2 = expr2
        self.op_str = operator
        if operator == 'AND':
            self.operator = Expression.and_intersect
        elif operator == 'AND NOT':
            self.operator = Expression.and_not_intersect
        elif operator == 'AND POS':
            self.operator = Expression.and_positional_intersect

    def evaluate(self):
        if isinstance(self.expr1, DummyIdentifier):
            return self.expr2.evaluate()
        if isinstance(self.expr2, DummyIdentifier):
            return self.expr1.evaluate()
        return self.operator(self.expr1.evaluate(), self.expr2.evaluate())

    @staticmethod
    def and_intersect(postings1: PostingsList, postings2: PostingsList) -> PostingsList:
        answer = PostingsList()
        p1 = p2 = 0
        while p1 < len(postings1) and p2 < len(postings2):
            if postings1[p1].doc_id == postings2[p2].doc_id:
                answer.add_document(
                    Posting(postings1[p1].doc_id, positions=postings1[p1].positions + postings2[p2].positions))
                p1 += 1
                p2 += 1
            elif postings1[p1].doc_id < postings2[p2].doc_id:
                p1 += 1
            else:
                p2 += 1

        return answer

    @staticmethod
    def and_not_intersect(postings1: PostingsList, postings2: PostingsList) -> PostingsList:
        answer = PostingsList()
        p1 = p2 = 0
        while p1 < len(postings1) and p2 < len(postings2):
            if postings1[p1].doc_id == postings2[p2].doc_id:
                p1 += 1
                p2 += 1
            elif postings1[p1].doc_id < postings2[p2].doc_id:
                answer.add_document(Posting(postings1[p1].doc_id, positions=postings1[p1].positions))
                p1 += 1
            else:
                p2 += 1

        return answer

    @staticmethod
    def and_positional_intersect(postings1: PostingsList, postings2: PostingsList) -> PostingsList:
        answer = PostingsList()
        p1 = p2 = 0
        while p1 < len(postings1) and p2 < len(postings2):
            if postings1[p1].doc_id == postings2[p2].doc_id:
                positions = Posting(postings1[p1].doc_id)
                p_list1 = postings1[p1].positions
                p_list2 = postings2[p2].positions
                pp1 = pp2 = 0
                while pp1 < len(p_list1) and pp2 < len(p_list2):
                    if p_list1[pp1] + 1 == p_list2[pp2]:
                        positions.add_position(p_list2[pp2])
                        pp1 += 1
                        pp2 += 1
                    elif p_list1[pp1] + 1 < p_list2[pp2]:
                        pp1 += 1
                    else:
                        pp2 += 1
                if len(positions) > 0:
                    answer.add_document(positions)
                p1 += 1
                p2 += 1
            elif postings1[p1].doc_id < postings2[p2].doc_id:
                p1 += 1
            else:
                p2 += 1

        return answer

    def __str__(self) -> str:
        return f"({self.expr1.__str__()} {self.op_str} {self.expr2.__str__()})"

    def __repr__(self) -> str:
        return self.__str__()


class DummyIdentifier:
    def __str__(self) -> str:
        return 'DUMMY'

    def __repr__(self) -> str:
        return self.__str__()


class Identifier:
    def __init__(self, term: str, index: InvertedIndex):
        self.term = term
        self.index = index

    def evaluate(self) -> PostingsList:
        return self.index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term.__str__()

    def __repr__(self) -> str:
        return self.term.__repr__()


class BooleanQuery:
    def __init__(self, query_string: str, index):
        self.index = index
        # normalize
        normal_query = hazm.Normalizer().normalize(query_string)
        # tokenize
        tokens = hazm.word_tokenize(normal_query)
        # parse !
        tokens = self.concat_nots(tokens)
        # stem - stop word
        tokens = list(map(hazm.Stemmer().stem, tokens))
        tokens = remove_stop_words(tokens, set_=utils.stop_set - set('«»'))
        # build tree
        self.exp_tree = self.build_tree(tokens)

    def concat_nots(self, tokens):
        out = []
        it = iter(tokens)
        for token in it:
            if token == '!':  # next word should be excluded from results
                out.append('!' + next(it))
                continue
            out.append(token)
        return out

    def build_tree(self, tokens: list) -> Expression:
        def build_positional(it: Iterator) -> Expression:
            tree = DummyIdentifier()
            for token in it:
                if token == '»':
                    break
                tree = Expression(tree, 'AND POS', Identifier(token, self.index))
            return tree

        exp = DummyIdentifier()
        it = iter(tokens)
        for token in it:
            if token == '«':
                sub_tree = build_positional(it)
                exp = Expression(exp, 'AND', sub_tree)
            elif token[0] == '!':
                exp = Expression(exp, 'AND NOT', Identifier(token[1:], self.index))
            else:
                exp = Expression(exp, 'AND', Identifier(token, self.index))

        return exp

    def parse_proximities(self, q_str: str) -> Tuple[str, list]:
        regex = r'"(.*?)"'

        proximity_queries = re.findall(regex, q_str)
        for q in proximity_queries:
            q_str = q_str.replace('"' + q + '"', '')

        return q_str, proximity_queries

    def get_results(self) -> PostingsList:
        return self.exp_tree.evaluate()


class RankedQuery:
    def __init__(self, query_string: str, index, collection_len: int):
        self.index = index
        self.collection_len = collection_len
        # normalize
        normal_query = hazm.Normalizer().normalize(query_string)
        # tokenize
        tokens = hazm.word_tokenize(normal_query)
        # stem
        tokens = list(map(hazm.Stemmer().stem, tokens))
        self.tfs = self.query_tf(tokens)

    def query_tf(self, tokens: List[str]) -> Dict[str, int]:
        tfs = {}
        for token in tokens:
            tfs[token] = tfs.get(token, 0) + 1

        return map_dict(lambda t: 1 + math.log10(t), tfs)

    def get_results(self, champions=True) -> PostingsList:
        scores = {}
        for token, token_tf in self.tfs.items():
            if token not in self.index.dictionary:
                continue
            postings_list = self.index.get_postings(token, champions=champions)
            idf = math.log10(self.collection_len / len(self.index.get_postings(token, champions=False)))
            print(f"token: {token}, idf: {idf}")
            for posting in postings_list:
                index = (1 + math.log10(len(posting))) * idf
                scores[posting.doc_id] = scores.get(posting.doc_id, 0) + index * token_tf

        scores = {doc_id: (score / self.index.lengths[doc_id]) for doc_id, score in scores.items()}
        ranked_results = sorted(scores, key=scores.get, reverse=True)

        out_postings_list = PostingsList()
        for doc_id in ranked_results:
            out_postings_list.add_document(Posting(doc_id))
        return out_postings_list
