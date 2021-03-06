import argparse
import logging
from argparse import Namespace
from pprint import pprint

import ir_system

logging.basicConfig(level=logging.INFO)


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(prog="MyIRSystem", allow_abbrev=False)

    parser.add_argument('-hl', '--heaps-law', action='store_true', help='demonstrate heaps law')
    parser.add_argument('-zl', '--zipf-law', action='store_true', help='demonstrate zipf law')

    i_group = parser.add_mutually_exclusive_group(required=False)
    i_group.add_argument('-l', '--load', type=str, action='store', metavar='index.pkl',
                         help='load previously saved index')
    i_group.add_argument('-s', '--save', type=str, action='store', metavar='index.pkl', help='save built index')

    t_group = parser.add_mutually_exclusive_group(required=False)
    t_group.add_argument('-r', '--ranked', action='store_true', default=True, help='ranked retrieval using tf-idf')
    t_group.add_argument('-b', '--boolean', action='store_true', default=False,
                         help='boolean retrieval using positional index')

    parser.add_argument('collection', type=str, help='collection .json file path', metavar='collection.json')

    return parser.parse_args()


def handling_arguments(args: Namespace, ir: ir_system.IR):
    if args.heaps_law:
        logging.info('demonstrating heaps law')
        ir_system.utils.heaps_law(ir, stem=False)
        ir_system.utils.heaps_law(ir, stem=True)

    if args.zipf_law:
        logging.info('demonstrating zipf law')
        ir_system.utils.zipf_law(ir, stop_words=False)
        ir_system.utils.zipf_law(ir, stop_words=True)

    if args.load is not None:
        logging.info('loading index')
        ir.load_index(args.load)
        logging.info('index loaded')
    else:
        ir.preprocess(stop_words=False)
        ir.build_index()

    if args.save is not None:
        ir.save_index(args.save)


if __name__ == '__main__':
    args = parse_arguments()

    logging.info('parsing collection')
    ir = ir_system.IR(args.collection)

    handling_arguments(args, ir)

    while True:
        q_str = input('--> ')
        if q_str == '':
            break
        if args.boolean:
            pprint(ir.boolean_query(q_str))
        else:
            pprint(ir.ranked_query(q_str))
