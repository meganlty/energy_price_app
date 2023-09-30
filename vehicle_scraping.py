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

# Okay we got 364 models. No way there's this many or that someone actually cares. 
# A lot of duplicate models with year
# and some of these EVs aren't sold in America 
# Let's average duplicate models (let's just assume that in recent year
# it has not changed much) and remove anything that isn't available in America 
# and honestly most people don't choose this many models. Let's get the brand from all of them. 

pat = r'([^\s]+)'
ev_con_df['brand'] =  ev_con_df['model'].str.extract(pat)

#only take if its within top 10. 
top10_brands = set(['Tesla', 'Ford', 'Chevrolet', 'Volkswagen',\
                'Nissan', 'Audi', 'Porsche', 'Hyundai'])

ev_con_df_sim = ev_con_df[ev_con_df['brand'].isin(top10_brands)].reset_index(drop=True)
ev_con_summary = pd.pivot_table(ev_con_df_sim, values = 'wh/km', index = 'brand', aggfunc = "mean")
