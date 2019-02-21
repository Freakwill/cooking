#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import bs4
import requests
import furl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from fake_useragent import UserAgent
ua = UserAgent()

HOME = "https://www.meishij.net"
SEARCH_PAGE = 'https://so.meishi.cc/'

def prettyDict(d):
    return '\n'.join(['%s: %s' % (k, v) for k, v in d.items()])

def prettyList(l):
    return '\n'.join(['%s. %s' % (k, a) for k, a in enumerate(l, 1)])

def index2url(index):
    return 'https://www.meishij.net/zuofa/%s.html' % index

TEMPLATE = """{title}:
==========
信息: 
{info}
----------
*{remark}*
主料: 
{zl}
辅料: 
{fl}
----------
步骤:
{steps}
----------
"""

class Recipe(object):
    '''Recipe Class
    '''
    def __init__(self, title='', steps=[], materials={}, info={}, remark=''):
        """
        Keyword Arguments:
            title {str} -- 菜名 (default: {''})
            steps {list} -- 烹饪步骤 (default: {[]})
            materials {dict} -- 用料, 主料、辅料 (default: {{}})
            info {dict} -- 信息 (default: {{}})
        """
        self.title = title
        self.info = info
        self.steps = steps
        self.materials = materials
        self.remark = remark

    def __getstate__(self):
        return self.title, self.steps, self.materials, self.info

    def __getstate__(self, state):
        self.title, self.steps, self.materials, self.info = state

    def __str__(self):
        return TEMPLATE.format(title=self.title, info=self.info, zl=prettyDict(self.materials['主料']), fl=prettyDict(self.materials['辅料']), steps=prettyList(self.steps), remark=self.remark)

    @staticmethod
    def fromIndex(index):
        """Get recipe by index
        
        Arguments:
            index {[str} -- may be pinyin of the title of the recipe
        
        Returns:
            Recipe
        """
        URL = index2url(index)
        return Recipe.fromURL(URL)

    @staticmethod
    def fromURL(URL):

        options = webdriver.ChromeOptions()
        options.set_headless(headless=True)

        options.add_argument('user-agent="%s"'%ua.random)
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(URL)
        soup = bs4.BeautifulSoup(driver.page_source, "lxml")

        main = soup.find('div', {'class': 'main clearfix'})
        title = main.find('h1', {'class': 'title'}).text

        info = {li.strong.text:li.a.text for li in main.find('div', {'class': 'info2'}).find_all('li')}
        
        materials = main.find('div', {'class': 'materials'})
        remark = materials.p.text
        materials = {m: {li.h4.a.text:li.span.text for li in div.find_all('li')} for m, div in zip(('主料', '辅料'), materials.find_all('div'))}
        method = main.find('div', {'class': 'editnew edit'})
        steps = [step.text.partition('.')[-1].strip() for step in method.find_all('div', {'class': 'content clearfix'})]
        return Recipe(title, steps, materials, info, remark)

    @staticmethod
    def search(keyword, **kwargs):
        """search recipe with keyword and other information
        
        Arguments:
            keyword {str} -- keyword for searching
            **kwargs
        
        Example:
        meishijie.py search --keyword 蛋炒饭 --kw 160
        """
        kwargs.update({'q':keyword})
        resp = requests.get(SEARCH_PAGE, params=kwargs)
        soup = bs4.BeautifulSoup(resp.text, 'lxml')
        for div in soup.find('div', {'class':'search2015_cpitem_w clearfix'}).find_all('div', {'class':'search2015_cpitem'}):
            print(div.a['href'])
            print(div.a['title'])

    @staticmethod
    def show(index):
        """
        Example:
        Folders/生活/meishijie.py show --index danchaofan_16
        """
        print(Recipe.fromIndex(index))

if __name__ == '__main__':
    import fire
    fire.Fire(Recipe)
