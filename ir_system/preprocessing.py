from typing import *

import hazm.utils

stop_set = set(hazm.utils.stopwords_list())


def map_dict(f: Callable, d: dict):
    return {key: f(val) for key, val in d.items()}


def remove_stop_words(tokens: str):
    return [t for t in tokens if t not in stop_set]
