import argparse
import os
import pickle
from itertools import chain

import pandas as pd
from seqeval.metrics import classification_report
from sklearn_crfsuite import CRF

from utils import read_corpus_file, data_preprocessing, convert_data, dump_report

parser = argparse.ArgumentParser(description='Process dataframe data.')


def run(args):
    args.corpus_name = args.path_to_data.split('/')[-1]

    report_dir = f'./results/{args.corpus_name}'
    os.makedirs(report_dir, exist_ok=True)

    train_file = os.path.join(args.path_to_data, 'train.csv')
    test_file = os.path.join(args.path_to_data, 'test.csv')

    report_file = os.path.join(report_dir, args.corpus_name + '_crf.csv')

    test_data = read_corpus_file(test_file, split_char=',')
    train_data = read_corpus_file(train_file, split_char=',')

    print('\n  Train data:', len(train_data))
    print('  Test data:', len(test_data))

    print('\nPreprocessing ...')

    print('\n  Train data')

    train_data = data_preprocessing(train_data)

    print('  Test data')

    test_data = data_preprocessing(test_data)

    X_train, y_train = convert_data(train_data)
    X_test, y_test = convert_data(test_data)
    pd.DataFrame.from_dict(X_train[0]).T.to_csv(f'{args.corpus_name}_X_train.csv', index=False)
    print('\nExample features:', X_train[0])
    print('Tags:', y_train[0])

    crf = CRF(algorithm='lbfgs', c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True)

    print("Training CRF")
    crf.fit(X_train, y_train)
    print('\nEvaluating CRF')

    y_pred = crf.predict(X_test)
    print(y_pred[:1])
    print(y_test[:1])
    print(set(chain.from_iterable(y_pred)))
    print(set(chain.from_iterable(y_test)))
    dict_report = classification_report(y_test, y_pred, output_dict=True)

    pickle.dump(crf, open(args.model_name, 'wb'))
    data_conll = ''

    for data, real_tags, pred_tags in zip(test_data, y_test, y_pred):
        words = data[0]
        sent = '\n'.join('{0} {1} {2}'.format(word, real_tag, pred_tag)
                         for word, real_tag, pred_tag in zip(words, real_tags, pred_tags))
        sent += '\n\n'
        data_conll += sent

    print('\nReport:', dict_report)

    print('\nSaving the report in:', report_file)

    dump_report(dict_report, report_file)

    script_result_file = os.path.join(report_dir, args.corpus_name + '_crf.tsv')

    with open(script_result_file, 'w', encoding='utf-8') as file:
        file.write(data_conll)


if __name__ == '__main__':
    parser.add_argument('--result_path',
                        default='./results/',
                        help='output filename')

    parser.add_argument('--path_to_data',
                        default='./data/tedtalk2012',
                        help='Files must be a dataframe with headers sentence_id,words,label')

    parser.add_argument('--k_fold_eval',
                        action='store_true',
                        default=False,
                        help='Files must be a dataframe with headers sentence_id,words,label')

    parser.add_argument('--model_name',
                        default='model_crf.pkl',
                        type=str,
                        help='Files must be a dataframe with headers sentence_id,words,label')
    args = parser.parse_args()
    run(args)
