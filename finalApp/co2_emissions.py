#@author: sisazavi

#https://www.epa.gov/egrid/summary-data

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

