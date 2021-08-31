from __future__ import unicode_literals

import glob
import json
import os
import re
import sys
import time
import traceback
from builtins import open
from time import sleep
import pyperclip
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs

from tqdm import tqdm

from . import secret
from .browser import Browser
from .exceptions import RetryException
from .fetch import fetch_caption
from .fetch import fetch_comments
from .fetch import fetch_datetime
from .fetch import fetch_imgs
from .fetch import fetch_likers
from .fetch import fetch_likes_plays
from .fetch import fetch_details
from .utils import instagram_int
from .utils import randmized_sleep
from .utils import retry


class Logging(object):
    PREFIX = "instagram-crawler"

    def __init__(self):
        try:
            timestamp = int(time.time())
            self.cleanup(timestamp)
            self.logger = open("/tmp/%s-%s.log" % (Logging.PREFIX, timestamp), "w")
            self.log_disable = False
        except Exception:
            self.log_disable = True

    def cleanup(self, timestamp):
        days = 86400 * 7
        days_ago_log = "/tmp/%s-%s.log" % (Logging.PREFIX, timestamp - days)
        for log in glob.glob("/tmp/instagram-crawler-*.log"):
            if log < days_ago_log:
                os.remove(log)

    def log(self, msg):
        if self.log_disable:
            return

        self.logger.write(msg + "\n")
        self.logger.flush()

    def __del__(self):
        if self.log_disable:
            return
        self.logger.close()


class InsCrawler(Logging):
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0
        self.login()
        self._dismiss_alarm_prompt()
        self._dismiss_save_prompt()

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one(".Ls00D .Szr5J")
        if ele_login:
            ele_login.click()

    def _dismiss_alarm_prompt(self):
        ele_alarm = self.browser.find_one(".cmbtv .y3zKF")
        if ele_alarm:
            ele_alarm.click()

    def _dismiss_save_prompt(self):
        ele_save = self.browser.find_one(".mt3GC .HoLwm")
        if ele_save:
            ele_save.click()

    def login(self):
        browser = self.browser
        url = "%s/accounts/login/" % (InsCrawler.URL)
        browser.get(url)
        u_input = browser.find_one('input[name="username"]')
        u_input.send_keys('a_e_i_o@naver.com') #자동완성때문에 직접 입력해둠 (secret.py 사용 안함)
        p_input = browser.find_one('input[name="password"]')
        p_input.send_keys('qhdRbfWkd1!')

        login_btn = browser.find_one(".L3NKy")
        login_btn.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_user_profile(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        name = browser.find_one(".rhpdm")
        desc = browser.find_one(".-vDIg span")
        photo = browser.find_one("._6q-tv")
        statistics = [ele.text for ele in browser.find(".g47SY")]
        post_num, follower_num, following_num = statistics
        return {
            "name": name.text,
            "desc": desc.text if desc else None,
            "photo_url": photo.get_attribute("src"),
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num,
        }

    def get_user_posts(self, username, number=None, detail=False):
        user_profile = self.get_user_profile(username)
        if not number:
            number = instagram_int(user_profile["post_num"])

        self._dismiss_login_prompt()

        if detail:
            return self._get_posts_full(number)
        else:
            return self._get_posts(number)

    def _get_posts_full(self, num):
        @retry()
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")

            # It takes time to load the post for some users with slow network
            if ele_a_datetime is None:
                raise RetryException()

            next_key = ele_a_datetime.get_attribute("href")
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        browser.implicitly_wait(1)
        browser.scroll_down()
        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()
        dict_posts = {}

        pbar = tqdm(total=num)
        pbar.set_description("fetching")
        cur_key = None

        all_posts = self._get_posts(num)
        i = 1

        # Fetching all posts
        for _ in range(num):
            dict_post = {}

            # Fetching post detail
            try:
                if(i < num):
                    check_next_post(all_posts[i]['key'])
                    i = i + 1

                # Fetching datetime and url as key
                ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
                cur_key = ele_a_datetime.get_attribute("href")
                dict_post["key"] = cur_key
                fetch_datetime(browser, dict_post)
                fetch_imgs(browser, dict_post)
                fetch_likes_plays(browser, dict_post)
                fetch_likers(browser, dict_post)
                fetch_caption(browser, dict_post)
                fetch_comments(browser, dict_post)

            except RetryException:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + cur_key or 'URL not fetched'
                    + "\x1b[0m"
                    + "\n"
                )
                break

            except Exception:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + cur_key if isinstance(cur_key,str) else 'URL not fetched'
                    + "\x1b[0m"
                    + "\n"
                )
                traceback.print_exc()

            self.log(json.dumps(dict_post, ensure_ascii=False))
            dict_posts[browser.current_url] = dict_post

            pbar.update(1)

        pbar.close()
        posts = list(dict_posts.values())
        if posts:
            posts.sort(key=lambda post: post["datetime"], reverse=True)
        return posts

    def _get_posts(self, num):
        """
            To get posts, we have to click on the load more
            button and make the browser call post api.
        """
        TIMEOUT = 600
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a")
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in key_set:
                    dict_post = { "key": key }
                    ele_img = browser.find_one(".KL4Bh img", ele)
                    dict_post["caption"] = ele_img.get_attribute("alt")
                    dict_post["img_url"] = ele_img.get_attribute("src")

                    fetch_details(browser, dict_post)

                    key_set.add(key)
                    posts.append(dict_post)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                pbar.set_description("Wait for %s sec" % (wait_time))
                sleep(wait_time)
                pbar.set_description("fetching")

                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        pbar.set_description("fetching")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        pbar.close()
        print("Done. Fetched %s posts." % (min(len(posts), num)))
        return posts[:num]

    # 검색창에 해시태그 입력 > 연관 해시태그 리스트 및 게시글 수 수집
    def fetch_hashtag_articles(self, tag):
        self.browser.find_one(".eyXLr .TqC_a").click()
        pyperclip.copy('#'+tag)
        self.browser.find_one(".LWmhU .XTCLo").send_keys(Keys.CONTROL, 'v')
        time.sleep(2)

        hashtags = self.browser.find(".uyeeR .Ap253")
        counts = self.browser.find(".Fy4o8 > span > span")

        hashtag = [h.text for h in hashtags]
        numbers = [c.text for c in counts]

        tag_counts = list(zip(hashtag, numbers))
        print(tag_counts)
        return tag_counts, hashtag # [('#운동', '14,786,428'), ('#운동하는여자', '10,017,468')]

    # 해시태그 검색 페이지에서 인기 게시글 url 가져오기
    def get_key_by_hashtag(self, tag):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)

        ele_post = self.browser.find(".EZdmt .v1Nh3 > a")
        key_list = []
        for ele in ele_post:
            key = ele.get_attribute('href')
            key_list.append(key)
        print(key_list)

        return key_list

    # 인기 게시글 url 들어가서 user 정보, 좋아요 수 가져오기
    def get_user_and_like(self, key):
        url = "%s/%s/" % (InsCrawler.URL, key)
        self.browser.get(url)

        user = self.browser.find_one(".e1e1d .Jv7Aj .sqdOP").text
        likes = self.browser.find_one(".Nm9Fw .sqdOP > span").text

        return (key, user, likes)

    # 그 다음에는 좋아요 높은 순으로 user 선택 (몇명 할건지..)

