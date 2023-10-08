#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 15:20:10 2023

@author: meganty
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

# We're going to generalize by climate zones because air conditioning/heating
# is the most share of electricity use. This also means that we only have to 
# clean 7 sets of tables, instead of 50 sets, and assign states to each of the climates. 


# Each file includes the summed energy consumption for all buildings of the
# specified type in the geography of interest by 15-minute timestep.

# There is also a column
# named `units_represented` (for residential) or `floor_area_represented` (for commercial)  which indicates the
# total number of dwelling units (for resedential) or floor area (for commercial) the aggregate represents.

httpString ='https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=nrel-pds-building-stock%2Fend-use-load-profiles-for-us-building-stock%2F2021%2Fresstock_tmy3_release_1%2Ftimeseries_aggregates%2Fby_building_america_climate_zone%2F'
print(httpString)
page = requests.get(httpString)

soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find(id="tbody-s3objects")

file_path ='https://oedi-data-lake.s3.amazonaws.com/nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock/2021/resstock_tmy3_release_1/timeseries_aggregates/by_building_america_climate_zone/'
files = table.find_all("a", href=True)
csv_list = []
for i in files:
    csv_list.append(i.text)
    
# We do not need mobile homes
csv_list_2 = [x for x in csv_list if 'mobile' not in x]

#Download and clean files
column_names = ['cm24', 'cm5', 'csa', 'csd',\
                'hdm24', 'hdm5', 'hdsa', 'hdsd',\
                'hhm24', 'hhm5', 'hhsa', 'hhsd',\
                'mm24', 'mm5', 'msa', 'msd',\
                'mdm24', 'mdm5', 'mdsa', 'mdsd',\
                'mhm24', 'mhm5', 'mhsa', 'mhsd',\
                'vcm24', 'vcm5', 'vcsa', 'vcsd']
all_monthly_sums = []

for i in range(len(csv_list_2)): 
    data = pd.read_csv(file_path + csv_list_2[i])
    temp = data[['timestamp', 'units_represented', 'out.electricity.total.energy_consumption']]
    temp2 = temp.copy()
    temp2['kwhperunit'] = temp2['out.electricity.total.energy_consumption']/temp2['units_represented'] #necessary because dataset is aggregated 
    temp2['timestamp'] = pd.to_datetime(temp2['timestamp'])
    temp2['month'] = pd.to_datetime(temp2['timestamp']).dt.month
    monthly_sums = pd.pivot_table(temp2, values = 'kwhperunit', index = 'month', aggfunc = "sum")
    all_monthly_sums.append(monthly_sums)

# Write files to final 
final = pd.concat(all_monthly_sums, axis = 1)
final.columns = column_names
print(final)
final.to_csv('input_data/averages_per_climate_zone.csv')
