#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
from nltk import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import RussianStemmer
from pymorphy2 import MorphAnalyzer

import artm
import numpy as np

from string import punctuation


def build_text_cleaner():
    remove_chars = punctuation
    remove_chars += u'…’—。，‘¸、ー一：ا°»·！«・¦‹】【█‐‑●》《،■“•'
    translate_tab = {ord(p): u" " for p in remove_chars}

    def replace_punctuation(raw_text):
        try:
            return raw_text.lower().translate(translate_tab)
        except:
            print raw_text.lower()
            raise

    return replace_punctuation


def get_text_processor():
    txt_cleaner = build_text_cleaner()
    tokenizer = RegexpTokenizer('[\w\d]+', gaps=False)
    stemmer = PorterStemmer()
    ru_stemmer = RussianStemmer()
    morph = MorphAnalyzer()

    def inner(text):
        tokens = tokenizer.tokenize(txt_cleaner(unicode(text)))
        for token in tokens:
            if all([c in u'1234567890йцукенгшщзхъэждлорпавыфячсмитьбю+-*/-_="$' for c in token]):
                yield ru_stemmer.stem(token)
                # yield morph.parse(token)[0].normal_form
            else:
                yield stemmer.stem(token)

    return inner


def apply_box_cox(vector):
    v = np.asarray(vector).copy()
    v[np.where(v != 0)] = np.log(v[np.where(v != 0)])  # dont ask. some kind of box-cox transformation magic
    v[np.where(v != 0)] = v[np.where(v != 0)] / v[np.where(v != 0)].sum()
    v[np.where(v != 0)] = (1 - v[np.where(v != 0)]) / (1 - v[np.where(v != 0)]).sum()
    v[np.where(v != 0)] = v[np.where(v != 0)] - v[np.where(v != 0)].min()
    v[np.where(v != 0)] = v[np.where(v != 0)] / v[np.where(v != 0)].sum()

    v = vector.reshape(-1) + v.reshape(-1) * 3  # just help trasformation by multy3 for more stable sampling
    v = v / v.sum()
    return v


def sample_from(vector):
    try:
        v = apply_box_cox(vector)
        return Counter(dict((k, v) for k, v in enumerate(np.random.multinomial(144, v.reshape(-1) * 0.99999)) if v > 0))
    except Exception as e:
        print vector.sum(), e


once_awared = set()


def to_vw(row, key='id', fields=['tag', 'text', 'classes']):
    line = '%s ' % row[key][len('https://'):]

    for field in fields:

        if field not in row:
            if field not in once_awared:
                print 'WARNING: there is no %s field in the row %s' % (field, row[key])
                once_awared.add(field)
            continue

        if row[field] is not None and len(row[field]) > 0:
            line += '|%s ' % field
            line += '%s ' % ' '.join(
                '%s:%i' % (unicode(pair[0]).replace(':', ''), pair[-1]) for pair in row[field].items() if
                pair[-1] > 0 and len(unicode(pair[0]).replace(':', '')) > 0)
    return '%s\n' % line


def prepare_for_artm(df, dataset_name):
    import io
    vw_path = '../data/%s.vw' % dataset_name
    with io.open(vw_path, 'w', encoding='utf8') as outcome:
        for k, row in df.iterrows():
            outcome.write(to_vw(row))
    artm_path = '../data/%s_batches' % dataset_name
    return artm.BatchVectorizer(target_folder=artm_path, data_path=vw_path, data_format='vowpal_wabbit',
                                batch_size=1000)
