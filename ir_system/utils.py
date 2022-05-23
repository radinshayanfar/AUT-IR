import itertools
from typing import Callable

import hazm.utils
import matplotlib.pyplot as plt
import numpy as np
from tqdm.contrib import tqdm

stop_set: set = set(hazm.utils.stopwords_list()).union(set("!@#$%^&*()-_=+?/\\|,~`:'\";<>.،«»"))


def map_dict(f: Callable, d: dict) -> dict:
    return {key: f(val) for key, val in tqdm(d.items())}


def remove_stop_words(tokens: list, set_=None) -> list:
    if set_ is None:
        set_ = stop_set
    return [t for t in tokens if t not in set_]


def zipf_law(ir, stop_words):
    ir.preprocess(stop_words=stop_words)
    ir.build_index()
    index_dict = ir.index.dictionary
    sorted_words = sorted(index_dict.keys(), key=lambda x: index_dict[x].length, reverse=True)

    # Plotting
    x = np.log10(range(1, len(sorted_words) + 1))
    y = np.log10([index_dict[w].length for w in sorted_words])

    theta = np.polyfit(x, y, 1, w=np.sqrt(y))
    y_line = theta[1] + theta[0] * np.array(x)

    print(f"line: y={theta[0]:.2f}x+{theta[1]:.2f}")

    plt.plot(x, y, 'b')
    plt.plot(x, y_line, 'r--')
    plt.xlabel('log10 rank')
    plt.ylabel('log10 cf')
    plt.title(f"Zipf law with{'' if stop_words else 'out'} removing stop words")
    plt.legend(['actual', 'fitted line'])
    plt.show()


def heaps_law(ir, stem):
    orig_collection = ir.collection

    x = []  # tokens
    y = []  # vocabulary
    for i in [500, 1000, 1500, 2000]:
        ir.collection = dict(itertools.islice(orig_collection.items(), i))
        ir.preprocess(stem=stem)
        ir.build_index()
        x.append(ir.index.total_tokens())
        y.append(len(ir.index.dictionary.keys()))
    ir.collection = orig_collection
    ir.preprocess(stem=stem)
    ir.build_index()
    x.append(ir.index.total_tokens())
    y.append(len(ir.index.dictionary.keys()))

    # Plotting
    x = np.log10(x)
    y = np.log10(y)

    theta = np.polyfit(x[:-1], y[:-1], 1, w=np.sqrt(y[:-1]))
    y_line = theta[1] + theta[0] * np.array(x)

    print(f"line: y={theta[0]:.2f}x+{theta[1]:.2f}")

    plt.plot(x, y, 'b-x')
    plt.plot(x, y_line, 'r--')
    plt.xlabel('log10 T')
    plt.ylabel('log10 M')
    plt.title(f"Heaps law with{'' if stem else 'out'} stemming")
    plt.legend(['actual', 'fitted line'])
    plt.show()
