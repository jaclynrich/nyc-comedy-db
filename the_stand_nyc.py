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
import csv
import json

def main():
    comedian_list = []
    with open('comedian_list.csv', 'r') as f:
        for line in f:
            comedian_list.append(line.strip())
    
    # Sort by length of name, and later only get the first match = longest match
    comedian_list.sort(key=len, reverse=True)
    
    # All of the shows are on this URL
    url = 'http://thestandnyc.ticketfly.com/listing'
    
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    list_view = soup.find('div', class_='list-view')
    shows = list_view.findAll(attrs={'class': re.compile(r'^list-view-item')})
    
    all_shows = []
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
        
        # Find performers from show_title
        # First look for Roy Wood, Jr. before split - he is the only performer
        # with a comma
        if 'Roy Wood, Jr.' in info['show_title']:
            info['acts'].append({'name': 'Roy Wood, Jr.', 'type': 'performer'})    
        title_parts = info['show_title'].split(',')
        t = {comedian.lower() for comedian in comedian_list}
        in_list = []
        for part in title_parts:
            in_list = [comedian for comedian in t if comedian in part.lower()]
            performer = None
            if len(in_list) > 1:
                performer = max(in_list, key=len)    
            elif len(in_list) == 1:
                performer = in_list[0]
            
            if performer is not None:    
                s = re.search(performer, part, re.IGNORECASE)
                if s and not s.group().islower():
                    info['acts'].append({'name': s.group(), 'type': 'performer'})
    
        # Get support acts for those that have them
        try:
            supports = details.find('h2', class_='supports description').\
                       find('a').text
            # First look for Roy Wood, Jr. before split - he is the only performer
            # with a comma
            if 'Roy Wood, Jr.' in supports:
                info['acts'].append({'name': 'Roy Wood, Jr.', 'type': 'support'})
            for support in supports.split(','):
                info['acts'].append({'name': support.strip(), 'type': 'support'})
        except:
            pass
        
        # If info['acts'] is an empty list, delete it
        if info['acts'] == []:
            del info['acts']
        
        day_date = details.find('h2', class_='dates').text
        month_day = day_date[4:]
        
        # Convert day abbreviation to full day name
        abbr_to_full = dict(zip(list(calendar.day_abbr), list(calendar.day_name)))
        info['day'] = abbr_to_full[day_date[:3]]
        
        # Append 17 to dates in 2017, 18 to those in 2018
        if month_day.startswith('1.'):
            info['date'] = (datetime.strptime(month_day + '.18', \
                        '%m.%d.%y').strftime('%B %-d, %Y'))
        else:
            info['date'] = (datetime.strptime(month_day + '.17', \
                        '%m.%d.%y').strftime('%B %-d, %Y'))
        
        # All shows have a show_time, only some have a door_time
        times = details.find('h2', class_='times')
        info['time'] = {}
        info['time_str'] = {}
        try:
            door_time = times.find('span', class_='doors').text
            info['time_str']['door_time'] = door_time[(door_time.find(':') + 1):]\
                .strip()
            info['time']['door_time'] = info['date'] + ' ' + \
                door_time[(door_time.find(':') + 1):].strip()
        except AttributeError:
            pass
            
        show_time = times.find('span', class_='start dtstart').contents[1]
        colon_ix = show_time.find('Show:')
        
        # Correct showtimes of 11:59 to 12:00
        if show_time == '11:59 pm':
            show_time = '12:00 am'
        
        if colon_ix >= 0:
            info['time_str']['show_time'] = show_time[(colon_ix + 6):].strip()
            info['time']['show_time'] = info['date'] + ' ' + \
                show_time[(colon_ix + 6):].strip()
        else:
            info['time_str']['show_time'] = show_time.strip()
            info['time']['show_time'] = info['date'] + ' ' + show_time.strip()
        
        # Include another date field that will not be converted to a datetime
        # when it is loaded into MongoDB
        info['date_str'] = info['date']
    
        info['show_note'] = details.find('h2', class_='age-restriction over-16').\
                            text.strip()
        
        all_shows.append(info)
    
    # Save all_shows as a set of json documents
    with open('the_stand_shows.json', 'w') as f:
        json.dump(all_shows, f, indent=4)
    print('Wrote the_stand_shows.json')
        
# Assemble list of comedians from The Stand's site for comedian_list
def get_comedian_list():
    comedians = set()
    all_urls = []
    all_urls.append('http://www.standupny.com/comedians-list/')
    
    html = urllib.request.urlopen(all_urls[0]).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    pages = soup.find('div', class_='pagination-custom')
    for page in pages.findAll('a'):
        all_urls.append(page['href'])
    
    for url in all_urls:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        for h in soup.findAll('h2', class_='schedule-title-pro'):
            comedians.add(h.find('a').text)
    
    comedians = list(comedians)
    
    with open('the_stand_comedians.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for line in comedians:
            writer.writerow([line])
            
if __name__ == '__main__':
    main()