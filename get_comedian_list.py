#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 18:51:36 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv

# Import manually assembled comedian list
comedian_list = []

xlsx = pd.ExcelFile('manual_comedian_list.xlsx')
df = pd.read_excel(xlsx, 'Sheet1', header=None, names=['comedians'])
comedian_list = df['comedians'].tolist()

# Append the comedians from The Comedy Cellar
with open('cellar_comedians.csv') as f:
    reader = csv.reader(f, delimiter=',')
    for line in reader:
        comedian_list.append(line[0])

# Append the comedians from The Stand's site to the manual list
all_urls = []
all_urls.append('http://www.standupny.com/comedians-list/')

html = urllib.request.urlopen(all_urls[0]).read()
soup = BeautifulSoup(html, 'html.parser')

pages = soup.find('div', class_='pagination-custom')
for page in pages.findAll('a'):
    all_urls.append(page['href'])

body = soup.find('ul', id='schedule-content-progression')
class_name = 'schedule3column-pro item-pro-schedule comedians'
for section in body.findAll('li', class_=class_name):
    comedian_list.append(section.find('a', href=re.compile\
                        (r'^http://www.standupny.com/comedians/')).text)

for url in all_urls[1:]:
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('ul', id='schedule-content-progression')
    for section in body.findAll('li', class_=class_name):
        comedian_list.append(section.find('a', href=re.compile\
                            (r'^http://www.standupny.com/comedians/')).text)

# Append the comedians from wikipedia's stand-up comedian list
url = 'https://en.wikipedia.org/wiki/List_of_United_States_stand-up_comedians'

html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

for comedian in soup.findAll('li'):
    comedian = comedian.text
    if comedian == 'List of New York Improv comedians':
        break
    
    # Remove other names in parentheses
    paren_ix = comedian.find('(')
    if paren_ix > -1:
        comedian = comedian[:paren_ix].strip()
    # Do not include singular letters from wikipedia's page
    if len(comedian) > 1:
        comedian_list.append(comedian)

comedian_list = list(set(comedian_list))