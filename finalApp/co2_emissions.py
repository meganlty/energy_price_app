#@author: sisazavi

#https://www.epa.gov/egrid/summary-data

import pandas as pd

# State Output Emission Rates (eGRID2021)
#Total output emission rates are in (lb/MWh)
emissions_data = pd.read_excel('eGRID2021_summary_tables.xlsx',sheet_name = 'Table 3', skiprows=3 , usecols='B:I', skipfooter=1)
emissions_data.rename(columns={'Unnamed: 1':'State'},inplace=True)


#4. State Resource Mix (eGRID2021)
resourcesEnergyMix = pd.read_excel('eGRID2021_summary_tables.xlsx',sheet_name = 'Table 4', skiprows=2 , usecols='B:O', skipfooter=2)
resourcesEnergyMix.rename(columns={'Unnamed: 1':'State','Unnamed: 2':'Nameplate Capacity','Unnamed: 3':'Net Generation'},inplace=True)

