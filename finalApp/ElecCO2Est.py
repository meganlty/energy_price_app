import streamlit as st
import pandas as pd
# import numpy as np
# from streamlit_folium import st_folium
# import folium
import electricity_estimation_functions as root_fct
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import electricity_prices as ep

# streamlit run ElecCO2Est.py  http://localhost:8501/
custom_css = """
<style>
    p {
        font-size: 16px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

header='<h2 style="font-size:40px;"><span style="color:Chocolate;">Electricity Cost</span>/ <span style="color:MediumSeaGreen;">CO2 Emission</span> Estimator</h2>'
st.markdown(header, unsafe_allow_html=True)


hasCar="No"
def carModelDropDown():
    if hasCar=="Yes":
        return False
    else:
        return True


with st.container():
    #Update Data
    updateData=st.radio("Would yo like to update the data?",key="update",options=["No","Yes"],)

# Add a button to update data from webscraping and API
if st.button("Update"):

    # Run modules
    if updateData=="Yes":
        try:
            ep.get_eia_prices()
        except:
            st.write("❌ No data found from https://api.eia.gov/")
            exit()
        st.write("Succesfully conected to https://api.eia.gov/")


st.markdown("""---""")
with st.container():

    #Select State
    st.markdown('<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Please Select Your State</h3>', unsafe_allow_html=True)
    statelist=root_fct.get_statelist()
    state_dropdown=st.selectbox(" ",statelist,key="state")
        
    tab1, tab2, tab3, tab4 = st.tabs(["Electric Car", "Home Type", "Energy Consciousness", "Compare"])

    #Select Electric Car
    with tab1:
        carQuestion='<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you have an electric vehicle?</h3>'
        st.markdown(carQuestion, unsafe_allow_html=True)
        hasCar=st.radio("🚘",key="car",options=["No","Yes"],on_change=carModelDropDown,)
        with st.expander("If YES",expanded=not carModelDropDown()):
            carModel_dropdown = st.selectbox("What's the model",("Audi","Ford","Hyundai","Nissan","Porsche","Tesla","Volkswagen"),key="carmodel",disabled=carModelDropDown(),index=None)
            monthlyMileage_input = st.text_input("Estimated Monthly Mileage in km",value="0",disabled=carModelDropDown())

    #Select Home Type              
    with tab2:
        homeTypeQuestion='<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Select your home type</h4>'
        st.markdown(homeTypeQuestion, unsafe_allow_html=True)
        homeType_dropdown = st.selectbox("🏠",('House (Detached)', 'House (Attached) e.g.: townhouse, rowhouse, duplex)', 'Apartment (2-4 units)','Apartment (5+ units) '),key="hometype")
    
    #Select Energy Consciousness Level
    with tab3:
        energySaverQuestion='<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you intend to save energy?</h4>'
        st.markdown(energySaverQuestion, unsafe_allow_html=True)
        energySaver_select=st.radio(
            "e.g. I always turn lights off when leave",
            key="energySaver",
            options=["Rarely", "Sometimes", "Always"],
            index=1
        )

    #Select state to compare
    with tab4:
        compareStateQuestion='<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">With which state would you like to compare?</h4>'
        st.markdown(compareStateQuestion, unsafe_allow_html=True)
        state_dropdown_2=st.selectbox(" ",statelist,key="state2")

st.markdown("""---""")
# Add a button to collect input values
if st.button("Calculate"):

    # Run function to calculate 
    #state 1
    root_fct.get_final(state_dropdown,carModel_dropdown,int(monthlyMileage_input),homeType_dropdown,energySaver_select)
    #state 2
    root_fct.get_final(state_dropdown_2,carModel_dropdown,int(monthlyMileage_input),homeType_dropdown,energySaver_select)


    userProfileHeader='<h3 style="font-size:20px;">👾 Entered Information</h3>'
    st.markdown(userProfileHeader, unsafe_allow_html=True)
    if hasCar=="Yes":
        try:
            int(monthlyMileage_input)
        except ValueError:
            st.write("❌ Please enter correct monthlyMileage")
            exit()
        st.write("🚘 Car: " + carModel_dropdown)
        st.write("🚘 Monthly Mileage: " + monthlyMileage_input)
    else:
        st.write("🚶🏻‍♀️ Don't have a car")
    st.write("🏠 Home type: " + homeType_dropdown)
    st.write("💚 I "+energySaver_select+" care about saving energy")
  
    #expense chart
    # Load the data from CSV
    month_mapping = {1: 'January',2: 'February', 3: 'March',4: 'April',
    5: 'May',6: 'June',7: 'July',8: 'August',
    9: 'September',10: 'October',11: 'November',12: 'December'}
    
    chart_data = pd.read_csv("output_data/monthlyElecCost_"+state_dropdown+".csv")
    chart_data.rename(columns={'Unnamed: 0':'Month'},inplace=True)
    chart_data['State']=state_dropdown
    chart_data2 = pd.read_csv("output_data/monthlyElecCost_"+state_dropdown_2+".csv")
    chart_data2.rename(columns={'Unnamed: 0':'Month'},inplace=True)
    chart_data2['State']=state_dropdown_2

    chart_1_2 = pd.concat([chart_data,chart_data2],axis=0)

    # Calculate the total elec costs
    total_cost = chart_data['Elec Costs'].sum()
    total_cost2 = chart_data2['Elec Costs'].sum()

    st.write("💰💰💰 Your total electric in {} costs would be ${}".format(state_dropdown, str(round(float(total_cost)))))
    if total_cost > total_cost2:
        st.write("💰💰💰 {}% greater than the costs in {}, where the costs are ${}"
                 .format(str(round(float(1-total_cost2/total_cost)*100))
                         , state_dropdown_2
                         , str(round(float(total_cost2)))))
    else:
        st.write("💰💰💰 {}% less than the costs in {}, where the costs are ${}"
                 .format(str(round(float(1-total_cost2/total_cost)*100))
                         , state_dropdown_2
                         , str(round(float(total_cost2)))))

    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a bar chart using Plotly with custom sorting
    fig = px.bar(
        chart_1_2,
        x='Month',
        y='Elec Costs',
        color='State',
        barmode='group',
        pattern_shape = 'State',
        title = state_dropdown + ' Electric Costs by Month',
        text='Elec Costs',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Electric Costs',
        showlegend=True,  # Hide legend
        title= state_dropdown + " Vs. " + state_dropdown_2 + " Electricity Costs EST by Month"
    )
    fig.update_yaxes(range=[0, chart_1_2['Elec Costs'].max()*1.1])

    # Add data labels above each bar
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Change the bar colors
    custom_colors = {
    'January': 'Salmon',
    'February': 'DarkSeaGreen',
    'March': 'RoyalBlue',
    'April': 'Orange',
    'May': 'Purple',
    'June': 'Gold',
    'July': 'Pink',
    'August': 'Cyan',
    'September': 'LimeGreen',
    'October': 'SkyBlue',
    'November': 'Red',
    'December': 'Teal'
}
    fig.update_traces(marker_color=[custom_colors[month] for month in chart_1_2['Month']])

    # Show the chart using Streamlit
    st.plotly_chart(fig)


#emission chart
    # Load the data from CSV
    chart_data = pd.read_csv("output_data/monthlyCO2_"+state_dropdown+".csv")
    chart_data.rename(columns={'Unnamed: 0':'Month'},inplace=True)
    chart_data['State']=state_dropdown
    chart_data2 = pd.read_csv("output_data/monthlyCO2_"+state_dropdown_2+".csv")
    chart_data2.rename(columns={'Unnamed: 0':'Month'},inplace=True)
    chart_data2['State']=state_dropdown_2

    chart_1_2 = pd.concat([chart_data,chart_data2],axis=0)

    # Calculate the total CO2 emissions
    total_ems = chart_data['Emission'].sum()
    total_ems2 = chart_data2['Emission'].sum()
    st.write("🍃🍃🍃 Total CO2 Emission would be " + str(round(float(total_ems),2)) + " tons")

    if total_ems > total_ems2:
        st.write("🍃🍃🍃 {}% greater than the emissions in {}, where the emissions are {} tons"
                 .format(str(round(float(1-total_ems2/total_ems)*100,2))
                         , state_dropdown_2
                         , str(round(float(total_ems2),2))))
    else:
        st.write("🍃🍃🍃 {}% less than the emissions in {}, where the emissions are {} tons"
                 .format(str(round(float(1-total_ems2/total_ems)*100,2))
                         , state_dropdown_2
                         , str(round(float(total_ems2),2))))
        
    # Calculate the average CO2 emissions
    average_ems = chart_data['Emission'].mean()

    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a bar chart using Plotly with custom sorting and conditional coloring
    fig = px.bar(
        chart_1_2,
        x='Month',
        y='Emission',
        color='State',
        barmode='group',
        pattern_shape = 'State',
        text='Emission',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='CO2 Emissions in tons',
        showlegend=True,  # Hide legend
        title= state_dropdown + " Vs. " + state_dropdown_2 + ' CO2 Emissions by Month'
    )
    fig.update_yaxes(range=[0, chart_1_2['Emission'].max()*1.1])

    # Define colors for above-average and below-average emissions
    above_avg_color = 'Salmon'
    below_avg_color = 'DarkSeaGreen'

    # Assign colors based on whether emissions are above or below average
    fig['data'][0]['marker']['color'] = [
        above_avg_color if em > average_ems else below_avg_color
        for em in chart_1_2['Emission']
    ]
    fig['data'][1]['marker']['color'] = [
        above_avg_color if em > average_ems else below_avg_color
        for em in chart_1_2['Emission']
    ]

    # Add data labels above each bar
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Show the chart using Streamlit
    st.plotly_chart(fig)
        
    # m = folium.Map(location=[39.949610, -75.150282], zoom_start=12,tiles='CartoDB positron')
    #st_map=st_folium(m,width=750,height=400)

#resources mix chart
    # Load the data from CSV
    df_resource = pd.read_csv('input_data/resourcesEnergyMix.csv', index_col=1)
    root_fct.uses_mix(state_dropdown,df_resource)
    pie_data = pd.read_csv("output_data/resourcesMIX_"+state_dropdown+".csv")
    root_fct.uses_mix(state_dropdown_2,df_resource)
    pie_data2 = pd.read_csv("output_data/resourcesMIX_"+state_dropdown_2+".csv")

    renewbableShare = pie_data[pie_data['Type']=='Renewable']['Proportion'].sum()
    renewbableShare2 = pie_data2[pie_data2['Type']=='Renewable']['Proportion'].sum()
    fossilShare = pie_data[pie_data['Type']=='Fossil']['Proportion'].sum()
    fossilShare2 = pie_data2[pie_data2['Type']=='Fossil']['Proportion'].sum()

    st.write("⚡⚡⚡ Renewable resources are the {}% of the total in {}".format(round(renewbableShare*100,2),state_dropdown))

    if renewbableShare > renewbableShare2:
        st.write("⚡⚡⚡ {}% greener than the resources in {}, where the renewable resources are {}%"
                 .format(str(round(float(1-renewbableShare2/renewbableShare)*100,2))
                         , state_dropdown_2
                         , str(round(float(renewbableShare2*100),2))))
    else:
        st.write("⚡⚡⚡ {}% less greener than the emissions in {}, where the renewable resources are {}%"
                 .format(str(round(float(1-renewbableShare2/renewbableShare)*100,2))
                         , state_dropdown_2
                         , str(round(float(renewbableShare2*100),2))))

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
    fig.add_trace(go.Pie(labels = pie_data['Resource'] , values=pie_data['Proportion'], name = state_dropdown + " CO2e"),1, 1)
    fig.add_trace(go.Pie(labels = pie_data2['Resource'] , values=pie_data2['Proportion'], name = state_dropdown_2 + " CO2e"),1, 2)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
    title_text = state_dropdown + " Vs. " + state_dropdown_2 + " Energy resource Mix",
    # Add annotations in the center of the donut pies.
    annotations=[dict(text = state_dropdown, x=0.18, y=0.5, font_size=20, showarrow=False),
                 dict(text = state_dropdown_2, x=0.82, y=0.5, font_size=20, showarrow=False)])
    
    # Show the chart using Streamlit
    st.plotly_chart(fig)
