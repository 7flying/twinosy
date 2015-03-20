# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ex_co
from bs4 import BeautifulSoup
import config

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
                except NoSuchElementException, e:
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
            WebDriverWait(self.firefox, 10).until(
                    ex_co.presence_of_element_located((By.CLASS_NAME,
                                                       'AppContainer')))
            try:
                number = self.firefox.find_element_by_class_name(
                    'ProfileNav-item--followers').find_element_by_class_name(
                        'ProfileNav-value').text
                if 'K' in number or 'M' in number:
                    return None
                else:
                    number = number.replace(',', '')
                    config.print_(user + " has " + str(number) + " followers")
                    return int(number)
            except NoSuchElementException:
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
            WebDriverWait(self.firefox, 10).until(
                 ex_co.presence_of_element_located((By.CLASS_NAME,
                                                    'AppContainer')))
            try:
                number = self.firefox.find_element_by_class_name(
                    'ProfileNav-item--following').find_element_by_class_name(
                        'ProfileNav-value').text
                if 'K' in number or 'M' in number:
                    return None
                else:
                    number = number.replace(',', '')
                    config.print_(user + " has " + str(number) + " following")
                    return int(number)
            except NoSuchElementException:
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
        except NoSuchElementException:
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
    
    def _get_favs_who(self, expected, limit):
        """Private method to process the fav tweets."""
        if self._is_timeline_protected():
            return None
        scroll = previous = error = 0
        ret = {}
        processed = set()
        if limit and limit < expected:
            expected = limit
        config.print_same_line("Processing...", True)
        while len(processed) < expected and error < Twitter.MAX_ERRORS_USER:
            scroll = self._scroll_down(scroll)
            soup = BeautifulSoup(self.firefox.page_source, "lxml")
            tweets = [element.find_all(class_='ProfileTweet')[0]
                      for element in soup.find_all(class_='js-stream-item')]
            for tweet in tweets:
                # Check tweet id
                tweet_id = int(tweet['data-item-id'])
                if tweet_id not in processed:
                    processed.add(tweet_id)
                    user = tweet['data-screen-name']
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
        WebDriverWait(self.firefox, 10).until(ex_co.presence_of_element_located(
            (By.CLASS_NAME, 'AppContainer')))
        soup = BeautifulSoup(self.firefox.page_source, "lxml")
        temp = soup.find_all(class_='ProfileHeaderCard')
        return temp[0].find_all(class_='ProfileHeaderCard-bio')[0].get_text() if len(temp) > 0 else None
            
