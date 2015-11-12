#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
import collections
import ibmmodel1
import utility


class _keydefaultdict(collections.defaultdict):
    '''define a local function for uniform probability initialization'''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


def _train(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
    # initialize t
    t = ibmmodel1._train(corpus, loop_count)
    # default value provided as uniform probability)

    def key_fun(key):
        ''' default_factory function for keydefaultdict '''
        i, j, l_e, l_f = key
        return float(1.0) / float(l_f + 1)

    a = _keydefaultdict(key_fun)

    # loop
    for _i in xrange(loop_count):
        print(_i)
        # variables for estimating t
        count = collections.defaultdict(float)
        total = collections.defaultdict(float)
        # variables for estimating a
        count_a = collections.defaultdict(float)
        total_a = collections.defaultdict(float)

        s_total = collections.defaultdict(float)
        for (es, fs) in corpus:
            l_e = len(es)
            l_f = len(fs)
            # compute normalization
            for (j, e) in enumerate(es, 1):
                s_total[e] = 0
                for (i, f) in enumerate(fs, 1):
                    s_total[e] += t[(e, f)] * a[(i, j, l_e, l_f)]
            # collect counts
            for (j, e) in enumerate(es, 1):
                for (i, f) in enumerate(fs, 1):
                    c = t[(e, f)] * a[(i, j, l_e, l_f)] / s_total[e]
                    count[(e, f)] += c
                    total[f] += c
                    count_a[(i, j, l_e, l_f)] += c
                    total_a[(j, l_e, l_f)] += c

        for (e, f) in count.keys():
            try:
                t[(e, f)] = count[(e, f)] / total[f]
            except decimal.DivisionByZero:
                print(u"e: {e}, f: {f}, count[(e, f)]: {ef}, total[f]: \
                      {totalf}".format(e=e, f=f, ef=count[(e, f)],
                                       totalf=total[f]))
                raise
        for (i, j, l_e, l_f) in count_a.keys():
            a[(i, j, l_e, l_f)] = count_a[(i, j, l_e, l_f)] / \
                total_a[(j, l_e, l_f)]
    return (t, a)


def train(sentences, loop_count=1000):
    corpus = utility.mkcorpus(sentences)
    return _train(corpus, loop_count)


def viterbi_alignment(es, fs, t, a):
    '''
    return
        dictionary
            e in es -> f in fs
    '''
    max_a = collections.defaultdict(float)
    l_e = len(es)
    l_f = len(fs)
    for (j, e) in enumerate(es, 1):
        current_max = (0, -1)
        for (i, f) in enumerate(fs, 1):
            val = t[(e, f)] * a[(i, j, l_e, l_f)]
            # select the first one among the maximum candidates
            if current_max[1] < val:
                current_max = (i, val)
        max_a[j] = current_max[0]
    return max_a


def show_matrix(es, fs, t, a):
    '''
    print matrix according to viterbi alignment like
          fs
     -------------
    e|           |
    s|           |
     |           |
     -------------
    '''
    max_a = viterbi_alignment(es, fs, t, a).items()
    m = len(es)
    n = len(fs)
    return utility.matrix(m, n, max_a)


if __name__ == '__main__':
    pass