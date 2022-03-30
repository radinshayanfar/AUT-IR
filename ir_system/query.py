import re
from typing import Tuple, List, Union

import hazm

from . import InvertedIndex
from .indexer import PostingsList, Posting
from .utils import remove_stop_words


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


class Query:
    def __init__(self, query_string: str):
        binary_q, proximity_q = self.parse_proximities(query_string)
        self.binary_token, self.proximity_tokens = self.tokenize_queries(binary_q, proximity_q)
        # print(self.binary_token)
        # print(self.proximity_tokens)

    def parse_proximities(self, q_str: str) -> Tuple[str, list]:
        regex = r'"(.*?)"'

        proximity_queries = re.findall(regex, q_str)
        for q in proximity_queries:
            q_str = q_str.replace('"' + q + '"', '')

        return q_str, proximity_queries

    def preprocess_query(self, q_str: str, stop_words=True) -> List[str]:
        # Normalizing query
        q_str = hazm.Normalizer().normalize(q_str)

        # Tokenizing query
        q_str = hazm.word_tokenize(q_str)

        # Stemming query
        q_str = list(map(hazm.Stemmer().stem, q_str))

        # Removing stop words
        if stop_words:
            q_str = remove_stop_words(q_str)

        return q_str

    def tokenize_queries(self, binary_q: str, proximity_q: List[str]) -> Tuple[List[str], List[List[str]]]:
        binary_q = self.preprocess_query(binary_q)
        proximity_q = [self.preprocess_query(q) for q in proximity_q]

        return binary_q, proximity_q

    def tokens_to_expression(self, tokens: List[str], operator, index: InvertedIndex) -> Union[Identifier, Expression]:
        it = iter(range(len(tokens)))
        exp = Identifier(tokens[next(it)], index)
        for i in it:
            if tokens[i] == '!':
                i = next(it)
                exp = Expression(exp, 'AND NOT', Identifier(tokens[i], index))
            else:
                exp = Expression(exp, operator, Identifier(tokens[i], index))

        return exp

    def get_results(self, index: InvertedIndex) -> PostingsList:
        it = iter(self.proximity_tokens)
        if len(self.binary_token) > 0:
            exp = self.tokens_to_expression(self.binary_token, 'AND', index)
        else:
            exp = self.tokens_to_expression(next(it), 'AND POS', index)

        for tokens in it:
            exp = Expression(exp, 'AND', self.tokens_to_expression(tokens, 'AND POS', index))

        return exp.evaluate()
