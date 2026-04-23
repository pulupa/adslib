#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
adslib.py

"""

#%%

"""
Set up imports
"""

import os
import re
import sys
import argparse
import calendar
import requests
import csv

#%%

"""
Routine to use initials instead of full names
"""

def extract_initial(first_name):
    """Extract an initial from a first name

    >>> extract_initial('First')
    'F.'
    """    
        
    try:
        found_re = re.search("[^ .]*?[^\W]", first_name)
        found = found_re.group(0) + '.'
    except AttributeError:
        found = first_name
    
    return(found)

def initialize_names(full_name):
    """From an input name (Last, First) return initialized name (Last, F.)

    >>> initialize_names('Last, First Middle')
    'Last, F.M.'
    >>> initialize_names('Last, F. M.')
    'Last, F.M.'
    >>> initialize_names('Last')
    'Last'
    >>> initialize_names('Last, Hyphenated-First')
    'Last, H.-F.'
    >>> initialize_names('Compound Last, First M')
    'Compound Last, F.M.'
    >>> initialize_names('Hyphenated-Last, First')
    'Hyphenated-Last, F.'
    >>> initialize_names('宮崎 駿')
    '宮崎 駿'
    >>> initialize_names('Гребенщиков, Борис')
    'Гребенщиков, Б.'
    """
    
    split_name = full_name.split(',', 1)

    last_name = split_name[0]
    
    n_names = len(split_name)
            
    if n_names > 1:
        
        first_names = split_name[1].replace('-',' -').replace('.',' ').split()
        
        initials_list = [extract_initial(first_name) for \
                         first_name in first_names]
        
        initials = "".join(initials_list)

        initialized_name = last_name + ", " + initials

    else:
        
        initialized_name = last_name
                
    return(initialized_name)
    
#%%

"""
Read in ADS dev key
"""

dev_key_file = os.path.expanduser('~') + '/.ads/dev_key'

if os.path.isfile(dev_key_file):

    with open (dev_key_file, 'r') as myfile:
        ads_dev_key_lines=myfile.readlines()

    ads_dev_key = ads_dev_key_lines[0]
    
else:
    
    print('ADS Dev Key not found')
    
    sys.exit()

#%%
    
"""
Load command line parameters
"""
    
parser = argparse.ArgumentParser(description='Download library from NASA ADS.')

parser.add_argument('library', type=str, 
                    help='NASA ADS Library ID')

parser.add_argument('--bibtex', type=str,
                    help='File for BibTeX output')

parser.add_argument('--bibcodes', type=str,
                    help='File containing all bibcodes')

parser.add_argument('--html', type=str, 
                    help='File for HTML output')

parser.add_argument('--csv', type=str, 
                    help='File for CSV output')

args = parser.parse_args()
    
#%%
    
"""
Get bibcodes from ADS library
"""

headers = {'Authorization': 'Bearer ' + ads_dev_key}

library = args.library

api_request_link = 'https://api.adsabs.harvard.edu/v1/biblib/libraries/'

start = 0

rows = 100

nrequests = 0

all_bibcodes = []

print("\nLoading bibcodes from input library:", args.library)

while True:

    request = requests.get(api_request_link + library, headers=headers,
                           params ={'start':'{}'.format(start), 
                           'rows':'{}'.format(rows)})

    lib_json = request.json()
    bibcodes = lib_json['documents']

    all_bibcodes.extend(bibcodes)

    if len(bibcodes) < rows:
        break

    if nrequests > 30:
        break
    
    nrequests += 1
    
    start += rows

print('Number of bibcodes retrieved:', len(all_bibcodes))
print('Remaining Requests:', request.headers['X-RateLimit-Remaining'])
print('Allowed Requests:', request.headers['X-RateLimit-Limit'])

#%%
"""
Send bigquery to ADS API to return a big structure with all of the bib info,
then output ADS information as HTML and/or CSV
"""

if args.html or args.csv:

    big = requests.post('https://api.adsabs.harvard.edu/v1/search/bigquery', 
                        params={'q':'*:*', 'wt':'json', 'fq':'{!bitset}', 
                                'fl':'abstract,author,bibcode,bibstem,doi,first_author,' +
                                'issue,page,pub,pubdate,title,volume,year',
                                'rows':'{}'.format(len(all_bibcodes))}, 
                                headers=headers,
                                data='bibcode\n'+'\n'.join(all_bibcodes))
    
    big_json = big.json()
    
    print('Number of bibcodes in library:', big_json['response']['numFound'])
    print('Remaining Big Requests:', big.headers['X-RateLimit-Remaining'])
    print('Allowed Big Requests:', big.headers['X-RateLimit-Limit'])

    docs = (big_json['response'])['docs']
    
    # HTML Export
    if args.html:
        print("\nOutput HTML file:", args.html)
        html = ''
        
        for doc in docs:
            html += '<p>\n'
            
            html += '<strong>'
            html += (doc['title'][0])
            html += '</strong>\n'
            
            html += ", ".join([initialize_names(author) for author in doc['author']]) + '\n'
        
            html += '<em>'
            if 'pub' in doc:
                html += doc['pub'] + ', '
        
            html += calendar.month_abbr[int((doc['pubdate'])[5:7])] + ' '
        
            html += doc['year']
            html += '</em>\n'
            
            if 'doi' in doc:
                html += '<a href="http://dx.doi.org/'+ doc['doi'][0] + '" target="_blank">DOI</a>\n'
            html += '<a href="http://adsabs.harvard.edu/abs/' + doc['bibcode'] + '" target="_blank">ADS URL</a>\n'
            
            html += '</p>\n'
        
        with open(args.html, "w", encoding='utf-8') as html_file:
            html_file.write(html)

    # CSV Export
    if args.csv:
        print("\nOutput CSV file:", args.csv)
        
        with open(args.csv, "w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Write Header
            writer.writerow(['Bibcode', 'Title', 'Authors', 'Publication', 'Date', 'DOI', 'ADS URL'])
            
            for doc in docs:
                bibcode = doc.get('bibcode', '')
                title = doc['title'][0] if 'title' in doc else ''
                authors = ", ".join([initialize_names(author) for author in doc.get('author', [])])
                pub = doc.get('pub', '')
                
                # Format Date safely using your existing logic
                try:
                    date = calendar.month_abbr[int((doc['pubdate'])[5:7])] + ' ' + doc['year']
                except (KeyError, ValueError, TypeError):
                    date = doc.get('year', '')
                    
                doi = doc['doi'][0] if 'doi' in doc else ''
                ads_url = 'http://adsabs.harvard.edu/abs/' + bibcode
                
                # Write row
                writer.writerow([bibcode, title, authors, pub, date, doi, ads_url])

#%%
"""
BibTex export
"""

if args.bibtex:

    print("\nOutput BibTeX file:", args.bibtex)

    bib = requests.post('https://api.adsabs.harvard.edu/v1/export/bibtex', 
                        headers=headers,
                        data='{"bibcode":["'+'","'.join(all_bibcodes)+'"]}')

    bib_json = bib.json()

    with open(args.bibtex, "w", encoding='utf-8') as bibtex_file:
        bibtex_file.write(bib_json['export'])

    print(bib_json['msg'])
    print('Remaining Export Requests:', bib.headers['X-RateLimit-Remaining'])
    print('Allowed Export Requests:', bib.headers['X-RateLimit-Limit'])

#%%
"""
Bibcodes export
"""

if args.bibcodes:

    print("\nOutput Bibcodes file:", args.bibcodes)

    with open(args.bibcodes, "w", encoding='utf-8') as bibcodes_file:
        for code in all_bibcodes:
            bibcodes_file.write("%s\n" % code)

#%%

if __name__ == '__main__':
    import doctest
    doctest.testmod()