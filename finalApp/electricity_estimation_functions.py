#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 21:22:27 2023

Contains calculation functions for electricity cost and emission estimations. 

"""
import pandas as pd
import numpy as np
import plotly.express as px

#df_resource_mix = pd.read_csv('input_data/resourcesEnergyMix.csv', index_col=1)

# month_mapping = {1: 'January',2: 'February', 3: 'March',4: 'April',
#                 5: 'May',6: 'June',7: 'July',8: 'August',
#                 9: 'September',10: 'October',11: 'November',12: 'December'}

# def get_e_total_price(state,homeType,df_price,df_load,month_mapping):
#     hh_type = get_hh_abb(homeType)
#     dict_states = get_mappings()
#     climate_zone = dict_states[state][0]
#     climate_zone_hometype = climate_zone + hh_type
#     total_cost_ = round(df_price[state]*df_load[climate_zone_hometype]/100,2)
#     df_total_cost = pd.DataFrame(total_cost_,columns=['Elec Costs'])
#     df_total_cost = df_total_cost.rename(index=month_mapping)
#     df_total_cost.to_csv('output_data/monthlyElecCost_'+state+'.csv')
#     return(df_total_cost)


# def get_e_total_emissions(state,homeType,df_emission,df_load,month_mapping):
#     hh_type = get_hh_abb(homeType)
#     dict_states = get_mappings()
#     climate_zone = dict_states[state][0]
#     climate_zone_hometype = climate_zone + hh_type
#     total_emissions_ = round(df_emission.loc[state]['CO2e']*0.001*0.0005*df_load[climate_zone_hometype],2)
#     total_emissions_.name = None
#     df_total_emissions = pd.DataFrame(total_emissions_,columns=['Emission'])
#     df_total_emissions = df_total_emissions.rename(index=month_mapping)
#     df_total_emissions.to_csv('output_data/monthlyCO2.csv')
#     return(df_total_emissions)

def uses_mix(state, df_resource):
    """
    Writes CSV file containing resource mix for user-defined state input. 
    

    Parameters
    ----------
    state : string
    df_resource : a dataframe containing all the states and their 
    corresponding resource mixes. 

    Returns
    -------
    None.

    """
    resources_list = ['Coal', 'Oil','Gas', 'Other Fossil', 'Nuclear', 'Hydro', 
                      'Biomass', 'Wind', 'Solar','Geo- thermal', 'Other unknown/ purchased fuel']
    
    type_res_dict = {'Coal':'Fossil', 'Oil':'Fossil','Gas':'Fossil', 'Other Fossil':'Fossil', 'Nuclear':'Renewable', 'Hydro':'Renewable', 
                      'Biomass':'Renewable', 'Wind':'Renewable', 'Solar':'Renewable','Geo- thermal':'Renewable', 'Other unknown/ purchased fuel':'Unknown'}


    df_resource_mix = pd.DataFrame(df_resource.loc[state][resources_list])
    df_resource_mix.rename(columns={state:'Proportion'},inplace=True)
    df_resource_mix['Resource'] = df_resource_mix.index
    df_resource_mix['Type'] = df_resource_mix['Resource'].apply(lambda x: type_res_dict[x])
    df_resource_mix.reset_index(inplace=True)
    df_resource_mix.to_csv('output_data/resourcesMIX_'+state+'.csv')
    return

def get_statelist():
    """
    Returns list of states (no duplicates). Used for
    drop-down selection of state in Streamlit app. 
    
    Returns
    -------
    states : List 
    """
    states = pd.read_excel('input_data/state_climate_zone.xlsx')["state"]
    states = list(set(states.tolist()))
    return states

def get_mappings():
    """
    Return dictionary with states as keys and list of climate zone(s) as values. 
    Used to map state to corresponding climate zone load data so further
    calculations can be performed. 

    Returns
    -------
    dict_states : Dictionary

    """
    cz_abbrev = {'Cold': 'c',
                 'Very Cold': 'vc',
                 'Very-Cold': 'vc',
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
    """
    Maps user input (from Streamlit) to abbreviation used to identify
    correct load files. 

    Parameters
    ----------
    hh_input : String

    Returns
    -------
    hh_abbrev : String

    """
    dict_hh_abbrev = {'House (Detached)':'sd', 
                 'House (Attached) e.g.: townhouse, rowhouse, duplex)' : 'sa', 
                 'Apartment (2-4 units)': 'm24',
                 'Apartment (5+ units) ': 'm5'}
    hh_abbrev = dict_hh_abbrev[hh_input]
    return hh_abbrev

def get_use_level(use_input):
    """
    Maps user input (from Streamlit) to scaling factor used to modify
    load files. 

    Parameters
    ----------
    use_input : String
    
    Returns
    -------
    user_level : Float

    """
    dict_use = {"Rarely" : 1.2, 
                "Sometimes": 1, 
                "Always": 0.8}
    user_level = dict_use[use_input]
    return user_level 

def get_load(state, carModel, monthlyMileage, house):
    """
    Returns load profile based on user-inputted information on state, 
    car brand, mileage, and house type. 

    Parameters
    ----------
    state : string
    carModel : string
    monthlyMileage : integer
    house : string

    Returns
    -------
    df_avg_cz : DataFrame
    df_ev_load : DataFrame

    """
    # Get dictionary of states and corresponding climate zones
    dict_states = get_mappings()
    
    # Generate list of relevant columns to pull from load data. 
    hh_type = get_hh_abb(house)
    cz_list = dict_states[state]
    cz_list_hhtype = [i + hh_type for i in cz_list]
    
    # Get relevant load data
    df_load = pd.read_csv('input_data/averages_per_climate_zone.csv', index_col=0)
    df_cz = []
    for i in cz_list_hhtype:
        df_cz.append(df_load[i])
    
    df_all_cz = pd.concat(df_cz, axis = 1)
    df_avg_cz = df_all_cz.mean(axis=1)
    
    #Get EV consumption for every month
    df_ev = pd.read_csv('input_data/energy_consumption_by_ev.csv', index_col=0)
    if carModel == None:
        ev=0
    else:
        ev = (df_ev.loc[carModel].values[0]*0.001)*monthlyMileage #to get in kW
        
    df_ev_load = pd.DataFrame({'ev_load':[ev for i in range(12)]}) # assumes that monthly mileage is constant
    df_ev_load.index =range(1, len(df_ev_load)+1) #resets index
    
    return df_avg_cz, df_ev_load
    
def get_final(state, carModel, monthlyMileage, house, cons_level):
    """
    Writes final data on estimated electricity costs and emissions data to output folder, to be
    pulled by Streamlit and displayed on web app. 

    Parameters
    ----------
    state : string
    carModel : string
    monthlyMileage : integer
    house : string
    cons_level : string

    Returns
    -------
    None.

    """
    # Get basic information
    level=get_use_level(cons_level)
    
    # Price Information 
    df_price = pd.read_csv('input_data/monthly_avg_prices_bystate.csv', index_col=0)    
    prices = df_price.loc[:,state]*0.01*level #for cents to dollars
    
    # Emission Information 
    df_emission = pd.read_csv('input_data/co2_emission_rates_data.csv', index_col=1)
    emissions = df_emission.loc[state, 'CO2']*0.001*level #MWh to kWh
    df_monthly_em = pd.DataFrame({'co2_in':[emissions for i in range(12)]})
    df_monthly_em.index =range(1, len(df_monthly_em)+1)

    # Get load
    df_avg_cz, df_ev_load = get_load(state, carModel, monthlyMileage, house)

    # Combine info
    df_all = pd.concat([prices, df_avg_cz, df_ev_load, df_monthly_em], axis =1)
    df_all.columns = ['prices', 'load', 'ev_load', 'co2_in']

    df_all['Elec Costs'] = df_all['prices'] * (df_all['load']+df_all['ev_load'])
    df_all['Emission'] = df_all['co2_in'] * (df_all['load']+df_all['ev_load'])*0.0005 # lb to ton

    months = ['January', 'February', 'March', 'April', 'May', 
              'June', 'July', 'August', 'September', 'October', 
              'November', 'December']

    # Writes to output dataframes that Streamlit app will use to display
    df_final_price = df_all['Elec Costs']
    df_final_price.index = months
    df_final_price.to_csv('output_data/monthlyElecCost_'+state+'.csv') 

    df_final_em = df_all['Emission']
    df_final_em.index = months
    df_final_em.to_csv('output_data/monthlyCO2_'+state+'.csv')
    
    return 

