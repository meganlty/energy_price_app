#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 21:22:27 2023

"""
import pandas as pd

#inputs #will be passed into by streamlit code
#these are temporary inputs 
state = 'TX'
carModel = 'Tesla'
monthlyMileage = 10 # in km
house = 'Apartment (5+ units)  '

df_price = pd.read_csv('input_data/monthly_avg_prices_bystate.csv', index_col=0)
df_load = pd.read_csv('input_data/averages_per_climate_zone.csv', index_col=0)
df_ev = pd.read_csv('input_data/energy_consumption_by_ev.csv', index_col=0)
df_emission = pd.read_csv('input_data/co2_emission_rates_data.csv', index_col=1)

def get_statelist():
    states = pd.read_excel('input_data/state_climate_zone.xlsx')["state"]
    return states

def get_mappings():
    cz_abbrev = {'Cold': 'c',
                 'Very Cold': 'vc',
                 'Hot-Dry' : 'hd',
                 'Hot-Humid' :'hh', 
                 'Marine' : 'm', 
                 'Mixed-Dry': 'md',
                 'Mixed-Humid': 'mh'}
    
    states = pd.read_excel('input_data/state_climate_zone.xlsx')
    states_ab = states.replace({'climate_zone':cz_abbrev})
    states_grouped = states_ab.groupby('state').agg({'climate_zone':list})
    
    dict_states = states_grouped.to_dict()
    dict_states = dict_states['climate_zone']
    return dict_states

def get_hh_abb(hh_input):
    dict_hh_abbrev = {'House (Detached)':'sd', 
                 'House (Attached) e.g.: townhouse, rowhouse, duplex)' : 'sa', 
                 'Apartment (2-4 units)': 'm24',
                 'Apartment (5+ units)  ': 'm5'}
    hh_abbrev = dict_hh_abbrev[hh_input]
    return hh_abbrev

def get_use_type(use_input):
    dict_use = {"Rarely" : 'h', 
                "Sometimes": 'm', 
                "Always": 'l'}
    use_abbrev = dict_use[use_input]
    return use_abbrev 

def get_load(state, carModel, monthlyMileage, house):
    dict_states = get_mappings()
    
    # Get list of columns 
    hh_type = get_hh_abb(house)
    cz_list = dict_states[state]
    cz_list_hhtype = [i + hh_type for i in cz_list]
    
    # Get relevant load data
    df_cz = []
    for i in cz_list_hhtype:
        df_cz.append(df_load[i])
    
    df_all_cz = pd.concat(df_cz, axis = 1)
    df_avg_cz = df_all_cz.mean(axis=1)
    
    #Get EV consumption for every month
    if carModel == None:
        ev=0
    else:
        ev = (df_ev.loc[carModel].values[0]*0.001)*monthlyMileage #to get in kW
    df_ev_load = pd.DataFrame({'ev_load':[ev for i in range(12)]})
    df_ev_load.index =range(1, len(df_ev_load)+1)
    return df_avg_cz, df_ev_load
    
def get_final(state, carModel, monthlyMileage, house):
    # Get basic information
    prices = df_price.loc[:,state]*0.01 #for cents to dollars
    emissions = df_emission.loc[state, 'CO2']*1000 #MWh to kWh
    df_monthly_em = pd.DataFrame({'co2_in':[emissions for i in range(12)]})
    df_monthly_em.index =range(1, len(df_monthly_em)+1)
    
    # Get load
    df_avg_cz, df_ev_load = get_load(state, carModel, monthlyMileage, house)

    # Combine info
    df_all = pd.concat([prices, df_avg_cz, df_ev_load, df_monthly_em], axis =1)
    df_all.columns = ['prices', 'load', 'ev_load', 'co2_in']

    df_all['Elec Costs'] = df_all['prices'] * (df_all['load']+df_all['ev_load'])
    df_all['Emission'] = df_all['co2_in'] * (df_all['load']+df_all['ev_load'])

    months = ['January', 'February', 'March', 'April', 'May', 
              'June', 'July', 'August', 'September', 'October', 
              'November', 'December']

    df_final_price = df_all['Elec Costs']
    df_final_price.index = months
    df_final_price.to_csv('output_data/monthlyElecCost.csv') 

    df_final_em = df_all['Emission']
    df_final_em.index = months
    df_final_em.to_csv('output_data/monthlyCO2.csv')
    return 

