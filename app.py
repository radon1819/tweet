import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Set page layout to wide
st.set_page_config(layout="wide")

# Load and clean data from CSV
@st.cache_data
def load_and_clean_data(file_path):
    data = pd.read_csv(file_path)

    # Remove duplicates
    data = data.drop_duplicates()

    # Handle missing values - you can choose different strategies like filling with 0, mean, median or dropping
    data = data.fillna(0)

    # Ensure correct data types
    data['ObservationDate'] = pd.to_datetime(data['ObservationDate'])
    data['Confirmed'] = data['Confirmed'].astype(int)
    data['Deaths'] = data['Deaths'].astype(int)
    data['Recovered'] = data['Recovered'].astype(int)

    return data

# Load data
df = load_and_clean_data('covid_19_data.csv').copy()

# Group data by country to get total confirmed cases, deaths, and recoveries
country_data = df.groupby('Country/Region').agg({
    'Confirmed': 'sum',
    'Deaths': 'sum',
    'Recovered': 'sum'
}).reset_index()

state_data = df.groupby('Province/State').agg({
    'Confirmed': 'sum',
    'Deaths': 'sum',
    'Recovered': 'sum'
}).reset_index()

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# Main option menu for navigation
page = option_menu(
    menu_title=None,
    options=["Dashboard", "Filtered Data", "Globe", "Time Series Analysis"],
    icons=["bar-chart", "filter", "globe", "line-chart"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    key="option_menu"
)

# Display different content based on the selected page
if page == 'Dashboard':
    st.session_state.page = 'Dashboard'
    st.title("COVID-19 Dashboard")

    # Columns for COVID-19 Dataset and Summary Statistics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("COVID-19 Dataset")
        st.dataframe(df, height=315)
    with col2:
        st.subheader("Summary Statistics")
        st.write(df.describe())

    # Columns for Pie Chart and Stacked Bar Chart
    col3, col4 = st.columns(2)

    with col3:
        # Interactive Pie chart
        st.subheader("COVID-19 Cases Distribution: Deaths and Recovered")
        labels = ['Deaths', 'Recovered']
        sizes = [df['Deaths'].sum(), df['Recovered'].sum()]
        total_cases = sum(sizes)

        fig_pie = px.pie(values=sizes, names=labels, title=f'Deaths vs Recovered Cases (Total Cases: {total_cases})')
        st.plotly_chart(fig_pie)

    with col4:
        # Stacked Bar Chart
        st.subheader("Breakdown of Cases by Country/Region")
        fig_bar = px.bar(country_data, x='Country/Region', y=['Confirmed', 'Deaths', 'Recovered'],
                         title='Confirmed, Deaths, and Recovered Cases by Country/Region',
                         labels={'value': 'Number of Cases', 'variable': 'Category'},
                         barmode='stack')
        st.plotly_chart(fig_bar)

elif page == 'Filtered Data':
    st.session_state.page = 'Filtered Data'
    st.title("Filtered Data Page")

    # Multiselect for countries
    selected_countries = st.multiselect("Select Country/Region(s)", df['Country/Region'].unique())
    country_filtered_data = df[df['Country/Region'].isin(selected_countries)]

    if not country_filtered_data.empty:
        # Check if only one country is selected
        if len(selected_countries) == 1:
            selected_country = selected_countries[0]

            # Get unique states for the selected country
            available_states = country_filtered_data[country_filtered_data['Country/Region'] == selected_country]['Province/State'].unique()

            # Multiselect for states within selected country
            selected_states = st.multiselect("Select Province/State(s) (optional)", available_states)

            if selected_states:
                state_filtered_data = country_filtered_data[(country_filtered_data['Country/Region'] == selected_country) & 
                                                            (country_filtered_data['Province/State'].isin(selected_states))]
            else:
                state_filtered_data = country_filtered_data[country_filtered_data['Country/Region'] == selected_country]

            st.subheader("Filtered Data by Selected Countries and States")
            st.dataframe(state_filtered_data, width=1500)

            # Interactive Line Chart for the selected country and states
            st.subheader("Confirmed Cases Over Time")
            fig_line_confirmed = px.line(state_filtered_data, x='ObservationDate', y='Confirmed', 
                               title='Confirmed Cases Over Time', labels={'ObservationDate': 'Date', 'Confirmed': 'Confirmed Cases'},
                               markers=True)
            st.plotly_chart(fig_line_confirmed)
            
            st.subheader("Recovered Cases Over Time")
            fig_line_recovered = px.line(state_filtered_data, x='ObservationDate', y='Recovered', 
                               title='Recovered Cases Over Time', labels={'ObservationDate': 'Date', 'Recovered': 'Recovered Cases'},
                               markers=True)
            st.plotly_chart(fig_line_recovered)
            
            st.subheader("Deaths Over Time")
            fig_line_deaths = px.line(state_filtered_data, x='ObservationDate', y='Deaths', 
                               title='Deaths Over Time', labels={'ObservationDate': 'Date', 'Deaths': 'Deaths'},
                               markers=True)
            st.plotly_chart(fig_line_deaths)

            # Interactive Pie chart for deaths and recovered in the selected country and states
            st.subheader("COVID-19 Cases Distribution: Deaths and Recovered")
            labels_filtered = ['Deaths', 'Recovered']
            sizes_filtered = [state_filtered_data['Deaths'].sum(), state_filtered_data['Recovered'].sum()]
            total_cases_filtered = sum(sizes_filtered)
            fig_pie_filtered = px.pie(values=sizes_filtered, names=labels_filtered, title=f'Deaths vs Recovered Cases (Filtered Data: Total Cases: {total_cases_filtered})')
            st.plotly_chart(fig_pie_filtered)
        else:
            # Plot line chart for the entire country without including states
            st.subheader("Confirmed Cases Over Time for Selected Country(s)")
            country_filtered_data_grouped = country_filtered_data.groupby('ObservationDate').sum().            country_filtered_data_grouped = country_filtered_data.groupby('ObservationDate').sum().reset_index()
            fig_line_countries = px.line(country_filtered_data_grouped, x='ObservationDate', y='Confirmed', 
                                         title='Confirmed Cases Over Time for Selected Country(s)', 
                                         labels={'ObservationDate': 'Date', 'Confirmed': 'Confirmed Cases'},
                                         markers=True)
            st.plotly_chart(fig_line_countries)
            
            st.subheader("Recovered Cases Over Time for Selected Country(s)")
            fig_line_countries_recovered = px.line(country_filtered_data_grouped, x='ObservationDate', y='Recovered', 
                                         title='Recovered Cases Over Time for Selected Country(s)', 
                                         labels={'ObservationDate': 'Date', 'Recovered': 'Recovered Cases'},
                                         markers=True)
            st.plotly_chart(fig_line_countries_recovered)
            
            st.subheader("Deaths Over Time for Selected Country(s)")
            fig_line_countries_deaths = px.line(country_filtered_data_grouped, x='ObservationDate', y='Deaths', 
                                         title='Deaths Over Time for Selected Country(s)', 
                                         labels={'ObservationDate': 'Date', 'Deaths': 'Deaths'},
                                         markers=True)
            st.plotly_chart(fig_line_countries_deaths)
            
            # Interactive Pie chart for deaths and recovered in the selected countries
            st.subheader("COVID-19 Cases Distribution: Deaths and Recovered (Filtered Data)")
            labels_filtered = ['Deaths', 'Recovered']
            sizes_countries_filtered = [country_filtered_data['Deaths'].sum(), country_filtered_data['Recovered'].sum()]
            total_cases_countries_filtered = sum(sizes_countries_filtered)
            fig_pie_countries_filtered = px.pie(values=sizes_countries_filtered, names=labels_filtered, title=f'Deaths vs Recovered Cases (Filtered Data: Total Cases: {total_cases_countries_filtered})', height=600)
            st.plotly_chart(fig_pie_countries_filtered)

elif page == 'Globe':
    st.session_state.page = 'Globe'
    st.title("Heatmap of COVID-19 Cases by Country/Region")

    # Generate heatmap
    fig_heatmap = px.choropleth(country_data,
                                 locations="Country/Region",
                                 locationmode="country names",
                                 color="Confirmed",
                                 hover_name="Country/Region",
                                 projection="natural earth",
                                 title="Heatmap of COVID-19 Cases by Country/Region (Confirmed Cases)",
                                 template="plotly_dark",
                                 color_continuous_scale="YlOrRd",
                                 labels={'Confirmed':'Confirmed Cases'})
    
    fig_heatmap.update_geos(showcountries=True)
    fig_heatmap.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig_heatmap)

elif page == 'Time Series Analysis':
    st.session_state.page = 'Time Series Analysis'
    st.title("Time Series Analysis of COVID-19 Cases")

    # Group data by date
    date_grouped = df.groupby('ObservationDate').agg({
        'Confirmed': 'sum',
        'Deaths': 'sum',
        'Recovered': 'sum'
    }).reset_index()

    # Calculate daily new cases
    date_grouped['NewConfirmed'] = date_grouped['Confirmed'].diff().fillna(0)
    date_grouped['NewDeaths'] = date_grouped['Deaths'].diff().fillna(0)
    date_grouped['NewRecovered'] = date_grouped['Recovered'].diff().fillna(0)

    # Plot daily new confirmed cases
    st.subheader("Daily New Confirmed Cases")
    fig_new_confirmed = px.line(date_grouped, x='ObservationDate', y='NewConfirmed', 
                                title='Daily New Confirmed Cases Over Time', 
                                labels={'ObservationDate': 'Date', 'NewConfirmed': 'Daily New Confirmed Cases'},
                                markers=True)
    st.plotly_chart(fig_new_confirmed)

    # Plot daily new deaths
    st.subheader("Daily New Deaths")
    fig_new_deaths = px.line(date_grouped, x='ObservationDate', y='NewDeaths', 
                             title='Daily New Deaths Over Time', 
                             labels={'ObservationDate': 'Date', 'NewDeaths': 'Daily New Deaths'},
                             markers=True)
    st.plotly_chart(fig_new_deaths)

    # Plot daily new recoveries
    st.subheader("Daily New Recovered Cases")
    fig_new_recovered = px.line(date_grouped, x='ObservationDate', y='NewRecovered', 
                                title='Daily New Recovered Cases Over Time', 
                                labels={'ObservationDate': 'Date', 'NewRecovered': 'Daily New Recovered Cases'},
                                markers=True)
    st.plotly_chart(fig_new_recovered)

    # Calculate growth rates
    date_grouped['GrowthRateConfirmed'] = date_grouped['NewConfirmed'].pct_change().fillna(0)
    date_grouped['GrowthRateDeaths'] = date_grouped['NewDeaths'].pct_change().fillna(0)
    date_grouped['GrowthRateRecovered'] = date_grouped['NewRecovered'].pct_change().fillna(0)

    # Plot growth rates
    st.subheader("Growth Rate of Confirmed Cases")
    fig_growth_confirmed = px.line(date_grouped, x='ObservationDate', y='GrowthRateConfirmed', 
                                   title='Growth Rate of Confirmed Cases Over Time', 
                                   labels={'ObservationDate': 'Date', 'GrowthRateConfirmed': 'Growth Rate of Confirmed Cases'},
                                   markers=True)
    st.plotly_chart(fig_growth_confirmed)

    st.subheader("Growth Rate of Deaths")
    fig_growth_deaths = px.line(date_grouped, x='ObservationDate', y='GrowthRateDeaths', 
                                title='Growth Rate of Deaths Over Time', 
                                labels={'ObservationDate': 'Date', 'GrowthRateDeaths': 'Growth Rate of Deaths'},
                                markers=True)
    st.plotly_chart(fig_growth_deaths)

    st.subheader("Growth Rate of Recovered Cases")
    fig_growth_recovered = px.line(date_grouped, x='ObservationDate', y='GrowthRateRecovered', 
                                   title='Growth Rate of Recovered Cases Over Time', 
                                   labels={'ObservationDate': 'Date', 'GrowthRateRecovered': 'Growth Rate of Recovered Cases'},
                                   markers=True)
    st.plotly_chart(fig_growth_recovered)

