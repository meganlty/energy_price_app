# Import necessary libraries
import streamlit as st
import pandas as pd
import electricity_estimation_functions as root_fct
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import electricity_prices as ep
from datetime import datetime

# Define custom CSS for styling
custom_css = """
<style>
    p {
        font-size: 16px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Define the header for the app
header = '<h2 style="font-size:40px;"><span style="color:MediumSeaGreen;">ElectriWise</span> <span style="color:Chocolate;">Estimator</span> App</h2>'
st.markdown(header, unsafe_allow_html=True)

# Initialize the 'hasCar' variable
hasCar = "No"

# Function to determine whether to show the car model dropdown
def carModelDropDown():
    if hasCar == "Yes":
        return False
    else:
        return True

# Create a container for the user input section
with st.container():
    # Step 1: Select State
    st.markdown('<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">1️⃣   Please Select Your State</h3>', unsafe_allow_html=True)
    statelist = root_fct.get_statelist()
    state_dropdown = st.selectbox(" ", statelist, key="state")

    # Step 2: Select State to Compare
    compareStateQuestion = '<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">2️⃣   With which state would you like to compare?</h3>'
    st.markdown(compareStateQuestion, unsafe_allow_html=True)
    statelist.append("-")
    state_dropdown_2 = st.selectbox(" ",statelist, key="state2", index=len(statelist)-1)

    # Step 3: Tell us more about you (Tabs for Electric Car, Home Type, Energy Consciousness)
    detailedQuestionPrompt = '<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">3️⃣   Tell us more about you</h3>'
    st.markdown(detailedQuestionPrompt, unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Electric Car", "Home Type", "Energy Consciousness"])

    # Step 3.1: Select Electric Car
    with tab1:
        carQuestion = '<h3 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you have an electric vehicle?</h3>'
        st.markdown(carQuestion, unsafe_allow_html=True)
        hasCar = st.radio("🚘", key="car", options=["No", "Yes"], on_change=carModelDropDown)
        with st.expander("If YES", expanded=not carModelDropDown()):
            carModel_dropdown = st.selectbox("What's the model", ("Audi", "Ford", "Hyundai", "Nissan", "Porsche", "Tesla", "Volkswagen"), key="carmodel", disabled=carModelDropDown(), index=None)
            monthlyMileage_input = st.text_input("Estimated Monthly Mileage in km", value="0", disabled=carModelDropDown())

    # Step 3.2: Select Home Type
    with tab2:
        homeTypeQuestion = '<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Select your home type</h4>'
        st.markdown(homeTypeQuestion, unsafe_allow_html=True)
        homeType_dropdown = st.selectbox("🏠", ('House (Detached)', 'House (Attached) e.g.: townhouse, rowhouse, duplex)', 'Apartment (2-4 units)', 'Apartment (5+ units) '), key="hometype")

    # Step 3.3: Select Energy Consciousness Level
    with tab3:
        energySaverQuestion = '<h4 style="font-size:22px;margin-bottom: 0;margin-top: 0; padding-bottom: 0px;">Do you intend to save energy?</h4>'
        st.markdown(energySaverQuestion, unsafe_allow_html=True)
        energySaver_select = st.radio(
            "e.g. I always turn lights off when leave",
            key="energySaver",
            options=["Rarely", "Sometimes", "Always"],
            index=1
        )

st.markdown("""---""")

# Step 4: Calculate Button
if st.button("4️⃣ Calculate"):

    # If user select None state to compare against, default this value to home state
    if state_dropdown_2 =="-":
        state_dropdown_2=state_dropdown
    # Check if user want to do comparison
    if state_dropdown ==state_dropdown_2:
        comparison_needed=False
    else:
        comparison_needed=True

    # Display user's entered information
    userProfileHeader = '<h3 style="font-size:20px;">👾 Entered Information</h3>'
    st.markdown(userProfileHeader, unsafe_allow_html=True)
    if hasCar == "Yes":
        try:
            int(monthlyMileage_input)
        except ValueError:
            st.write("❌ Please enter a correct monthlyMileage")
            exit()
        st.write("🚘 Car: " + carModel_dropdown)
        st.write("🚘 Monthly Mileage: " + monthlyMileage_input)
    else:
        st.write("🚶🏻‍♀️ Don't have a car")
    st.write("🏠 Home type: " + homeType_dropdown)
    st.write("💚 I " + energySaver_select + " care about saving energy")

    st.markdown("""---""")
    
    # Run function to calculate
    # State 1
    root_fct.get_final(state_dropdown, carModel_dropdown, int(monthlyMileage_input), homeType_dropdown, energySaver_select)
    # State 2
    root_fct.get_final(state_dropdown_2, carModel_dropdown, int(monthlyMileage_input), homeType_dropdown, energySaver_select)

    # Expense chart
    # Load the data from CSV
    month_mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    chart_data = pd.read_csv("output_data/monthlyElecCost_" + state_dropdown + ".csv")
    chart_data.rename(columns={'Unnamed: 0': 'Month'}, inplace=True)
    chart_data['State'] = state_dropdown
    chart_data2 = pd.read_csv("output_data/monthlyElecCost_" + state_dropdown_2 + ".csv")
    chart_data2.rename(columns={'Unnamed: 0': 'Month'}, inplace=True)
    chart_data2['State'] = state_dropdown_2

    # Concatenate two group of data if comparison needed
    if comparison_needed:
        chart_1_2 = pd.concat([chart_data, chart_data2], axis=0)
    else:    
        chart_1_2 = chart_data

    # Define a custom sorting order for the months
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Create a bar chart using Plotly with custom sorting
    fig = px.bar(
        chart_1_2,
        x='Month',
        y='Elec Costs',
        color='State',
        barmode='group',
        pattern_shape='State',
        title=state_dropdown + ' Electric Costs by Month',
        text='Elec Costs',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Electric Costs',
        showlegend=False,
        title="Electricity Costs EST by Month: "+state_dropdown
    )
    fig.update_yaxes(range=[0, chart_1_2['Elec Costs'].max() * 1.1])

    if comparison_needed:
        fig.update_layout(
        showlegend=True,
        title='Electricity Costs EST by Month: '+state_dropdown + "vs. "+state_dropdown_2
        )

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

    # Calculate the total elec costs
    total_cost = chart_data['Elec Costs'].sum()
    total_cost2 = chart_data2['Elec Costs'].sum()

    # Conclude the electric costs in two states
    st.write("💰💰💰 Your total electric in {} costs would be ${}".format(state_dropdown, str(round(float(total_cost)))))
    if comparison_needed:
        if total_cost > total_cost2:
            st.write("💰💰💰 {}% greater than the costs in {}, where the costs are ${}"
                    .format(str(round(float(1 - total_cost2 / total_cost) * 100))
                            , state_dropdown_2
                            , str(round(float(total_cost2)))))
        else:
            st.write("💰💰💰 {}% less than the costs in {}, where the costs are ${}"
                    .format(str(round(float(1 - total_cost2 / total_cost) * 100))
                            , state_dropdown_2
                            , str(round(float(total_cost2)))))
    st.markdown("""---""")

    # Emission chart
    # Load the data from CSV
    chart_data = pd.read_csv("output_data/monthlyCO2_" + state_dropdown + ".csv")
    chart_data.rename(columns={'Unnamed: 0': 'Month'}, inplace=True)
    chart_data['State'] = state_dropdown
    chart_data2 = pd.read_csv("output_data/monthlyCO2_" + state_dropdown_2 + ".csv")
    chart_data2.rename(columns={'Unnamed: 0': 'Month'}, inplace=True)
    chart_data2['State'] = state_dropdown_2

    # Concatenate two group of data if comparison needed
    if comparison_needed:
        chart_1_2 = pd.concat([chart_data, chart_data2], axis=0)
    else:    
        chart_1_2 = chart_data
    

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
        pattern_shape='State',
        text='Emission',
        category_orders={'Month': month_order},
    )

    # Customize the chart layout
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='CO2 Emissions in tons',
        showlegend=False,
        title='CO2 Emissions by Month: '+state_dropdown
    )
    fig.update_yaxes(range=[0, chart_1_2['Emission'].max() * 1.1])

    # Define colors for above-average and below-average emissions
    above_avg_color = 'Salmon'
    below_avg_color = 'DarkSeaGreen'

    # Assign colors based on whether emissions are above or below average
    fig['data'][0]['marker']['color'] = [
        above_avg_color if em > average_ems else below_avg_color
        for em in chart_1_2['Emission']
    ]
    if comparison_needed:
        fig.update_layout(
        showlegend=True,
        title='CO2 Emissions by Month: '+state_dropdown + "vs. "+state_dropdown_2
        )
        fig['data'][1]['marker']['color'] = [
            above_avg_color if em > average_ems else below_avg_color
            for em in chart_1_2['Emission']
        ]

    # Add data labels above each bar
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Show the chart using plotly
    st.plotly_chart(fig)

    # Calculate the total CO2 emissions
    total_ems = chart_data['Emission'].sum()
    total_ems2 = chart_data2['Emission'].sum()

    # Conclude the CO2 emission in two states
    st.write("🍃🍃🍃 Total CO2 Emission would be " + str(round(float(total_ems), 2)) + " tons")
    if comparison_needed:
        if total_ems > total_ems2:
            st.write("🍃🍃🍃 {}% greater than the emissions in {}, where the emissions are {} tons"
                    .format(str(round(float(1 - total_ems2 / total_ems) * 100, 2))
                            , state_dropdown_2
                            , str(round(float(total_ems2), 2))))
        else:
            st.write("🍃🍃🍃 {}% less than the emissions in {}, where the emissions are {} tons"
                    .format(str(round(float(1 - total_ems / total_ems2) * 100, 2))
                            , state_dropdown_2
                            , str(round(float(total_ems2), 2))))
    st.markdown("""---""")

    # Resources pie chart
    # Load the data from uses_mix function
    df_resource = pd.read_csv('input_data/resourcesEnergyMix.csv', index_col=1)
    root_fct.uses_mix(state_dropdown, df_resource)
    pie_data = pd.read_csv("output_data/resourcesMIX_" + state_dropdown + ".csv")
    root_fct.uses_mix(state_dropdown_2, df_resource)
    pie_data2 = pd.read_csv("output_data/resourcesMIX_" + state_dropdown_2 + ".csv")

    renewbableShare = pie_data[pie_data['Type'] == 'Renewable']['Proportion'].sum()
    renewbableShare2 = pie_data2[pie_data2['Type'] == 'Renewable']['Proportion'].sum()
    fossilShare = pie_data[pie_data['Type'] == 'Fossil']['Proportion'].sum()
    fossilShare2 = pie_data2[pie_data2['Type'] == 'Fossil']['Proportion'].sum()

    # Create subplots: use 'domain' type for Pie subplot
    fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
    if comparison_needed:
        fig.add_trace(go.Pie(labels=pie_data['Resource'], values=pie_data['Proportion'], name=state_dropdown + " CO2e"), 1, 1)
        fig.add_trace(go.Pie(labels=pie_data2['Resource'], values=pie_data2['Proportion'], name=state_dropdown_2 + " CO2e"), 1, 2)
        fig.update_layout(
        title_text="Energy resource Mix",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=state_dropdown, x=0.18, y=0.5, font_size=20, showarrow=False),
                     dict(text=state_dropdown_2, x=0.82, y=0.5, font_size=20, showarrow=False)])
    else:
        fig.add_trace(go.Pie(labels=pie_data['Resource'], values=pie_data['Proportion'], name=state_dropdown + " CO2e"))
        fig.update_layout(title_text="Energy Resource Mix:" + state_dropdown,)
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    

    # Show the chart using Streamlit
    st.plotly_chart(fig)

    # Conclude the renewable recources weighs of two states
    st.write("⚡⚡⚡ Renewable resources are the {}% of the total in {}".format(round(renewbableShare * 100, 2), state_dropdown))
    if comparison_needed:
        if renewbableShare > renewbableShare2:
            st.write("⚡⚡⚡ {}% greener than the resources in {}, where the renewable resources are {}%"
                    .format(str(round(float(1 - renewbableShare2 / renewbableShare) * 100, 2))
                            , state_dropdown_2
                            , str(round(float(renewbableShare2 * 100), 2))))
        else:
            st.write("⚡⚡⚡ {}% less greener than the emissions in {}, where the renewable resources are {}%"
                    .format(str(round(float(1 - renewbableShare / renewbableShare2) * 100, 2))
                            , state_dropdown_2
                            , str(round(float(renewbableShare2 * 100), 2))))
st.markdown("""---""")

# Update data from webscraping and API
with st.container():
    if st.button("Update Source Data"):
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            ep.get_eia_prices()  # You should import ep and define this function separately
            st.markdown("<p style='color: green;'>✅ Successfully Updated from https://api.eia.gov/</p>", unsafe_allow_html=True)
            st.write("Last Updated: " + current_time)
        except:
            st.markdown("<p style='color: red;'>❌ No data found from https://api.eia.gov/</p>", unsafe_allow_html=True)
            exit()
