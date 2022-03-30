import logging
from pprint import pprint

from ir_system.query import Expression, Identifier

logging.basicConfig(level=logging.INFO)

import ir_system

if __name__ == '__main__':
    logging.info('Parsing collection')
    ir = ir_system.IR('IR_data_news_12k.json')

    # logging.info('Preprocessing collection')
    # ir.preprocess()
    #
    # logging.info('Building inverted index')
    # ir.build_index()
    #
    # logging.info('Saving index')
    # ir.save_index('index.pkl')

    logging.info('loading index')
    ir.load_index('index.pkl')
    logging.info('index loaded')

    pprint(ir.query('تحریم آمریکا ایران'))
    pprint(ir.query('"رییس جمهور"'))
    pprint(ir.query('غده'))
    pprint(ir.query('"تحریم هسته‌ای" آمریکا علیه برادران ! ایران'))
    # ir.query('"Foo Bar" fiz "Another Value" something else')
    # print(ir.tokenized_collection['2969'])

    # print(Expression(Identifier('آمریکا', ir.index), 'AND POS', Identifier('ایر', ir.index)).evaluate())
