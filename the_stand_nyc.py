#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract show information for The Stand NYC

Created on Wed Oct 25 23:06:54 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import calendar
from datetime import datetime
import re
from comedian_list import comedian_list 

#%%

# All of the shows are on this URL
url = 'http://thestandnyc.ticketfly.com/listing'

html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, "html.parser")

all_shows = []

list_view = soup.find('div', class_='list-view')
shows = list_view.findAll(attrs={'class': re.compile(r'^list-view-item')})

for show in shows:
    info = {}
    
    info['location'] = 'The Stand NYC'
    price_text = show.find('h3', class_='price-range').text.strip()
    dash_ix = price_text.find('-')
    if dash_ix >= 0:
        info['price'] = float(price_text[dash_ix + 3:].strip())
    else:
        pass
        info['price'] = float(price_text[1:].strip())
    
    try:
        info['ticket_link'] = show.find('a', class_='tickets')['href'].strip()
    except TypeError:
        continue
    
    details = show.find('div', class_='list-view-details vevent')
    
    info['show_title'] = details.find('h1').find('a').text
    info['acts'] = []
    
    # Find headliners from show_title
    for comedian in comedian_list:
        if comedian in info['show_title']:
            info['acts'].append({'name': comedian, 'type': 'headliner'})
                   
    # Get support acts for those that have them
    try:
        supports = details.find('h2', class_='supports description').find('a').text
        for support in supports.split(','):
            info['acts'].append({'name': support.strip(), 'type': 'support'})
    except:
        pass    
    
    day_date = details.find('h2', class_='dates').text
    
    # Convert day abbreviation to full day name
    abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))
    info['day'] = abbr_to_full[day_date[:3]]
    info['date'] = datetime.strftime(datetime.strptime(day_date[4:] + '.17', '%m.%d.%y'), '%B %d, %Y')
    
    # All shows have a show_time, only some have a door_time
    times = details.find('h2', class_='times')
    info['time'] = {}
    try:
        door_time = times.find('span', class_='doors').text
        info['time']['door_time'] = door_time[(door_time.find(':') + 1):].strip()
    except AttributeError:
        pass
        
    show_time = times.find('span', class_='start dtstart').contents[1]
    colon_ix = show_time.find('Show:')
    if colon_ix >= 0:
        info['time']['show_time'] = show_time[(colon_ix + 6):].strip()
    else:
        info['time']['show_time'] = show_time.strip()
        
    info['show_note'] = details.find('h2', class_='age-restriction over-16').text.strip()
    
    all_shows.append(info)
