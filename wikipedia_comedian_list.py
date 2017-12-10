#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:40:57 2017

Get comedians from wikipedia's stand-up comedian list

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import csv

#%%
url = 'https://en.wikipedia.org/wiki/List_of_United_States_stand-up_comedians'

comedians = set()
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

for comedian in soup.findAll('li'):
    comedian = comedian.text
    if comedian == 'List of New York Improv comedians':
        break
    
    # Remove other names in parentheses and after commas
    paren_ix = comedian.find('(')
    if paren_ix > -1:
        comedian = comedian[:paren_ix].strip()
    comma_ix = comedian.find(',')
    if comma_ix > -1:
        comedian = comedian[:comma_ix].strip()
    # Do not include singular letters from wikipedia's page
    if len(comedian) > 1:
        comedians.add(comedian)

comedians = list(comedians)

with open('wiki_comedians.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',')
    for line in comedians:
        writer.writerow([line])