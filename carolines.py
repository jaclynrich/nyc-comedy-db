#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 02:37:22 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import calendar
from datetime import datetime
import re
from get_comedian_list import comedian_list

#%%
url = 'http://www.carolines.com/full-schedule/'

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
        info['acts'].append({'name': comedian, 'type': 'headliner'})
    print(info['acts'])
    
    # Look for headliners in the show subtitle
    subtitle = show_info.findAll('h2')[1].text
    in_list_sub = [comedian for comedian in comedian_list if comedian in subtitle]
    for comedian in in_list_sub:
        info['acts'].append({'name': comedian, 'type': 'headliner'})
    print(info['acts'])
    
    date_info = show.find('div', class_='show-date')
    day_date = date_info.find('p', class_='white').text.strip()
    
    # Convert day abbreviation to full day name
    abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))
    info['day'] = abbr_to_full[day_date[:3]]
    
    abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))

    month = day_date[4:7]
    date = day_date[8:-2]
    info['date'] = datetime.strftime(datetime.strptime(month + ' ' + date + \
                                     ' 17', '%b %d %y'), '%B %d, %Y')

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
    info['time']['show_time'] = corrected_time
    
    # Parse the ticket_link url to get the price
    
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(info['ticket_link'],headers=hdr)
    page = urlopen(req)
    reservation_soup = BeautifulSoup(page, 'html.parser')
    price = reservation_soup.find('strong', class_='EDPPriceVerticalAlign')

    if price is not None:
        info['price'] = float(price.text[1:])

    show_list.append(info)
    

