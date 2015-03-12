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
                    input_pass = self.firefox.find_element_by_id('signin-password')
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
        """Scrolls down to the specified value, returns expected position. """
        to += 4500
        self.firefox.execute_script('scroll(0, ' + str(to) + ');')
        return to

    def _get_follx(self, expected, limit):
        """Private method to get the js-stream-items representing users."""
        scroll = previous = 0
        ret = set()
        if limit:
            expected = limit
        config.print_same_line("Processing...", True)
        while len(ret) < expected:
            soup = BeautifulSoup(self.firefox.page_source, "lxml")
            scroll = self._scroll_down(scroll)
            elements_soup = soup.find_all(class_='js-stream-item')
            ret.update(str(element.find_all(class_='ProfileCard')[0]
                           ['data-screen-name']) for element in elements_soup)
            now = len(ret) * 100 / expected
            if now != previous:
                previous = now
                config.print_same_line(str(now) + "%..")
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
            number = self.firefox.find_element_by_class_name(
                'ProfileNav-item--followers').find_element_by_class_name(
                    'ProfileNav-value').text
            if 'K' in number or 'M' in number:
                return None
            else:
                number = number.replace(',', '')
                config.print_(user + " has " + str(number) + " followers")
                return int(number)
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
            number = self.firefox.find_element_by_class_name(
                'ProfileNav-item--following').find_element_by_class_name(
                    'ProfileNav-value').text
            if 'K' in number or 'M' in number:
                return None
            else:
                number = number.replace(',', '')
                config.print_(user + " has " + str(number) + " following")
                return int(number)
        else:
            return None
    
    def get_followers(self, user, limit=False):
        """Returns the username's set of followers."""
        config.print_("Processing get_followers of " + user)
        total_foll = self.get_num_followers(user)
        if total_foll == None:
            config.print_(" !!! Couldn't retrieve followers !!!")
        return self._get_follx(total_foll, limit) if total_foll != None else set()

    def get_following(self, user, limit=False):
        """Returns the username's set of followings."""
        config.print_("Processing get_following of " + user)
        total_foll = self.get_num_following(user)
        if total_foll == None:
            config.print_(" !!! Couldn't retrieve following !!!")
        return self._get_follx(total_foll, limit) if total_foll != None else set()
