#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 12:26:59 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
import requests
from bs4 import BeautifulSoup

#%% This gets all of the show information for one date

url = 'http://www.comedycellar.com/line-up/'
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, "html.parser")

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
    
    time_more = gig.find('span', class_='show-time closed').text.strip()
    time_ix = time_more.find('m')
    show['time'] = time_more[:time_ix+1]
    show['performers'] = []
    
    note = gig.find('p', class_='show-note')
    if note is not None:
        show['show_note'] = note.text.strip()
    
    for performer in gig.findAll('span', class_='comedian-block-desc-name'):
        p = ' '.join(performer.getText().strip().split())
        if(p.startswith('MC')):
            mc_ix = p.find(':')
            show['MC'] = p[mc_ix+2:]
        else:
            show['performers'].append(p)
            
    shows.append(show)

# Include show name, location, comedian descriptions

# Change how stored - make it a dictionary of dictionaries
# with each day, date tuple as the key?

#%% Encapsulate getting data for one page of data into a function

url = 'http://www.comedycellar.com/line-up/'

def extract_data(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    
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
        
        time_more = gig.find('span', class_='show-time closed').text.strip()
        time_ix = time_more.find('m')
        show['time'] = time_more[:time_ix+1]
        show['performers'] = []
        
        note = gig.find('p', class_='show-note')
        if note is not None:
            show['show_note'] = note.text.strip()
        
        for performer in gig.findAll('span', class_='comedian-block-desc-name'):
            p = ' '.join(performer.getText().strip().split())
            if(p.startswith('MC')):
                mc_ix = p.find(':')
                show['MC'] = p[mc_ix+2:]
            else:
                show['performers'].append(p)
                
        shows.append(show)
    return shows

shows_list = extract_data(url)

#%% Get date options from dropdown

date_options = []
value_options = []
options = soup.find('select', class_='dropkick filter-lineup-shows')
for option in options.findAll('option'):
    date_options.append(option.text.strip()) # just in case need it
    value_options.append(option['value'].strip())

#%% Get all of the shows for all of the dates available on the site

full_show_list = []
base_url = 'http://www.comedycellar.com/line-up/?_'

for value in value_options:
    url = base_url + urllib.parse.urlencode({'date': value})
    r = requests.get(url)
    full_show_list.append(extract_data(url)) 

