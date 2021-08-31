from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import os
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
from pprint import pprint
from typing import Tuple, Callable, List
import pickle
import json
from tqdm import tqdm
from collections import OrderedDict
import re

from pathlib import Path

class NamedEntityRecognitionDataset(Dataset):
    def __init__(self, train_data_dir: str, model_dir=Path('data_in')):
        self.model_dir = model_dir
        list_of_total_source_no, list_of_total_source_str, list_of_total_target_str = self.load_data(train_data_dir=train_data_dir)
        self.create_ner_dict(list_of_total_target_str)
        self._corpus = list_of_total_source_str
        self._label = list_of_total_target_str

    def set_transform_fn(self, transform_source_fn, transform_target_fn):
        self._transform_source_fn = transform_source_fn
        self._transform_target_fn = transform_target_fn

    def __len__(self) -> int:
        return len(self._corpus)

    def __getitem__(self, idx:int) -> Tuple[torch.Tensor, torch.Tensor]:
        # preprocessing
        # str -> id -> cls, sep -> pad
        token_ids_with_cls_sep, tokens, prefix_sum_of_token_start_index = self._transform_source_fn(self._corpus[idx].lower())
        list_of_ner_ids, list_of_ner_label = self._transform_target_fn(self._label[idx], tokens, prefix_sum_of_token_start_index)

        x_input = torch.tensor(token_ids_with_cls_sep).long()
        token_type_ids = torch.tensor(len(x_input[0]) * [0])
        label = torch.tensor(list_of_ner_ids).long()

        return x_input[0], token_type_ids, label

    def create_ner_dict(self, list_of_total_target_str):
        if not os.path.exists(self.model_dir / "ner_to_index.json"):
            regex_ner = re.compile('<(.+?):[A-Z]{3}>')
            list_of_ner_tag = []
            for label_text in list_of_total_target_str:
                regex_filter_res = regex_ner.finditer(label_text)
                for match_item in regex_filter_res:
                    ner_tag = match_item[0][-4:-1]
                    if ner_tag not in list_of_ner_tag:
                        list_of_ner_tag.append(ner_tag)

            ner_to_index = {"[CLS]":0. "[SEP]":1, "[PAD]":2, "[MASK]":3, "O":4}
            for ner_tag in list_of_ner_tag:
                ner_to_index['B-' + ner_tag] = len(ner_to_index)
                ner_to_index['I-' + ner_tag] = len(ner_to_index)

            with open(self.model_dir / 'ner_to_index.json', 'w', encoding='utf-8') as io:
                json.dump(ner_to_index, io, ensure_ascii=False, indent=4)
            self.ner_to_index = ner_to_index

        else:
            self.set_ner_dict()

        def set_ner_dict(self):
            with open(self.model_dir / "ner_to_index.json", 'rb') as f:
                self.ner_to_index = json.load(f)

        def load_data(self, train_data_dir):
            list_of_file_name = [file_name for file_name in os.listdir(train_data_dir) if '.txt' in file_name]
            list_of_full_file_path = [train_data_dir / file_name for file_name in list_of_file_name]
            print("num of files: ", len(list_of_full_file_path))

            list_of_total_source_no, list_of_total_source_str, list_of_total_target_str = [], [], []
            for i, full_file_path in enumerate(list_of_full_file_path):
                list_of_source_no, list_of_source_str, list_of_target_str = self.load_data_from_txt(file_full_name=full_file_path)
                list_of_total_source_str.extend(list_of_source_str)
                list_of_total_target_str.extend(list_of_target_str)
            assert len(list_of_total_source_str) == len(list_of_total_target_str)

            return list_of_total_source_no, list_of_total_source_str, list_of_total_target_str

    def load_data_from_txt(self, file_full_name):
        with codecs.open(file_full_name, "r", "utf-8") as io:
            lines = io.readlines()

            prev_line = ""
            save_flag = False
            count = 0
            sharp_lines = []

            for line in lines:
                if prev_line == "\n" or prev_line == "":
                    save_flag = True
                if line[:3] == "##" and save_flag is True:
                    count += 1
                    sharp_lines.append(line[3:])
                if count == 3:
                    count = 0
                    save_flag = False

                prev_line = line
            list_of_source_no, list_of_source_str, list_of_target_str = sharp_lines[0::3], sharp_lines[1::3], sharp_lines[2::3]
        return list_of_source_no, list_of_source_str, list_of_target_str

from gluonnlp.data import SentencepieceTokenizer, SentencepieceDetokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model
from kobert.utils import get_tokenizer
from data_utils.vocab_tokenizer import Vocabulary, Tokenizer
from data_utils.pad_sequence import keras_pad_fn

class NamedEntityRecognitionFormatter():
    def __init__(self, vocab=None, tokenizer=None, maxlen=30, model_dir=Path('data_in')):

        if vocab is None or tokenizer is None:
            tok_path = get_tokenizer()
            self.ptr_tokenizer = SentencepieceTokenizer(tok_path)
            self.ptr_detokenizer = SentencepieceDetokenizer(tok_path)
            _, vocab_of_gluonnlp = get_pytorch_kobert_model()
            token2idx = vocab_of_gluonnlp.token_to_idx
            self.vocab = Vocabulary(token2idx=token2idx)
            self.tokenizer = Tokenizer(vocab=self.vocab, split_fn=self.ptr_tokenizer, pad_fn=keras_pad_fn, maxlen=maxlen)
        else:
            self.vocab = vocab
            self.tokenizer = tokenizer
        self.maxlen = maxlen
        self.model_dir = model_dir

    def transform_source_fn(self, text):
        tokens = self.tokenizer.split(text)
        token_ids_with_cls_sep = self.tokenizer.list_of_string_to_arr_of_cls_sep_pad_token_ids([text])

        prefix_sum_of_token_start_index = []
        sum = 0
        for i, token in enumerate(tokens):
            if i == 0:
                prefix_sum_of_token_start_index.append(0)
                sum += len(token) - 1
            else:
                prefix_sum_of_token_start_index.append(sum)
                sum += len(token)
        return token_ids_with_cls_sep, tokens, prefix_sum_of_token_start_index

    def transform_target_fn(self, label_text, tokens, prefix_sum_of_token_start_index):
        regex_ner = re.compile('<(.+?):[A-Z]{3}>') # NER Tag가 2자리 문자면 {3} -> {2}로 변경 (e.g. LOC -> LC) 인경우
        regex_filter_res = regex_ner.finditer(label_text)

        list_of_ner_tag = []
        list_of_ner_text = []
        list_of_tuple_ner_start_end = []

        count_of_match = 0
        for match_item in regex_filter_res:
            ner_tag = match_item[0][-4:-1]
            ner_text = match_item[1]
            start_index = match_item.start()
            end_index = match_item.end()

            list_of_ner_tag.append(ner_tag)
            list_of_ner_text.append(ner_text)
            list_of_tuple_ner_start_end.append((start_index, end_index))
            count_of_match += 1

        list_of_ner_label = []
        entity_index = 0
        is_entity_still_B = True
        for tup in zip(tokens, prefix_sum_of_token_start_index):
            token, index = tup

            if '▁' in token:
                index += 1

            if entity_index < len(list_of_tuple_ner_start_end):
                start, end = list_of_tuple_ner_start_end[entity_index]

                if end < index:
                    is_entity_still_B = True
                    entity_index = entity_index + 1 if entity_index + 1 < len(list_of_tuple_ner_start_end) else entity_index
                    start, end = list_of_tuple_ner_start_end[entity_index]

                if start <= index and index < end:
                    entity_tag = list_of_ner_tag[entity_index]
                    if is_entity_still_B is True:
                        entity_tag = 'B-' + entity_tag
                        list_of_ner_label.append(entity_tag)
                        is_entity_still_B = False
                    else:
                        is_entity_still_B = True
                        entity_tag = 'O'
                        list_of_ner_label.append(entity_tag)

            else:
                entity_tag = 'O'
                list_of_ner_label.append(entity_tag)

        with open(self.model_dir / "ner_to_index,json", 'rb') as f:
            self.ner_to_index = json.load(f)

        list_of_ner_ids = [self.ner_to_index['[CLS']] + [self.ner_to_index[ner_tag] for ner_tag in list_of_ner_label] + [self.ner_to_index['[SEP]']]
        list_of_ner_ids = self.tokenizer._pad([list_of_ner_ids], pad_id=self.vocab.PAD_ID, maxlen=self.maxlen)[0]

        return list_of_ner_ids, list_of_ner_label

if __name__ == '__main__':

    text = "첫 회를 시작으로 13일까지 4일간 총 4회에 걸쳐 매 회 2편씩 총 8편이 공개될 예정이다."
    label_text = "첫 회를 시작으로 <13일:DAT>까지 <4일간:DUR> 총 <4회:NOH>에 걸쳐 매 회 <2편:NOH>씩 총 <8편:NOH>이 공개될 예정이다."
    ner_formatter = NamedEntityRecognitionFormatter()
    token_ids_with_cls_sep, tokens, prefix_sum_of_token_start_index = ner_formatter.transform_source_fn(text)
    ner_formatter.transform_target_fn(label_text, tokens, prefix_sum_of_token_start_index)
