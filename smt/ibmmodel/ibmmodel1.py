#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
from operator import itemgetter
import collections
from pprint import pprint
import itertools
import utility

def _constant_factory(value):
    '''define a local function for uniform probability initialization'''
    return itertools.repeat(value).next


def _train(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
        
    # default value provided as uniform probability)
    t = collections.defaultdict(_constant_factory(float(1.0/len(f_keys))))

    # loop
    for i in xrange(loop_count):
        print(i)
        count = collections.defaultdict(float)
        total = collections.defaultdict(float)
        s_total = collections.defaultdict(float)
        for (es, fs) in corpus:
            # compute normalization
            for e in es:
                s_total[e] = float(0.0)
                for f in fs:
                    s_total[e] += t[(e, f)]
            for e in es:
                for f in fs:
                    count[(e, f)] += t[(e, f)] / s_total[e]
                    total[f] += t[(e, f)] / s_total[e]
        # estimate probability
        for (e, f) in count.keys():
            t[(e, f)] = count[(e, f)] / total[f]

    return t


def train(sentences, loop_count=1000):
    corpus = utility.mkcorpus(sentences)
    return _train(corpus, loop_count)


def _pprint(tbl):
    for (e, f), v in sorted(tbl.items(), key=itemgetter(1), reverse=True):
        print(u"p({e}|{f}) = {v}".format(e=e, f=f, v=v))


if __name__ == '__main__':
    pass
