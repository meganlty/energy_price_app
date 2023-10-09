import streamlit as st
import pandas as pd
# import numpy as np
# from streamlit_folium import st_folium
# import folium
import electricity_estimation_functions as root_fct
import plotly.express as px

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
    
    #Select State
    st.markdown('<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Please Select Your State</h3>', unsafe_allow_html=True)
    statelist=root_fct.get_statelist()
    state_dropdown=st.selectbox(" ",statelist,key="state")
        
    tab1, tab2, tab3 = st.tabs(["Electric Car", "Home Type", "Energy Consciousness"])

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
       
st.markdown("""---""")
# Add a button to collect input values
if st.button("Calculate"):

    # Run function to calculate 
    root_fct.get_final(state_dropdown,carModel_dropdown,int(monthlyMileage_input),homeType_dropdown,energySaver_select)

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
    chart_data = pd.read_csv("output_data/monthlyElecCost.csv")

    # Calculate the total elec costs
    total_cost = chart_data['Elec Costs'].sum()
    st.write("Your total electric costs would be $"+str(round(float(total_cost))))

    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a bar chart using Plotly with custom sorting
    fig = px.bar(
        chart_data,
        x='Unnamed: 0',
        y='Elec Costs',
        title='Electric Costs by Month',
        text='Elec Costs',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Electric Costs',
        showlegend=False,  # Hide legend
        title="Electricity Costs EST by Month"
    )
    fig.update_yaxes(range=[0, chart_data['Elec Costs'].max()*1.1])

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
    fig.update_traces(marker_color=[custom_colors[month] for month in chart_data['Unnamed: 0']])

    # Show the chart using Streamlit
    st.plotly_chart(fig)


#emission chart
    # Load the data from CSV
    chart_data = pd.read_csv("output_data/monthlyCO2.csv")

    # Calculate the total CO2 emissions
    total_ems = chart_data['Emission'].sum()
    st.write("Total CO2 Emission would be " + str(round(float(total_ems))) + " tons")

    # Calculate the average CO2 emissions
    average_ems = chart_data['Emission'].mean()

    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a bar chart using Plotly with custom sorting and conditional coloring
    fig = px.bar(
        chart_data,
        x='Unnamed: 0',
        y='Emission',
        text='Emission',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='CO2 Emissions in tons',
        showlegend=False,  # Hide legend
        title='CO2 Emissions by Month'
    )
    fig.update_yaxes(range=[0, chart_data['Emission'].max()*1.1])

    # Define colors for above-average and below-average emissions
    above_avg_color = 'Salmon'
    below_avg_color = 'DarkSeaGreen'

    # Assign colors based on whether emissions are above or below average
    fig['data'][0]['marker']['color'] = [
        above_avg_color if em > average_ems else below_avg_color
        for em in chart_data['Emission']
    ]

    # Add data labels above each bar
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Show the chart using Streamlit
    st.plotly_chart(fig)
        
    # m = folium.Map(location=[39.949610, -75.150282], zoom_start=12,tiles='CartoDB positron')
    #st_map=st_folium(m,width=750,height=400)
