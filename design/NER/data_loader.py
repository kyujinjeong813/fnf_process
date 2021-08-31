import torch
import torch.utils.data as data
import os
import pickle
import numpy as np
from .data_utils import Vocabulary
from .data_utils import load_data_and_labels_klp, load_data_and_labels_exo
from konlpy.tag import Mecab

NER_idx_dic = {'<unk>':0, 'LC':1, 'DT':2, 'OG':3, 'TI':4, 'PS':5}

class DocumentDataset(data.Dataset):
    def __init__(self, vocab, char_vocab, pos_vocab, lex_dict, x_text, x_split, x_pos, labels):
        self.vocab = vocab
        self.char_vocab = char_vocab
        self.pos_vocab = pos_vocab
        self.lex_dict = lex_dict
        self.x_text = x_text
        self.x_split = x_split
        self.x_pos = x_pos
        self.labels = labels

    def __getitem__(self, index):
        x_text_item = self.x_text[index]
        x_split_item = self.x_split[index]
        x_pos_item = self.x_pos[index]
        label_item = self.labels[index]

        x_text_char_item = []

        for x_word in x_text_item:
            x_char_item = []

            for x_char in x_word:
                x_char_item.append(x_char)

            x_text_char_item.append(x_char_item)

        x_idx_item = prepare_sequence(x_text_item, self.vocab.word2idx)
        x_idx_char_item = prepare_char_sequence(x_text_char_item, self.char_vocab.word2idx)
        x_pos_item = prepare_sequence(x_pos_item, self.pos_vocab.word2idx)
        x_lex_item = prepare_lex_sequence(x_text_item, self.lex_dict)

        label = torch.LongTensor(label_item)

        return x_text_item, x_split_item, x_idx_item, x_idx_char_item, x_pos_item, x_lex_item, label

    def __len__(self):
        return len(self.x_text)

def prepare_sequence(seq, word_to_idx):
    idxs = list()
    for word in seq:
        if word not in word_to_idx:
            idxs.append(word_to_idx['<unk>'])
        else:
            idxs.append(word_to_idx[word])

def prepare_char_sequence(seq, char_to_idx):
    char_idxs = list()
    for word in seq:
        idxs = list()
        for char in word:
            if char not in char_to_idx:
                idxs.append(char_to_idx['<unk>'])
            else:
                idxs.append(char_to_idx[word])
        char_idxs.append(idxs)
    return char_idxs

def prepare_lex_sequence(seq, lex_to_ner_list):
    lex_idxs = list()
    for lexicon in seq:
        if lexicon not in lex_to_ner_list:
            lex_idxs.append([lex_to_ner_list['<unk>']])
        else:
            lex_idxs.append(lex_to_ner_list[lexicon])
    return lex_idxs

def collate_fn(data):
    """Creates mini-batch tensor"""
    data.sort(key=lambda x: len(x[0]), reverse=True)

    x_text_batch, x_split_batch, x_idx_batch, x_idx_char_batch, x_pos_batch, x_lex_batch, labels = zip(*data)

    lengths = [len(label) for label in labels]
    targets = torch.zeros(len(labels), max(lengths), 10).long()
    for i, label in enumerate(labels):
        end = lengths[i]
        targets[i, :end] = label[:end]

    max_word_len =