#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 23:36:20 2023

@author: meganty

This script scrapes EV charging requirements and corresponding models from EV database, 
and summarizes them in the top 8 most common brands and their charging requirements. 

"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

httpString ='https://ev-database.org/cheatsheet/energy-consumption-electric-car'
page = requests.get(httpString)

if page.status_code == 200:
    print('\nSuccesfully connected to EV database website')
    
    soup = BeautifulSoup(page.content, 'html.parser')
    core = soup.find(class_="core-content")
    
    # Get energy consumption rates in order (wh/km)
    battery_data_list = core.find_all("span")
    battery_data = []
    for i in battery_data_list[1:]: 
        battery_data.append(int(i.get_text()))
    
    # Get model names in order
    car_data_list = core.find_all("a", href=True)
    model_data = []
    for i in car_data_list[:-1]:
        model_data.append(i.get_text())
    
    # Check that we got the same number of tags - make sure that every model has a corresponding rate
    print(len(battery_data) == len(model_data))
    
    # Create DataFrame using data from webpage
    ev_con_df = pd.DataFrame({'model': model_data, 'wh/km': battery_data})
    print(ev_con_df.head())
    
    # Get brand 
    pat = r'([^\s]+)'
    ev_con_df['brand'] =  ev_con_df['model'].str.extract(pat)
    
    # Only take if its within top 8 popular brands - from https://www.kbb.com/best-cars/most-popular-electric-cars/
    top8_brands = set(['Tesla', 'Ford', 'Chevrolet', 'Volkswagen',\
                    'Nissan', 'Audi', 'Porsche', 'Hyundai'])
    
    # Assume that models from same brand have similar charging requirements - take average. 
    # It shouldn't matter too much because they're all relatively close to each other anyway. 
    ev_con_df_sim = ev_con_df[ev_con_df['brand'].isin(top8_brands)].reset_index(drop=True) 
    ev_con_summary = pd.pivot_table(ev_con_df_sim, values = 'wh/km', index = 'brand', aggfunc = "mean") 
    ev_con_summary.loc['No EV'] = 0
    ev_con_summary.to_csv('input_data/energy_consumption_by_ev.csv')