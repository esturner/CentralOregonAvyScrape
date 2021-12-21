# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 19:54:15 2021

@author: etran
"""
import requests
import numpy as np
from bs4 import BeautifulSoup


class Observation(dict):
    
    def __init__(self, link):
        '''has all the info of a single observation i.e.
        'Observation Date/Time', 'Reporter(s)', 'Location/Elevation', 
        'Report Type', 'Travel Mode', 'Temperature', 'Sky Conditions', 
        'Precip Type/Intensity', 'Height of Snow (HS)', 'Wind Direction/Speed',
        'Written Report', and 'flags'
        '''
        
        self = dict()
        
        sections, data = read_observation_report(link)
        print("Link at:", link)
        #print(f"Section length {len(sections)}. Data Length {len(data)}")
        
        if len(sections) != len(data):
            print("Length Error at", link)
            print("Sections: ", sections)
            print("Data: ", data)
        else:
            for i in range(len(sections)):
                section = sections[i]
                self[section]= data[i]


    
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

def getLinkSoup(link):
    '''takes link returns BeautifulSoup soup type'''
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def getSections(soup):
    title_list = soup.find_all('b')
    sections = []
    for item in title_list:
        sections.append(item.text.strip(':'))       
    return sections


def read_observation_report(link, report_text = True):
    '''takes a link with /ob/#### extentions'''
    soup = getLinkSoup((link))
    sections = getSections(soup)
    
    obervation_dict = {} 
    
    #soup.b
    #print(sections)
    
    #find flags in avy repor
    info_raw = soup.div(class_='col-md-12')[3]
    flags = None
    if len(info_raw.div(class_ = 'red_flags'))>0:
        red_flags = info_raw.div(class_ = 'red_flags')[0].text.strip()
        flags = ''
        flags_list = red_flags.split('\n')
        for n_flag in range(len(flags_list)):
            if n_flag != 0:
                flags += flags_list[n_flag].strip()
    
    #make report details into a string info
    raw_list = info_raw.div(class_= 'col-md-6')
    info = ''
    for section in raw_list:
        info += section.text
    report = ''
    if len(info_raw.div(class_='col-md-12'))>1:
        report = info_raw.div(class_='col-md-12')[1].text
    
    #split info into list each section
    info_list = info.split('\n')
    for i in reversed(range(len(info_list))):
        item = info_list[i]
        item = item.strip()
        info_list[i] = item
        if len(item) ==0:
            info_list.pop(i)
        if item.strip(':') in sections:
            info_list.pop(i)
    
    #location/elevation is split by a \n so we need to combine the two in info_list
    #they occur at index 2 and 3
    for l in info_list[3] :
        if l == '/' :
            info_list[2] += info_list.pop(3)
    
    #add flag

    
    if report_text:
        report = report.strip().strip('Written Report:').strip('\n')
    info_list.append(report)
    
    #add flag
    if flags:
        sections.append('Flags')
        info_list.append(flags)   
        
    return sections, info_list


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
    observations = []
    root = 'https://www.coavalanche.org'
    obs_links = get_obs_links(root + "/observations")
    for link in obs_links:
        observations.append(Observation(root + link))
    
    print(observations[0])
    return

if __name__== '__main__':
    main()

#Note to next: 
#fix data parsing to pick up non-complete reports