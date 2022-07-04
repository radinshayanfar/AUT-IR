# Information Retrieval Engine

Implementation of an information retrieval engine as AUT IR course project.

>  Instructor: [Dr. A. Nickabadi](https://scholar.google.com/citations?user=pSMNSZwAAAAJ&hl=en)

> Semester: Spring 2022



## Usage

See the help command by entering `python main.py  --help`.

```
usage: MyIRSystem [-h] [-hl] [-zl] [-l index.pkl | -s index.pkl] [-r | -b] collection.json

positional arguments:
  collection.json       collection .json file path

optional arguments:
  -h, --help            show this help message and exit
  -hl, --heaps-law      demonstrate heaps law
  -zl, --zipf-law       demonstrate zipf law
  -l index.pkl, --load index.pkl
                        load previously saved index
  -s index.pkl, --save index.pkl
                        save built index
  -r, --ranked          ranked retrieval using tf-idf
  -b, --boolean         boolean retrieval using positional index
```

If the inverted index is saved beforehand, it can be loaded using `--load` switch. Otherwise, it will build a new index, which could be saved by `--save` switch.

There are two operation modes; boolean and ranked. In ranked mode, documents are scored based on a tf-idf weighting scheme. In boolean mode, the number of terms' occurrences is used to rank the results. Supported operators for boolean mode are:

- And: The default operator by using `space` between terms in a query; `A B`
- Not: By using `!` before a term; `A ! B`
- Phrase: By using `"` around the phrase; `"A B"`

A sample input collection is available [here](./sample.json).

Preprocessing and tokenization are done by the [hazm](https://github.com/sobhe/hazm/) library (for the Persian language).

