#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
from pprint import pprint


def phrase_extract(es, fs, alignment):
    ext = extract(es, fs, alignment)
    ind = {((x, y), (z, w)) for x, y, z, w in ext}
    es = tuple(es)
    fs = tuple(fs)
    return {(es[e_s-1:e_e], fs[f_s-1:f_e])
            for (e_s, e_e), (f_s, f_e) in ind}


def extract(es, fs, alignment):
    phrases = set()
    len_es = len(es)
    for e_start in range(1, len_es+1):
        for e_end in range(e_start, len_es+1):
            # find the minimally matching foreign phrase
            f_start, f_end = (len(fs), 0)
            for (e, f) in alignment:
                if e_start <= e <= e_end:
                    f_start = min(f, f_start)
                    f_end = max(f, f_end)
            phrases.update(_extract(es, fs, e_start,
                                    e_end, f_start,
                                    f_end, alignment))
    return phrases


def _extract(es, fs, e_start, e_end, f_start, f_end, alignment):
    if f_end == 0:
        return {}
    for (e, f) in alignment:
        if (f_start <= f <= f_end) and (e < e_start or e > e_end):
            return {}
    ex = set()
    f_s = f_start
    while True:
        f_e = f_end
        while True:
            ex.add((e_start, e_end, f_s, f_e))
            f_e += 1
            if f_e in zip(*alignment)[1] or f_e > len(fs):
                break
        f_s -= 1
        if f_s in zip(*alignment)[1] or f_s < 1:
            break
    return ex


def available_phrases(fs, phrases):
    """ return : set of phrase indexed tuple like """
    available = set()
    for i, f in enumerate(fs):
        f_rest = ()
        for fr in fs[i:]:
            f_rest += (fr,)
            if f_rest in phrases:
                available.add(tuple(enumerate(f_rest, i+1)))
    return available


if __name__ == '__main__':
    pass