import logging
logging.basicConfig(level=logging.INFO)

import ir_system

if __name__ == '__main__':
    logging.info('Parsing collection')
    ir = ir_system.IR('IR_data_news_12k.json')

    logging.info('Preprocessing collection')
    ir.preprocess()

    logging.info('Building inverted index')
    ir.build_index()

    logging.info('Saving index')
    ir.save_index('index.pkl')

    # ir.load_index('index.pkl')
    # print(ir.index)
