#@author: sisazavi

import requests
import json
import pandas as pd

#API Documentation: https://www.eia.gov/opendata/pdf/EIA-APIv2-HandsOn-Webinar-11-Jan-23.pdf
#EIA key: FRIoMFhDgTlYp3MRWAh2seJuCJaEqGg2X5U6tfA1
#https://api.eia.gov/v2/?api_key=FRIoMFhDgTlYp3MRWAh2seJuCJaEqGg2X5U6tfA1

key = 'FRIoMFhDgTlYp3MRWAh2seJuCJaEqGg2X5U6tfA1'
url = """https://api.eia.gov/v2/electricity/retail-sales/data/?\
frequency=monthly&data[0]=price&facets[stateid][]=AK&facets[stateid][]\
=AL&facets[stateid][]=AR&facets[stateid][]=AZ&facets[stateid][]\
=CA&facets[stateid][]=CO&facets[stateid][]=CT&facets[stateid][]\
=DC&facets[stateid][]=DE&facets[stateid][]=ENC&facets[stateid][]\
=ESC&facets[stateid][]=FL&facets[stateid][]=GA&facets[stateid][]\
=HI&facets[stateid][]=IA&facets[stateid][]=ID&facets[stateid][]\
=IL&facets[stateid][]=IN&facets[stateid][]=KS&facets[stateid][]\
=KY&facets[stateid][]=LA&facets[stateid][]=MA&facets[stateid][]\
=MAT&facets[stateid][]=MD&facets[stateid][]=ME&facets[stateid][]\
=MI&facets[stateid][]=MN&facets[stateid][]=MO&facets[stateid][]\
=MS&facets[stateid][]=MT&facets[stateid][]=MTN&facets[stateid][]\
=NC&facets[stateid][]=ND&facets[stateid][]=NE&facets[stateid][]\
=NEW&facets[stateid][]=NH&facets[stateid][]=NJ&facets[stateid][]\
=NM&facets[stateid][]=NV&facets[stateid][]=NY&facets[stateid][]\
=OH&facets[stateid][]=OK&facets[stateid][]=OR&facets[stateid][]\
=PA&facets[stateid][]=PACC&facets[stateid][]=PACN&facets[stateid][]\
=RI&facets[stateid][]=SAT&facets[stateid][]=SC&facets[stateid][]\
=SD&facets[stateid][]=TN&facets[stateid][]=TX&facets[stateid][]\
=US&facets[stateid][]=UT&facets[stateid][]=VA&facets[stateid][]\
=VT&facets[stateid][]=WA&facets[stateid][]=WI&facets[stateid][]\
=WNC&facets[stateid][]=WSC&facets[stateid][]=WV&facets[stateid][]\
=WY&start=2010-01&sort[0][column]=period&sort[0][direction]\
=desc&api_key="""+key


response = requests.get(url, headers={'Content-Type': 'application/json'})
if response.status_code == 200:
    print('\nSuccesfully conected to https://api.eia.gov/\n')
    try:
        data_temp1 = json.loads(response.content.decode('utf-8'))
        data_temp2 = data_temp1['response']['data']
        #should return the following columns: preriod, stateid, stateDescription, sectorid, sectorName, price and price-units
        headers = list(data_temp2[0].keys())
        df_price = pd.DataFrame(columns=headers)
        #insert each new row to the df_price data frame
        for i in range(len(data_temp2)):
            df_price = pd.concat([df_price,pd.DataFrame(data_temp2[i],index=[i])])
    except:
        print('\nNo data found\n')

# print(df_price.head())
# print('')
# print(df_price.describe())
# print('')
# print(df_price['sectorName'].unique())
# print('')
# print(df_price['sectorid'].unique())
# print('')
# print(df_price['stateDescription'].unique())
# print('')
# print(df_price['period'].unique())

# print(df_price.head().to_string)

#get the the prices for the residential sector
df_price_res = df_price[df_price['sectorName'] == 'residential']

states = set(['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', \
              'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', \
              'KS', 'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', \
              'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', \
              'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', \
              'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', \
              'WV', 'WI', 'WY'])
    
df_price_res = df_price_res[df_price_res['stateid'].apply(lambda x: x in states)]
# print(df_price_res)

df_price_res['month'] = pd.to_datetime(df_price_res['period']).dt.month
df_price_pivot = pd.pivot_table(df_price_res, values = 'price', index = 'month', 
                                columns = 'stateid', aggfunc = 'mean') 

# print(df_price_pivot)
#export csv to input_data directory
df_price_pivot.to_csv('input_data/monthly_avg_prices_bystate.csv')
print('\nThe average prices by state and month can be found in input_data/monthly_avg_prices_bystate.csv\n')