from typing import Callable
from tqdm.contrib import tqdm

import hazm.utils

stop_set: set = set(hazm.utils.stopwords_list())


def map_dict(f: Callable, d: dict) -> dict:
    return {key: f(val) for key, val in tqdm(d.items())}


def remove_stop_words(tokens: list) -> list:
    return [t for t in tokens if t not in stop_set]
