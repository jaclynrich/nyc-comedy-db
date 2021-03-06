#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract show information for the Comedy Cellar

Created on Sat Sep 23 12:26:59 2017

@author: Jackie
"""

import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import csv
import json
from datetime import datetime

# Gets all of the show information for one date
def extract_data(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    
    places = ['MacDougal Street', 'Village Underground', 'Fat Black Pussycat']
    
    # This block will be the same for all shows
    day_date = soup.find('div', class_='show-search-title').text.strip()
    ix_space = day_date.find(' ')
    day = day_date[:ix_space]
    date_str = day_date[ix_space+1:]
    date = datetime.strptime(date_str, '%B %d, %Y').strftime('%B %-d, %Y')
    link = soup.find('a', class_='make-comedy-reservation-link')['href']
    
    # Get price from ticket_link url
    # Get source of iframe to open with selenium
    reservation_html = urllib.request.urlopen(link).read()
    reservation_soup = BeautifulSoup(reservation_html, "html.parser")
    frame = reservation_soup.find('iframe', attrs={'name':'reservation_iframe'})
    
    BASE_URL = 'http://www.comedycellar.com/'
    frame_url = urljoin(BASE_URL, frame['src'])
    
    # Get all the prices for that date as a list
    chromedriver = '/Users/Jackie/anaconda/chromedriver/chromedriver'
    browser = webdriver.Chrome(chromedriver)
    browser.get(frame_url)
    
    price_soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.close()
    
    prices = []
    showtimes = price_soup.find('div', class_='showtimes')
    for p in showtimes.findAll('span', class_='cover-span'):
        m = re.match(r'([$]\d+)', p.text)
        if m:
            prices.append(float(m.group()[1:]))
        else:
            prices.append(-1)
    
    times = []
    for p in showtimes.findAll('span'):
        attributes_dictionary = p.attrs
        if attributes_dictionary == {}:
            times.append(p.text.split()[0])
    
    # correct times
    corrected_times = []
    for time in times:
        am_pm = None
        m = re.search('.m', time)
        if m:
            am_pm = m.group()
        time = re.sub('.m', '', time)
        if len(time) < 3:
            time = time + ':00'
        if am_pm is not None:
            corrected_times.append(time + ' ' + am_pm)
        else:
            corrected_times.append(time + ' pm')
                                    
    price_times = dict(zip(corrected_times, prices))
    
    shows = []
    for gig in soup.findAll('div', class_='show'):
        show = {}
        show['day'] = day
        show['date'] = date
        show['date_str'] = date
        show['ticket_link'] = link
        
        time_location = gig.find('span', class_='show-time closed').text.strip()
        time, location = time_location.split('|')
        show_time = time.strip()[:-5]
        
        # Some times are incorrectly marked as having hour:01
        show_time = re.sub(':01', ':00', show_time)
        show['time'] = {}
        show['time_str'] = {}
        show['time']['show_time'] = show['date'] + ' ' + show_time
        show['time_str']['show_time'] = show_time

        pm_ix = location.find('pm')
        if pm_ix > 0:
            show['show_title'] = location.strip()[pm_ix+2:]
        else:
            if location.strip() in places: #only assign location if it is places
                show['location'] = location.strip()
        
        # Look for possible location name in show note
        note = gig.find('p', class_='show-note')
        if note is not None:
            note = note.text.strip()
            show['show_note'] = note
            matching = [place for place in places if place in note]
            if len(matching) == 1:
                show['location'] = matching[0]
        
        # If the show location is not stated
        # then it is assumed to be MacDougal Street
        if show.get('location') == None:
            show['location'] = 'MacDougal Street'
            
        # Fix show locations that do not include the full name
        if show.get('location') == 'Fat Black Pussycat':
            show['location'] = 'Fat Black Pussycat Lounge'
            
        show['acts'] = []
        for performer in gig.findAll('span', class_='comedian-block-desc-name'):
            p = ' '.join(performer.getText().strip().split())
            if(p.startswith('MC')):
                mc_ix = p.find(':')
                show['acts'].append({'name': p[mc_ix+2:], 'type': 'MC'})
            elif p == 'MORE TO BE ANNOUNCED':
                continue
            else:
                show['acts'].append({'name': p, 'type': 'performer'})
        
        # If info['acts'] is an empty list, delete it
        if show['acts'] == []:
            del show['acts']
        
        # Append Comedy Cellar to each location name
        show['location'] = 'Comedy Cellar - ' + show['location']
        
        # Price - loop through prices and assign according to show_ix
        time = show['time_str']['show_time']
        try:
            if price_times[time] > -1:
                show['price'] = float(price_times[time])      
        # Look for show in show_note
        except KeyError:
            if note is not None:
                m = re.search(r'[$](\d+)', show['show_note'])
                if m:
                    show['price'] = float(m.group()[1:])
        
        shows.append(show)
        
    return shows

# Get date options from dropdown menu
def get_date_options():
    date_options = []
    value_options = []
    
    url = 'http://www.comedycellar.com/line-up/'
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    
    options = soup.find('select', class_='dropkick filter-lineup-shows')
    for option in options.findAll('option'):
        date_options.append(option.text.strip()) # just in case it is needed
        value_options.append(option['value'].strip())
    
    return value_options

# Get all of the shows for all of the dates available on the site and write
# it as a json file
def write_all_show_info(value_options): 
    all_shows = []
    shows_unflat = []
    base_url = 'http://www.comedycellar.com/line-up/?_'
    
    for value in value_options:
        url = base_url + urllib.parse.urlencode({'date': value})
        shows_unflat.append(extract_data(url))
    
    all_shows = [item for sublist in shows_unflat for item in sublist]

    # Save all_shows as a set of json documents
    with open('cellar_shows.json', 'w') as f:
        json.dump(all_shows, f, indent=4)
    print('Wrote cellar_shows.json')
    
# Assemble list of comedians for comedian_list
def write_comedy_list(all_shows):
    comedians = set()
    for show in all_shows:
        for act in show['acts']:
            comedians.add(act['name'])
    comedians = list(comedians)
    
    with open('cellar_comedians.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for line in comedians:
            writer.writerow([line])
            
if __name__ == '__main__':
    value_options = get_date_options()
    write_all_show_info(value_options)