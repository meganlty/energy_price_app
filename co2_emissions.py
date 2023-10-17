"""
Created on Oct 2023

@author: sisazavi

Script that retrieves and cleans emission data from: https://www.epa.gov/egrid/summary-data
where the EPA provide by subregion and state-level emission rates and resource mix as well
as grid gross loss value.

The Emissions & Generation Resource Integrated Database (eGRID) 1, released in January 2023 is 
the sixteenth edition of eGRID. eGRID2021 includes two Excel workbooks, one with imperial
units and one with metric units, that contain generator and unit spreadsheets as well as 
spreadsheets by aggregation level for data year 2021.

This short script reorganizes the Excel data and imports it to CSV files in the input_data 
directory for the main program to use it.

"""

import pandas as pd

# State Output Emission Rates (eGRID2021)
#Total output emission rates are in (lb/MWh)
df_emissions_data = pd.read_excel('input_data/eGRID2021_summary_tables.xlsx',sheet_name = 'Table 3', skiprows=3 , usecols='B:I', skipfooter=1)
df_emissions_data.rename(columns={'Unnamed: 1':'State'},inplace=True)
df_emissions_data.to_csv('input_data/co2_emission_rates_data.csv')
print('\nThe average emission rates (lb/MWh) by state can be found in input_data/co2_emission_rates_data.csv\n')


#4. State Resource Mix (eGRID2021)
resourcesEnergyMix = pd.read_excel('input_data/eGRID2021_summary_tables.xlsx',sheet_name = 'Table 4', skiprows=2 , usecols='B:O', skipfooter=2)
resourcesEnergyMix.rename(columns={'Unnamed: 1':'State','Unnamed: 2':'Nameplate Capacity','Unnamed: 3':'Net Generation'},inplace=True)
resourcesEnergyMix.to_csv('input_data/resourcesEnergyMix.csv')
