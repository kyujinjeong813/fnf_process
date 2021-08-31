# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import json
import sys
from io import open
import time

from inscrawler import InsCrawler
from inscrawler.settings import override_settings
from inscrawler.settings import prepare_override_settings


# https://github.com/simonseo/instagram-hashtag-crawler
def get_posts_by_user(username, number, detail, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_user_posts(username, number, detail)


def get_profile(username):
    ins_crawler = InsCrawler()
    return ins_crawler.get_user_profile(username)


def get_profile_from_script(username):
    ins_cralwer = InsCrawler()
    return ins_cralwer.get_user_profile_from_script_shared_data(username)


def get_posts_by_hashtag(tag, number, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_posts_by_tag(tag, number)


def get_postnum_by_hashtag(tag, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.fetch_hashtag_articles(tag)


def get_key_by_hashtag(tag, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_key_by_hashtag(tag)


def arg_required(args, fields=[]):
    for field in fields:
        if not getattr(args, field):
            parser.print_help()
            sys.exit()

def output(data, filepath):
    out = json.dumps(data, ensure_ascii=False)
    if filepath:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(out)
    else:
        print(out)

tag_counts, hashtag = get_postnum_by_hashtag('필라테스', True)
print(hashtag)

# for tag in hashtag:
#     input_tag = tag.replace('#', '')
#     get_key_by_hashtag(input_tag, True)
#     time.sleep(1)

# lst = get_key_by_hashtag('서퍼', True) # key list가 리턴됨

# 여기서 또 타고 가서 계정, 좋아요 가져와야 햄

# ins_crawler = InsCrawler(has_screen=True)
#
# tag = '필라' #텍스트형식 #라이딩, 자전거, 한강
#
# tag_counts, hashtag = ins_crawler.fetch_hashtag_articles(tag)
# for h in hashtag:
#     input_tag = h.replace('#', '')
#     ins_crawler.get_key_by_hashtag(input_tag)

# 너무 많아서 안되면 심플하게 캡춰 떠버렷