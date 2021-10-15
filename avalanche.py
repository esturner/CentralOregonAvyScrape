# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 19:54:15 2021

@author: etran
"""
import requests
import numpy as np
from bs4 import BeautifulSoup

#takes table columns
def find_header(soup_table):
    '''returns list of column titles'''
    headers = soup_table.thead.tr.find_all('th')
    header_lbs = []
    for header in headers:
        header_lbs.append(header.string)
    return header_lbs

def page_data(soup_table):
    ''' 
    Returns Dict
    
    extracts the entries to the table on the page_link (intended for central 
    Oregon Avalanche). Returned entries are in a dictionary with the following keys
    ['Ob Date/Time', 'Title', 'Report Type', 'Position', 'Reporter(s)']
    
    '''
#add a list for each header label
    header_lbs = find_header(soup_table)
    
    page_data= {}
    for label in header_lbs:
        page_data[label] = []
    page_data['link'] = []
    
    dat_html = soup_table.tbody
    observations = dat_html.find_all('tr')
    for obs in observations:
        categories = obs.find_all('td')
        for i in range(len(categories)):
            if categories[i].string:
                page_data[header_lbs[i]].append(categories[i].string.strip())
            else:
                if i==0:
                    if categories[i].time:
                        page_data[header_lbs[i]].append(categories[i].time.string)
                    else:
                        page_data[header_lbs[i]].append(categories[i].string.strip())
                link = categories[i].a
                if link:
                    page_data[header_lbs[i]].append(categories[i].a.string)
                    page_data['link'].append(link['href'])
    return header_lbs, page_data

def get_obs_links(observation_link):
    '''returns the list of html extensions'''
            # Make a request
    page = requests.get(observation_link)
    soup = BeautifulSoup(page.content, 'html.parser')
                
    # Takes the table of observations 
    table = soup.table
    
    header, data =page_data(table)
    
    #finds the /ob/#### extension
    links = data['link']
    return links

def read_observation_report(link):
    '''takes a link with /ob/#### extentions'''
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    sections = soup.find_all('b')
    
    #soup.b
    print(sections)
    print(soup.div(class_='col-md-12')[3])
    
    print()
    
    return


def main():
        # Make a request
    page = requests.get(
        "https://www.coavalanche.org/observations")
    soup = BeautifulSoup(page.content, 'html.parser')
                
    # Takes the table of observations 
    table = soup.table
    
    header, data = page_data(table)
    #print(header)
    #print(data[header[0]])
    obs_links = get_obs_links("https://www.coavalanche.org/observations")
    read_observation_report('https://www.coavalanche.org' + obs_links[0])
    return

if __name__== '__main__':
    main()

    #
#print(page_data['Ob Date/Time'])