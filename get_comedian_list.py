#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 18:51:36 2017

@author: Jackie
"""

import pandas as pd
import csv

def main():
    # Import manually assembled comedian list
    xlsx = pd.ExcelFile('manual_comedian_list.xlsx')
    df = pd.read_excel(xlsx, 'Sheet1', header=None, names=['comedians'])
    comedian_list = df['comedians'].tolist()
    
    # Append the comedians from The Comedy Cellar
    with open('cellar_comedians.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            comedian_list.append(line[0])
    
    # Append the comedians from The Stand's site to the manual list
    with open('the_stand_comedians.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            comedian_list.append(line[0])
            
    # Append the comedians from Wikipedia's list of NYC stand-ups
    with open('wiki_comedians.csv') as f:
        reader = csv.reader(f, delimiter=',')
        for line in reader:
            comedian_list.append(line[0])
    
    comedian_list = list(set(comedian_list))
    
    # Write out comedian_list as csv
    with open('comedian_list.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for c in comedian_list:
            writer.writerow([c])
    print('Wrote comedian_list.csv')

if __name__ == '__main__':
    main()