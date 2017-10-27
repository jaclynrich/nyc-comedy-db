#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract show information for the Comedy Cellar

Created on Sat Sep 23 12:26:59 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
import requests
from bs4 import BeautifulSoup

# Gets all of the show information for one date
def extract_data(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    
    places = ['MacDougal Street', 'Village Underground', 'Fat Black Pussycat', 'Fat Black Pussycat Lounge']
    
    # This block will be the same for all shows
    day_date = soup.find('div', class_='show-search-title').text.strip()
    ix_space = day_date.find(' ')
    day = day_date[:ix_space]
    date = day_date[ix_space+1:]
    link = soup.find('a', class_='make-comedy-reservation-link')['href']
    
    shows = []
    for gig in soup.findAll('div', class_='show'):
        show = {}
        show['day'] = day
        show['date'] = date
        show['reservation_link'] = link
            
        time_location = gig.find('span', class_='show-time closed').text.strip()
        time, location = time_location.split('|')
        show['time'] = time.strip()[:-5]
        
        pm_ix = location.find('pm')
        if pm_ix > 0:
            show['show_name'] = location.strip()[pm_ix+2:]
        else:
            show['location'] = location.strip()
        
        note = gig.find('p', class_='show-note')
        if note is not None:
            note = note.text.strip()
            show['show_note'] = note
            matching = [place for place in places if place in note]
            if len(matching) == 1:
                show['location'] = matching[0]
                print(show['location'])
        
        # If the show location is not stated
        # then it is assumed to be MacDougal Street
        if show.get('location') == None:
            show['location'] = 'MacDougal Street'
            
        show['acts'] = []
        performers = []
        for performer in gig.findAll('span', class_='comedian-block-desc-name'):
            p = ' '.join(performer.getText().strip().split())
            if(p.startswith('MC')):
                mc_ix = p.find(':')
                show['acts'].append({'MC': p[mc_ix+2:]})
            else:
                performers.append(p)
        show['acts'].append({'performers': performers})
                
        shows.append(show)
    return shows

# Test function out for one page
url = 'http://www.comedycellar.com/line-up/'
shows_list = extract_data(url)

#%% Get date options from dropdown menu

date_options = []
value_options = []

html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, "html.parser")

options = soup.find('select', class_='dropkick filter-lineup-shows')
for option in options.findAll('option'):
    date_options.append(option.text.strip()) # just in case it is needed
    value_options.append(option['value'].strip())

#%% Get all of the shows for all of the dates available on the site

full_show_list = []
base_url = 'http://www.comedycellar.com/line-up/?_'

for value in value_options:
    url = base_url + urllib.parse.urlencode({'date': value})
    r = requests.get(url)
    full_show_list.append(extract_data(url))