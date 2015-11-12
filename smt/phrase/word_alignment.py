#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
from smt.ibmmodel import ibmmodel2
from pprint import pprint


def _alignment(elist, flist, e2f, f2e):
    '''
    elist, flist
        wordlist for each language
    e2f
        translation alignment from e to f
        alignment is
        [(e, f)]
    f2e
        translation alignment from f to e
        alignment is
        [(e, f)]
    return
        alignment: {(f, e)}
             flist
          -----------------
        e |               |
        l |               |
        i |               |
        s |               |
        t |               |
          -----------------

    '''
    neighboring = {(-1, 0), (0, -1), (1, 0), (0, 1),
                   (-1, -1), (-1, 1), (1, -1), (1, 1)}
    e2f = set(e2f)
    f2e = set(f2e)
    m = len(elist)
    n = len(flist)
    alignment = e2f.intersection(f2e)
    # marge with neighborhood
    while True:
        set_len = len(alignment)
        for e_word in xrange(1, m+1):
            for f_word in xrange(1, n+1):
                if (e_word, f_word) in alignment:
                    for (e_diff, f_diff) in neighboring:
                        e_new = e_word + e_diff
                        f_new = f_word + f_diff
                        if not alignment:
                            if (e_new, f_new) in e2f.union(f2e):
                                alignment.add((e_new, f_new))
                        else:
                            if ((e_new not in zip(*alignment)[0]
                                 or f_new not in zip(*alignment)[1])
                                and (e_new, f_new) in e2f.union(f2e)):
                                alignment.add((e_new, f_new))
        if set_len == len(alignment):
            break
    # finalize
    for e_word in xrange(1, m+1):
        for f_word in xrange(1, n+1):
            # for alignment = set([])
            if not alignment:
                if (e_word, f_word) in e2f.union(f2e):
                    alignment.add((e_word, f_word))
            else:
                if ((e_word not in zip(*alignment)[0]
                     or f_word not in zip(*alignment)[1])
                    and (e_word, f_word) in e2f.union(f2e)):
                    alignment.add((e_word, f_word))
    return alignment


def alignment(es, fs, e2f, f2e):
    """
    es: English words
    fs: Foreign words
    f2e: alignment for translation from fs to es
        [(e, f)] or {(e, f)}
    e2f: alignment for translation from es to fs
        [(f, e)] or {(f, e)}
    """
    _e2f = zip(*reversed(zip(*e2f)))
    return _alignment(es, fs, _e2f, f2e)


def symmetrization(es, fs, corpus):
    '''
    corpus for translation from fs to es
    return alignment **from fs to es**
    '''
    f2e_train = ibmmodel2._train(corpus, loop_count=1000)
    f2e = ibmmodel2.viterbi_alignment(es, fs, *f2e_train).items()

    e2f_corpus = zip(*reversed(zip(*corpus)))
    e2f_train = ibmmodel2._train(e2f_corpus, loop_count=1000)
    e2f = ibmmodel2.viterbi_alignment(fs, es, *e2f_train).items()

    return alignment(es, fs, e2f, f2e)


if __name__ == '__main__':
    pass
