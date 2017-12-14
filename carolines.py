#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 02:37:22 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import calendar
from datetime import datetime
import re
import json

#%%
comedian_list = []
with open('comedian_list.csv', 'r') as f:
    for line in f:
        comedian_list.append(line.strip())

# Sort by length of name, and later only get the first match = longest match
comedian_list.sort(key=len, reverse=True)

def extract_data(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    show_list = []
    for show in soup.findAll('div', class_='schedul-block'):    
        info = {}
        info['location'] = 'Carolines'
        
        show_info = show.find('div', class_='show-info')
        info['show_title'] = show_info.find('a', class_='comedian-page')\
                                            ['title'].strip()    
        
        # Look for headliners in the show_title
        info['acts'] = []
        in_list = [comedian for comedian in comedian_list if comedian in info['show_title']]
        for comedian in in_list:
            info['acts'].append({'name': comedian, 'type': 'performer'})
        
        # Look for headliners in the show subtitle
        subtitle = show_info.findAll('h2')[1].text
        in_list_sub = [comedian for comedian in comedian_list if comedian in \
                       subtitle]
        for comedian in in_list_sub:
            info['acts'].append({'name': comedian, 'type': 'performer'})

        date_info = show.find('div', class_='show-date')
        day_date = date_info.find('p', class_='white').text.strip()
        
        # Convert day abbreviation to full day name
        abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))
        info['day'] = abbr_to_full[day_date[:3]]
        
        abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))
    
        month = day_date[4:7]
        date = day_date[8:-2]
        
        # Append 17 to dates in 2017, 18 to those in 2018
        if month == 'Dec':
            info['date'] = datetime.strptime(month + ' ' + date + ' 17', \
                        '%b %d %y').strftime('%B %-d, %Y')
        else:
            info['date'] = datetime.strptime(month + ' ' + date + ' 18', \
                        '%b %d %y').strftime('%B %-d, %Y')
    
        info['ticket_link'] = date_info.find('a', style='color:red')['href']
        time = date_info.find('a', style='color:red').text.strip().lower()
        
        space_ix = time.find(' ')
        if space_ix == -1:
            m_ix = time.find('m')
            time_parts = [time[:m_ix-1], time[m_ix-1:m_ix+1]]
            corrected_time = (' ').join(time_parts)
        else:
            corrected_time = re.sub(',', '', time)
        info['time'] = {}
        info['time_str'] = {}
        info['time_str']['show_time'] = corrected_time
        info['time']['show_time'] = info['date'] + ' ' + corrected_time
        
        # Parse the ticket_link url to get the price
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(info['ticket_link'],headers=hdr)
        page = urlopen(req)
        reservation_soup = BeautifulSoup(page, 'html.parser')
        price = reservation_soup.find('strong', class_='EDPPriceVerticalAlign')
        
        # Include another date field that will not be converted to a datetime 
        # when it is loaded into MongoDB
        info['date_str'] = info['date']
    
        if price is not None:
            info['price'] = float(price.text[1:])
    
        show_list.append(info)
        
    return show_list
    
#%% Get the urls of all of the different pages of shows

base_url = 'http://www.carolines.com'
urls = []
url = 'http://www.carolines.com/full-schedule/'
urls.append(url)

html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')
    
navigation = soup.find('div', class_='navigation nf-pagenavi')
for page_option in navigation.findAll('a'):
    url = page_option['href']
    urls.append(urljoin(base_url, url))
    
# Not all urls were available from the first page - so get the rest from
# the last page
html = urllib.request.urlopen(urls[len(urls)-1]).read()
soup = BeautifulSoup(html, 'html.parser')
navigation = soup.find('div', class_='navigation nf-pagenavi')
for page_option in navigation.findAll('a'):
    url = page_option['href']
    urls.append(urljoin(base_url, url))

# Remove duplicates from urls
no_duplicates_urls = set()
new_urls = []

for u in urls:
  if u in no_duplicates_urls: continue
  new_urls.append(u)
  no_duplicates_urls.add(u)

urls[:] = new_urls
    
#%% Get all of the shows for all of the dates available on the site

all_shows = []
shows_unflat = []
for url in urls:
    shows_unflat.append(extract_data(url))

all_shows = [item for sublist in shows_unflat for item in sublist]


#%% Save all_shows as a set of json documents
with open('carolines_shows.json', 'w') as f:
    json.dump(all_shows, f, indent=4)