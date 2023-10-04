import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import folium
import altair as alt


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


def carModelDropDown():
    if hasCar=="Yes":
        return False
    else:
        return True
        


with st.container():
    
    #Enter zipcode
    st.markdown('<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Please Enter Zipcode</h3>', unsafe_allow_html=True)
    zipcode = st.text_input(label="📍",value="15289",max_chars=5)
    
        
    tab1, tab2, tab3 = st.tabs(["Electric Car", "Home Type", "Other"])
    with tab1:
        carQuestion='<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you have an electric vehicle?</h3>'
        st.markdown(carQuestion, unsafe_allow_html=True)
        hasCar=st.radio("🚘",key="car",options=["No","Yes"],on_change=carModelDropDown,)
        with st.expander("If YES",expanded=not carModelDropDown()):
            carModel = st.selectbox("What's the model",("Audi","Ford","Hyundai","Nissan","Porsche","Tesla","Volkswagen"),key="carmodel",disabled=carModelDropDown())
            monthlyMileage = st.text_input("Estimated Monthly Mileage",disabled=carModelDropDown())
                      
    with tab2:
        homeTypeQuestion='<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Select your home type</h4>'
        st.markdown(homeTypeQuestion, unsafe_allow_html=True)
        homeType = st.selectbox("🏠",('House (Detached)', 'House (Attached) e.g.: townhouse, rowhouse, duplex)', 'Apartment (2-4 units)','Apartment (5+ units) '),key="hometype")
    
    with tab3:
        energySaverQuestion='<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you intent to save energy?</h4>'
        st.markdown(energySaverQuestion, unsafe_allow_html=True)
        energySaver=st.radio(
            "e.g. I always turn lights off when leave",
            key="energySaver",
            options=["Rarely", "Sometimes", "Always"],
        )
       
st.markdown("""---""")
# Add a button to collect input values
if st.button("Calculate"):
    try:
        int(zipcode)
    except ValueError:
        st.write("❌ Please enter correct zipcode")
        exit()
    if len(zipcode)!=5:
        st.write("❌ Please enter correct zipcode")
        exit()
        
    userProfileHeader='<h3 style="font-size:20px;">👾 Entered Information</h3>'
    st.markdown(userProfileHeader, unsafe_allow_html=True)
    if hasCar=="Yes":
        try:
            int(monthlyMileage)
        except ValueError:
            st.write("❌ Please enter correct monthlyMileage")
            exit()
        st.write("🚘 Car: " + carModel)
        st.write("🚘 Monthly Mileage: " + monthlyMileage)
    else:
        st.write("🚶🏻‍♀️ Don't have a car")
    st.write("🏠 Home type: " + homeType)
    st.write("💚 I "+energySaver+" care about saving energy")
    
    costChartHeader='<h3 style="font-size:20px;color:Chocolate;">Electricity Costs EST by Month</h3>'
    st.markdown(costChartHeader, unsafe_allow_html=True)
    
    
    
#expense chart
    # Load the data from CSV
    chart_data = pd.read_csv("monthlyElecCost.csv")
    
    total_cost = chart_data['Elec Costs'].sum()
    st.write("Your total electric costs would be $"+str(total_cost))
    
    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # Create a vertical bar chart using Altair with custom sorting
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X('Month:N', title='Month', sort=month_order),  # Sort the x-axis using the custom order
            y=alt.Y('Elec Costs:Q', title='Electric Costs'),
            color=alt.value("GoldenRod"), #alt.Color('Month:N', title='Month'),
            text=alt.Text('Elec Costs:N', format='.2f')  # Display the values with two decimal places
        )
    )
    
    # Add data labels above each bar
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        fontSize=14
    ).encode(
        text=alt.Text('Elec Costs:Q', format='.1f')
    )
    
    # Adjust the chart size to fit the container width
    st.altair_chart(chart + text, use_container_width=True)

    
    emissionChartHeader='<h3 style="font-size:20px;color:MediumSeaGreen;">CO2 Emission EST by Month</h3>'
    st.markdown(emissionChartHeader, unsafe_allow_html=True)
    
    
    
#emission chart
    # Load the data from CSV
    chart_data = pd.read_csv("monthlyCO2.csv")
    
    # Calculate the total electric cost
    total_ems = chart_data['Emission'].sum()
    st.write("Total CO2 Emission would be " + str(total_ems))
    
    # Calculate the average electric cost
    average_ems = chart_data['Emission'].mean()
    
    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # Create a vertical bar chart using Altair with conditional coloring
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X('Month:N', title='Month', sort=month_order),
            y=alt.Y('Emission:Q', title='CO2 Emissions'),
            color=alt.condition(
                alt.datum['Emission'] > average_ems,
                alt.value('Salmon'),  # Bars above average are red
                alt.value('DarkSeaGreen')  # Bars at or below average are green
            ),
            text=alt.Text('Emission:Q', format='.2f')  # Display the values with two decimal places
        )
    ).properties(
        width=alt.Step(60)  # Adjust the bar width
    )
    
    # Add data labels above each bar
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        fontSize=14
    ).encode(
        text=alt.Text('Emission:Q', format='.2f')
    )
    
    # Adjust the chart size to fit the container width and display the legend
    st.altair_chart(chart + text, use_container_width=True)
        
    
    m = folium.Map(location=[39.949610, -75.150282], zoom_start=12,tiles='CartoDB positron')
    #st_map=st_folium(m,width=750,height=400)
