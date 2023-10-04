#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 23:36:20 2023

@author: meganty
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

httpString ='https://ev-database.org/cheatsheet/energy-consumption-electric-car'
print(httpString)
page = requests.get(httpString)
print(page.status_code)

soup = BeautifulSoup(page.content, 'html.parser')
core = soup.find(class_="core-content")

battery_data_list = core.find_all("span")
battery_data = []
for i in battery_data_list[1:]: #we start from 1 because of HTML
    battery_data.append(int(i.get_text()))

car_data_list = core.find_all("a", href=True)
model_data = []
for i in car_data_list[:-1]:
    model_data.append(i.get_text())

# Check that we got the same number of tags
print(len(battery_data) == len(model_data))

# Create DataFrame
ev_con_df = pd.DataFrame({'model': model_data, 'wh/km': battery_data})
print(ev_con_df.head())

# Get top ten most popular brands 
pat = r'([^\s]+)'
ev_con_df['brand'] =  ev_con_df['model'].str.extract(pat)

#only take if its within top 10. 
top10_brands = set(['Tesla', 'Ford', 'Chevrolet', 'Volkswagen',\
                'Nissan', 'Audi', 'Porsche', 'Hyundai'])

ev_con_df_sim = ev_con_df[ev_con_df['brand'].isin(top10_brands)].reset_index(drop=True)
ev_con_summary = pd.pivot_table(ev_con_df_sim, values = 'wh/km', index = 'brand', aggfunc = "mean")
ev_con_summary.to_csv('energy_consumption_by_ev.csv')