from __future__ import absolute_import, division, print_function, unicode_literals
from tensorflow import keras
import numpy as np
from konlpy.tag import Twitter
from collections import Counter
from threading import Thread

class Vocabulary(object):
    def __init__(self, token_to_idx=None):
        self.token_to_idx = {}
        self.idx_to_token = {}
        self.idx = 0

        self.PAD = self.padding_token = "[PAD]"
        self.START_TOKEN = "<S>"
        self.END_TOKEN = "<T>"
        self.UNK = "[UNK]"
        self.CLS = "[CLS]"
        self.MASK = "[MASK]"
        self.SEP = "[SEP]"
        self.SEG_A = "[SEG_A]"
        self.SEG_B = "[SEG_B]"
        self.NUM = "<num>"

        self.cls_token = self.CLS
        self.sep_token = self.SEP

        self.special_tokens = [self.PAD, self.START_TOKEN, self.END_TOKEN, self.UNK, self.CLS, self.MASK, self.SEG_A, self.SEG_B, self.NUM]

        self.init_vocab()

        if token_to_idx is not None:
            self.token_to_idx = token_to_idx
            self.idx_to_token = {v: k for k, v in token_to_idx.items()}
            self.idx = len(token_to_idx) - 1

            if self.PAD in self.token_to_idx:
                self.PAD_ID = self.transform_token2idx(self.PAD)
            else:
                self.PAD_ID = 0

    def init_vocab(self):
        for special_token in self.special_tokens:
            self.add_token(special_token)
        self.PAD_ID = self.transform_token2idx(self.PAD)

    def __len__(self):
        return len(self.token_to_idx)

    def to_indices(self, tokens):
        return [self.transform_token2idx(X_token) for X_token in tokens]

    def add_token(self, token):
        if not token in self.token_to_idx:
            self.token_to_idx[token] = self.idx
            self.idx_to_token[self.idx] = token
            self.idx += 1

    def transform_token2idx(self, token, show_oov=False):
