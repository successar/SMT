from __future__ import division, print_function
from smt.decoder.PhraseTable import PhraseTable
from smt.decoder.stack_decoder import StackDecoder
from smt.phrasetable_gen import ibmmodel2, phrase_extract
from smt.phrasetable_gen.word_alignment import alignment
from utility import mkcorpus
from collections import defaultdict
import collections
from smt.langmodel.ngram import ngram, create_ngram_count, create_unigram_count
import math
import cPickle as pickle

class SMTReq:
    def __init__(self, pt_file, lm_file, word_pen, beam_thresh, stack_size, distortion) :
        self.pt = PhraseTable()
        self.load_pt(pt_file)
        self.load_lm(lm_file)
        self.stack_decoder = StackDecoder(self.pt, self.language_model, word_pen, beam_thresh, stack_size, distortion)


    def load_pt(self, filename) :
        with open(filename, 'r') as fp :
            for line in fp :
                line = line.rstrip().split('|||')
                e = line[0].decode('utf-8').strip().split(' ')
                h = line[1].decode('utf-8').strip().split(' ')
                s = line[2].strip().split(' ')
                p = float(s[0])
                self.pt.add(tuple(e), tuple(h), p)
        print('Completed Phrase Table')

    def load_lm(self, filename) :

        language_prob = defaultdict(lambda: -999.0)

        with open(filename, 'r') as fp :
            for line in fp :
                line = line.strip().split('\t')
                p = float(line[0])
                l = tuple(line[1].strip().split(' '))
                language_prob[l] = p

        self.language_model = type('',(object,),{'probability_change': lambda self, context, phrase: language_prob[phrase], 
        'probability': lambda self, phrase: language_prob[phrase]})()
        print('Completed Language Model')

    def translate(self, sentence) :
        s = sentence.strip().split(' ')
        return unicode(u' '.join(self.stack_decoder.translate(s)))

class SMTDes:
    def __init__(self, lang1_file, lang2_file, lang2_lmfile, out) :
        # Translate from lang1_file to lang2_file
        self.lang1_file = lang1_file
        self.lang2_file = lang2_file
        self.out = out
        self.word_align_file_m1t2 = open(out + '.align12', 'w')
        self.word_align_file_m2t1 = open(out + '.align21', 'w')

        self.create_corpus()
        self.run_ibmmodel()
        self.phrase_table()
        self.create_phrase_prob_table(out + '.pt')
        lm_file = open(out + '.lm', 'w')
        fp = open(lang2_lmfile, 'r')
        lm_data = [line.decode('utf-8') for line in fp]       
        self.create_ngram_prob(lm_data, lm_file)
        self.create_unigram_prob(lm_data, lm_file)

    def create_corpus(self):
        self.lang1_corp = [line.decode('utf-8') for line in open(self.lang1_file, 'r')]
        self.lang2_corp = [line.decode('utf-8') for line in open(self.lang2_file, 'r')]

    def run_ibmmodel(self) :
        corpus = zip(self.lang1_corp, self.lang2_corp)
        self.m2t1 = ibmmodel2.train(corpus, loop_count = 5)
        rev_corpus = zip(self.lang2_corp, self.lang1_corp)
        self.m1t2 = ibmmodel2.train(rev_corpus, loop_count = 5)
        pickle.dump(dict(self.m2t1[0]), self.word_align_file_m2t1)
        pickle.dump(dict(self.m2t1[1]), self.word_align_file_m2t1)
        pickle.dump(dict(self.m1t2[0]), self.word_align_file_m1t2)
        pickle.dump(dict(self.m1t2[1]), self.word_align_file_m1t2)
        self.word_align_file_m2t1.close()
        self.word_align_file_m1t2.close()

    def symmetrization(self, lang1s, lang2s):
        v2t1 = ibmmodel2.viterbi_alignment(lang1s, lang2s, *self.m2t1).items()
        v1t2 = ibmmodel2.viterbi_alignment(lang1s, lang2s, *self.m1t2).items()
        return alignment(lang1s, lang2s, v1t2, v2t1)

    def phrase_extract(self, lang1s, lang2s) :
        lang1s_s = lang1s.split()
        lang2s_s = lang2s.split()
        alignment = self.symmetrization(lang1s_s, lang2s_s)
        return phrase_extract.phrase_extract(lang1s_s, lang2s_s, alignment)

    def phrase_table(self) :
        self.phrases12 = defaultdict(float)
        self.phrases2 = defaultdict(float)
        i = 0
        for (lang1s, lang2s) in zip(self.lang1_corp, self.lang2_corp) :
            phrases = self.phrase_extract(lang1s, lang2s)
            for lang1ps, lang2ps in phrases :
                lang1p = u" ".join(lang1ps)
                lang2p = u" ".join(lang2ps)
                self.phrases12[(lang1p, lang2p)] += 1
                self.phrases2[(lang2p)] += 1
            if i % 500 == 0 :
                print(i)
            i += 1


    def create_phrase_prob_table(self, outfile) :
        fp = open(outfile, 'w') 		
        for (lang1p, lang2p), count in self.phrases12.items():
            count1_2 = self.phrases2[lang2p]
            p1_2 = math.log(count / count1_2)
            fp.write((lang1p + '|||' + lang2p + '|||' + str(p1_2) + '\n').encode('utf-8'))


    def create_ngram_prob(self, corpus, lm_file):
        # calculate total number
        ngram_count, ngram_countWL = create_ngram_count(corpus, 3)
        bigram_done = defaultdict(int)
        totalnumber = len(ngram_count.keys())

        for key, count in ngram_count.items():
            count_WL = ngram_countWL[key[:-1]]
            # if fetch is failed, one is NONE (no exceptions are raised)
            if not count_WL:
                print("not found correspont first and second")
                continue
            else:
                alpha = 0.00017
                c = count
                n = count_WL
                v = totalnumber
                # create logprob
                logprob = math.log((c + alpha) / (n + alpha * v))
                print(u"{}: log({} + {} / {} + {} + {}) = {}".format(key, c, alpha, n, alpha, v, logprob).encode('utf-8'))
                # for without last
                if bigram_done[key[:-1]] != 1 :
                    logprobwithoutlast = math.log(alpha / (n + alpha * v))
                    print(u"{}: log({} / {} + {} + {}) = {}".format(key, alpha, n, alpha, v, logprobwithoutlast).encode('utf-8'))
                    lm_file.write((str(logprob) + '\t' + ' '.join(key) + '\n').encode('utf-8'))
                    lm_file.write((str(logprobwithoutlast) + '\t' + u' '.join(key[:-1]) + '\n').encode('utf-8'))
                    bigram_done[key[:-1]] = 1


    def create_unigram_prob(self, corpus, lm_file):
        unigram_count = create_unigram_count(corpus)
        sm = sum(unigram_count.values())
        totalnumber = len(unigram_count.keys())

        for (first,), count in unigram_count.items():
            alpha = 0.00017
            c = count
            v = totalnumber
            # create logprob
            logprob = math.log((c + alpha) / (sm + alpha * v))
            print(u"{}: log({}+{} / {} + {}*{}) = {}".format(first, c, alpha, sm, alpha, v, logprob).encode('utf-8'))
            lm_file.write((str(logprob) + '\t' + first + '\n').encode('utf-8'))

