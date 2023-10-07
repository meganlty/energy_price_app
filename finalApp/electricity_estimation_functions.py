# functions or classes responsible for estimating the different values we want to show
import pandas as pd

df_e_unit_price = pd.read_csv('input_data/monthly_avg_prices_bystate.csv')
df_emission_rates = pd.read_csv('input_data/co2_emission_rates_data.csv')

zip_code = 12345 #input parameter form the dashboard
state = 'PA' #obtained as an input or after joining tables to get the state?
total_consumption = 123 #average from climate zone


def electricity_total_price(zip_code,state,df_e_unit_price,total_consumption):
    return(total_price)

def electricity_total_emissions(zip_code,state,df_emission_rates,total_consumption):
    return(total_emissions)

# def electricity_resource_mix():
#     return()

def car_electricity():
    return()

def state_comparision():
    return()

# def uses_mix():
#     return()
