#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
import itertools
import collections


class NgramException(Exception):
    pass


def ngram(sentences, n):
    s_len = len(sentences)
    if s_len < n:
        raise NgramException("the sentences length is not enough:\
                             len(sentences)={} < n={}".format(s_len, n))
    xs = itertools.tee(sentences, n)
    for i, t in enumerate(xs[1:]):
        for _ in xrange(i+1):
            next(t)
    return itertools.izip(*xs)

def create_ngram_count(corpus, n=3):
    ngram_dic = collections.defaultdict(float)
    ngram_dic_WL = collections.defaultdict(float)
    for item in corpus:
        sentences = item.split()
        sentences = ["</s>", "<s>"] + sentences + ["</s>"]
        ngrams = ngram(sentences, n)
        for tpl in ngrams:
            ngram_dic[tpl] += 1
            ngram_dic_WL[tpl[:-1]] += 1

    return ngram_dic, ngram_dic_WL

def create_unigram_count(corpus):
    ngram_dic = collections.defaultdict(float)
    for item in corpus:
        sentences = item.split()
        if len(sentences) < 1 :
            continue
        ngrams = ngram(sentences, 1)
        for tpl in ngrams:
            ngram_dic[tpl] += 1

    return ngram_dic


if __name__ == '__main__':
    pass
