# -*- coding: utf-8 -*-
from sys import argv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_co
from bs4 import BeautifulSoup
import config
import re

MAIN_URL = "https://twitter.com"

class Twitter(object):
    """Crawls Twitter"""
    MAX_ERRORS_USER = 30
    
    def __init__(self, username=None, password=None):
        self.loged_in = False
        self.firefox = webdriver.Firefox()
        self.firefox.get(MAIN_URL)
        self.username = username
        self.password = password

    def _login(self):
        if not self.loged_in:
            if self.firefox == None:
                self.firefox = webdriver.Firefox()
            self.firefox.get(MAIN_URL)
            if self.username is not None and self.password is not None:
                try:
                    self.firefox.find_element_by_id('signin-email').send_keys(
                        self.username)
                    input_pass = self.firefox.find_element_by_id(
                        'signin-password')
                    input_pass.send_keys(self.password)
                    input_pass.submit()
                    WebDriverWait(self.firefox, 10).until(
                        ex_co.presence_of_element_located(
                            (By.ID, 'user-dropdown-toggle')))
                    self.loged_in = True
                except Exception, e:
                    print "Exception %s" % e.args[0]
            else:
                print "some error"

    def _sign_out(self):
        if self.loged_in:
            try:
                self.firefox.find_element_by_id('user-dropdown-toggle').click()
                self.firefox.find_element_by_id('signout-form').submit()
                self.firefox.quit()
                self.loged_in = False
            except NoSuchElementException, e:
                print "Exception %s" % e.args[0]

    def _scroll_down(self, to):
        """Scrolls down to the specified value, returns expected position."""
        to += 4500
        self.firefox.execute_script('scroll(0, ' + str(to) + ');')
        return to

    def _is_timeline_protected(self):
        """Checks whether the current user page is protected.
        Expcects to be in a user page."""
        ret = True
        try:
            el = self.firefox.find_element_by_class_name('ProtectedTimeline')
            config.print_("!!! Protected profile !!!")
        except NoSuchElementException:
            ret = False
        return ret
            
    def _get_follx(self, expected, limit):
        """Private method to get the js-stream-items representing users."""
        if self._is_timeline_protected():
            return set()
        scroll = previous = error = 0
        ret = set()
        if limit and limit < expected:
            expected = limit
        config.print_same_line("Processing...", True)
        while len(ret) < expected and error < Twitter.MAX_ERRORS_USER:
            scroll = self._scroll_down(scroll)
            soup = BeautifulSoup(self.firefox.page_source, "lxml")
            elements_soup = soup.find_all(class_='js-stream-item')
            ret.update(str(element.find_all(class_='ProfileCard')[0]
                           ['data-screen-name']) for element in elements_soup)
            now = len(ret) * 100 / expected
            if now != previous:
                previous = now
                config.print_same_line(str(now) + "%..")
                error = 0
            else:
                error += 1
        config.print_end()
        return ret
    
    def get_num_followers(self, user):
        """Returns the number of followers of user and stays in /followers."""
        if self.loged_in:
            if user == self.username:
                self.firefox.get('https://twitter.com/followers')
            else:
                self.firefox.get('https://twitter.com/' + user + '/followers')
            try:
                WebDriverWait(self.firefox, 10).until(
                    ex_co.presence_of_element_located((By.CLASS_NAME,
                                                       'AppContainer')))
                number = self.firefox.find_element_by_class_name(
                    'ProfileNav-item--followers').find_element_by_class_name(
                        'ProfileNav-value').text
                if 'K' in number or 'M' in number:
                    return None
                else:
                    number = number.replace(',', '')
                    config.print_(user + " has " + str(number) + " followers")
                    return int(number)
            except (NoSuchElementException, TimeoutException):
                config.print_("It seems that " + user + " hasn't followers.")
                return 0
        else:
            return None

    def get_num_following(self, user):
        """Returns the number of followings of user and stays in /following."""
        if self.loged_in:
            if user == self.username:
                self.firefox.get('https://twitter.com/following')
            else:
                self.firefox.get('https://twitter.com/' + user + '/following')
            try:
                WebDriverWait(self.firefox, 10).until(
                    ex_co.presence_of_element_located((By.CLASS_NAME,
                                                       'AppContainer')))
                number = self.firefox.find_element_by_class_name(
                    'ProfileNav-item--following').find_element_by_class_name(
                        'ProfileNav-value').text
                if 'K' in number or 'M' in number:
                    return None
                else:
                    number = number.replace(',', '')
                    config.print_(user + " has " + str(number) + " following")
                    return int(number)
            except (NoSuchElementException, TimeoutException):
                config.print_("It seems that " + user + " is not following \
                anyone.")
                return 0
        else:
            return None

    def get_followers(self, user, limit=False):
        """Returns the username's set of followers."""
        config.print_("Processing get_followers of " + user)
        total_foll = self.get_num_followers(user)
        if total_foll == None:
            config.print_("!!! Couldn't retrieve followers !!!")
        return self._get_follx(total_foll, limit) if total_foll != None else set()

    def get_following(self, user, limit=False):
        """Returns the username's set of followings."""
        config.print_("Processing get_following of " + user)
        total_foll = self.get_num_following(user)
        if total_foll == None:
            config.print_("!!! Couldn't retrieve following !!!")
        return self._get_follx(total_foll, limit) if total_foll != None else set()
    
    def get_num_tweets(self, user):
        """Returns the number of tweets a user has made."""
        if user != None and len(user) > 0:
            self.firefox.get('https://twitter.com/' + user)
            try:
                WebDriverWait(self.firefox, 10).until(
                    ex_co.presence_of_element_located(
                        (By.CLASS_NAME, 'AppContainer')))
                count = self.firefox.find_element_by_class_name(
                    'ProfileNav-item--tweets').find_element_by_tag_name(
                        'a').get_attribute('title')
                count = count.replace(',','')
                index = count.find(' ')
                return int(count[:index]) if index != -1 else int(count)
            except (NoSuchElementException, TimeoutException):
                return None
        else:
            return None

    def get_favourite_count(self, user):
        """Returns the number of favourited tweets by a user."""
        self.firefox.get('https://twitter.com/' + user)
        try:
            WebDriverWait(self.firefox, 10).until(
                ex_co.presence_of_element_located(
                    (By.CLASS_NAME, 'AppContainer')))
            number = self.firefox.find_element_by_class_name(
                'ProfileNav-item--favorites').find_element_by_class_name(
                    'ProfileNav-value').text
            if 'K' in number or 'M' in number:
                return None
            else:
                number = number.replace(',', '')
                config.print_(user + " has " + str(number) + " favourites")
                return int(number)
        except (NoSuchElementException, TimeoutException):
            return None

    def get_favourite_counts_by_user(self, user, limit=False):
        """Returns a dict with the number of favourites done by a user
        to others."""
        if self.loged_in:
            num = self.get_favourite_count(user)
            if user == self.username:
                self.firefox.get('https://twitter.com/favorites')
            else:
                self.firefox.get('https://twitter.com/' + user + '/favorites')
            
            WebDriverWait(self.firefox, 10).until(
                ex_co.presence_of_element_located(
                    (By.CLASS_NAME, 'AppContainer')))
            if num == None:
                config.print_("!!! Couldn't retrieve the favourites !!!")
            return self._get_favs_who(num, limit) if num != None else {}

    def _get_js_stream(self):
        """Returns the js-stream-items of the current page."""
        soup = BeautifulSoup(self.firefox.page_source, "lxml")
        tweets = [element.find_all(class_='ProfileTweet')[0]
                  for element in soup.find_all(class_='js-stream-item')]
        return tweets

    def _get_tweet_id_js_stream(self, js_stream):
        """Returns the tweet-id from a js stream element."""
        temp = js_stream['data-item-id']
        return int(temp) if temp != None else None

    def _get_tweet_author_js_stream(self, js_stream):
        """Returns the tweet-author from a js stream element."""
        return js_stream['data-screen-name']

    def _get_tweet_author_id_js_stream(self, js_stream):
        """Returns the tweet-author-id from a js stream element."""
        temp = js_stream['data-user-id']
        return int(temp) if temp != None else None

    def _get_tweet_time_date_js_stream(self, js_stream):
        """Returns the tweet-timedate from a js stream element."""
        temp = js_stream.find_all(class_='ProfileTweet-header')[0]
        if temp != None:
            timestamp = temp.find_all(class_='ProfileTweet-timestamp')
            return timestamp[0]['title']
        else:
            return None

    def _get_tweet_text_js_stream(self, js_stream):
        """Returns the tweet text from a js stream element."""
        if len(js_stream) > 0:
            return js_stream[0].find(class_='ProfileTweet-contents').find(
                class_='ProfileTweet-text').getText()
        else:
            return None
    
    def _get_favs_who(self, expected, limit):
        """Private method to process the fav tweets."""
        if self._is_timeline_protected():
            return None
        scroll = previous = error = 0
        ret = {}
        processed = set()
        if limit and limit < expected:
            print "limit", limit
            print "expected", expected
            expected = limit
        config.print_same_line("Processing...", True)
        while len(processed) < expected and error < Twitter.MAX_ERRORS_USER:
            scroll = self._scroll_down(scroll)
            tweets = self._get_js_stream()
            for tweet in tweets:
                # Check tweet id
                tweet_id = self._get_tweet_id_js_stream(tweet)
                if tweet_id not in processed:
                    processed.add(tweet_id)
                    user = self._get_tweet_author_js_stream(tweet)
                    if user not in ret:
                        ret[user] = 0
                    ret[user] += 1
            now = len(processed) * 100 / expected
            if now != previous:
                previous = now
                config.print_same_line(str(now) + "%..")
                error = 0
            else:
                error += 1
        config.print_end()
        return ret

    def get_user_bio(self, user):
        """Returns a user's profile description."""
        self.firefox.get('https://twitter.com/' + user)
        try:
            WebDriverWait(self.firefox, 10).until(
                ex_co.presence_of_element_located(
                    (By.CLASS_NAME, 'AppContainer')))
            soup = BeautifulSoup(self.firefox.page_source, "lxml")
            temp = soup.find_all(class_='ProfileHeaderCard')
            return temp[0].find_all(
                class_='ProfileHeaderCard-bio')[0].get_text()\
                if len(temp) > 0 else None
        except (NoSuchElementException, TimeoutException):
            return None

    def _get_badges(self, user):
        """Returns the badges of a user."""
        self.firefox.get('https://twitter.com/' + user)
        try:
            WebDriverWait(self.firefox, 10).until(
                ex_co.presence_of_element_located(
                    (By.CLASS_NAME, 'AppContainer')))
            soup = BeautifulSoup(self.firefox.page_source, "lxml")
            temp = soup.find_all(class_='ProfileHeaderCard')
            if len(temp) > 0:
                badges = temp[0].find_all(class_=
                                          'ProfileHeaderCard-name')[0].find_all(
                                              class_='ProfileHeaderCard-badges')
                if badges:
                    ret = [x['title'] for x \
                           in badges[0].find_all(class_='js-tooltip')]
                    return ret
                else:
                    return False
        except (NoSuchElementException, TimeoutException):
            return None

    def is_official(self, user):
        """Checks whether the specified account is official or not."""
        ret = self._get_badges(user)
        if ret == None:
            return False
        else:
            return ret if type(ret) == bool else str('Verified account') in ret

    def get_tweets_timedates_last(self, user, lastx=50):
        """Returns a dict of tweet-id, timestamp of the last x tweets of a User"""
        if user != None:
            num = self.get_num_tweets(user)
            lastx = num if num < lastx else lastx
            self.firefox.get('https://twitter.com/' + user)
            try:
                if self._is_timeline_protected():
                    return None
                else:
                    scroll = previous = error = 0
                    ret = []
                    processed = set()
                    while len(processed) < lastx and \
                      error < Twitter.MAX_ERRORS_USER:
                        scroll = self._scroll_down(scroll)
                        soup = BeautifulSoup(self.firefox.page_source, "lxml")
                        tweets = [x.find_all(class_='ProfileTweet')
                                 for x in soup.find_all(class_='js-stream-item')]
                        for tweet in tweets:
                            if len(tweet) > 0:
                                tweet_id = self._get_tweet_id_js_stream(tweet[0])
                                if tweet_id != None and \
                                  tweet_id not in processed:
                                    processed.add(tweet_id)
                                    timestamp = \
                                      self._get_tweet_time_date_js_stream(
                                          tweet[0])
                                    if timestamp != None:
                                        ret.append({'id': tweet_id,
                                                    'timestamp': timestamp})
                        now = len(ret) * 100 / lastx
                        if now != previous:
                            previous = now
                            config.print_same_line(str(now) + "%..")
                            error = 0
                        else:
                            error += 1
                    return ret
            except (NoSuchElementException, TimeoutException):
                return None

    def get_whole_tweets_last(self, user, lastx=100):
        """Returns the last x tweets from a user, giving the author, author-id,
        tweet-id, tweet and timestamp"""
        if user != None:
            num = self.get_num_tweets(user)
            lastx = num if num < lastx else lastx
            try:
                if self._is_timeline_protected():
                    return None
                else:
                    scroll = previous = error = 0
                    ret = []
                    processed = set()
                    while len(processed) < lastx and \
                      error < Twitter.MAX_ERRORS_USER:
                      scroll = self._scroll_down(scroll)
                      soup = BeautifulSoup(self.firefox.page_source, "lxml")
                      tweets = [x.find_all(class_='ProfileTweet')
                                for x in soup.find_all(class_='js-stream-item')]
                      for tweet in tweets:
                          if len(tweet) > 0:
                              tweet_id = self._get_tweet_id_js_stream(tweet[0])
                              if tweet_id != None and tweet_id not in processed:
                                  processed.add(tweet_id)
                                  text = self._get_tweet_text_js_stream(tweet)
                                  author_id = \
                                    self._get_tweet_author_id_js_stream(tweet[0])
                                  author = self._get_tweet_author_js_stream(
                                      tweet[0])
                                  timestamp = self._get_tweet_time_date_js_stream(
                                          tweet[0])
                                  ret.append({'id': tweet_id, 'tweet': text,
                                              'author-id': author_id,
                                              'author': author,
                                              'timestamp': timestamp})
                      now = len(ret) * 100 / lastx
                      if now != previous:
                          previous = now
                          config.print_same_line(str(now) + "%..")
                          error = 0
                      else:
                          error += 1
                    return ret
            except (NoSuchElementException, TimeoutException):
                return None

def get_hastags_from_tweet(tweet):
    """Returns a list of the hastags in a tweet."""
    if tweet == None or len(tweet) == 0:
        return None
    else:
        matcher_hastags = re.compile('(#\w+)')
        return matcher_hastags.find_all(tweet)


def get_mentions_from_tweet(tweet):
    """Returns a list of the mentions in a tweet."""
    if tweet == None or len(tweet) == 0:
        return None
    else:
        matcher_mentions = re.compile('(@(\w|\d|_)+)')
        return [x[0] for x in matcher_mentions.find_all(tweet)]

if __name__ == '__main__':
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    tweets = twitter.get_whole_tweets_last('lifehacker', 5)
    for tweet in tweets:
        print tweet
    twitter._sign_out()
