from __future__ import division
import argparse
import glob
import lasagne
import nltk
import numpy as np
import sys
import theano
import theano.tensor as T
import time
from sklearn import metrics
from sklearn.preprocessing import LabelBinarizer
from theano.printing import Print as pp

def str2bool(v):
    return v.lower() in ('yes', 'true', 't', '1')

class Model:

    def __init__(self, train_file, test_file, batch_size=32, embedding_size=20, max_norm=40, lr=0.01, num_hops=3, adj_weight_tying=True, linear_start=True, **kwargs):
        train_lines, test_lines = self.get_lines(train_file), self.get_lines(test_file)
        lines = np.concatenate([train_lines, test_lines], axis=0)
        vocab, word_to_idx, idx_to_word, max_seqlen, max_sentlen = self.get_vocab(lines)

        self.data = {'train': {}, 'test': {}}
        S_train, self.data['train']['C'], self.data['train']['Q'], self.data['train']['Y'] = self.process_dataset(train_lines, word_to_idx, max_sentlen, offset=0)
        S_test, self.data['test']['C'], self.data['test']['Q'], self.data['test']['Y'] = self.process_dataset(test_lines, word_to_idx, max_sentlen, offset=len(S_train))
        S = np.concatenate([np.zeros((1, max_sentlen), dtype=np.int32), S_train, S_test], axis=0)
        for i in range(10):
            for k in ['C', 'Q', 'Y']:
                print k, self.data['test'][k][i]
        print 'batch_size:', batch_size, 'max_seqlen:', max_seqlen, 'max_sentlen:', max_sentlen
        print 'sentences:', S.shape
        print 'vocab:', len(vocab), vocab
        for d in ['train', 'test']:
            print d,
            for k in ['C', 'Q', 'Y']:
                print k, self.data[d][k].shape,
            print ''

        lb = LabelBinarizer()
        lb.fit(list(vocab))
        vocab = lb.classes_.tolist()
        self.batch_size = batch_size
        self.max_seqlen = max_seqlen
        self.max_sentlen = max_sentlen
        self.embedding_size = embedding_size
        self.num_classes = len(vocab) + 1
        self.vocab = vocab
        self.adj_weight_tying = adj_weight_tying
        self.num_hops = num_hops
        self.lb = lb
        self.init_lr = lr
        self.lr = self.init_lr
        self.max_norm = max_norm
        self.S = S
        self.idx_to_word = idx_to_word
        self.nonlinearity = None if linear_start else lasagne.nonlinearities.softmax

        self.build_network(self.nonlinearity)

def main():
    parser = argparse.ArgumentParser()
    parser.register('type', 'bool', str2bool)
    parser.add_argument('--task', type=int, default=1, help='Task#')
    parser.add_argument('--train_file', type=str, default='', help='Train file')
    parser.add_argument('--test_file', type=str, default='', help='Test file')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--embedding_size', type=int, default=20, help='Embedding size')
    parser.add_argument('--max_norm', type=float, default=40.0, help='Max norm')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')
    parser.add_argument('--num_hops', type=int, default=3, help='Num hops')
    parser.add_argument('--adj_weight_tying', type='bool', default=True, help='Whether to use adjacent weight tying')
    parser.add_argument('--linear_start', type='bool', default=False, help='Whether to start with linear activations')
    parser.add_argument('--shuffle_batch', type='bool', default=True, help='Whether to shuffle minibatches')
    parser.add_argument('--n_epochs', type=int, default=100, help='Num epochs')
    args = parser.parse_args()
    print '*' * 80
    print 'args:', args
    print '*' * 80
    
    args.task=1;
    args.train_file = glob.glob('data/tasks_1-20_v1-2/en/qa%d_*train.txt' % args.task)[0]
    args.test_file = glob.glob('data/tasks_1-20_v1-2/en/qa%d_*test.txt' % args.task)[0]

    if args.train_file == '' or args.test_file == '':
        args.train_file = glob.glob('data/tasks_1-20_v1-2/en/qa%d_*train.txt' % args.task)[0]
        args.test_file = glob.glob('data/tasks_1-20_v1-2/en/qa%d_*test.txt' % args.task)[0]

    model = Model(**args.__dict__)
    model.train(n_epochs=args.n_epochs, shuffle_batch=args.shuffle_batch)

if __name__ == '__main__':
    main()
