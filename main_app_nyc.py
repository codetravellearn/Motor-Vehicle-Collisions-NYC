import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in NYC")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC 🗽 🚗 💥")

@st.cache(persist = True)
# to make the function more efficient we used cache
#it will only rerun the computio when there any change made and not everytime


def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows =nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace = True)
    #The dropna() function is used to remove missing values.
    # subset: Labels along other axis to consider, e.g. if you are dropping rows these would be a list of columns to include.
    # inplcae : If True, do operation inplace and return None.
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {'crash_date_crash_time': 'date/time'}, inplace = True)
    return data

data = load_data(100000)
original_data = data

#-----------
st.header("Where are the most people injured in NYC")
injured_people = st.slider("", 0 ,19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how = "any"))

st.header("How many collisions occur during a given time of the day?")
hour = st.slider("Hour to look at",0,23)
data = data[data['date/time'].dt.hour == hour]

# to visualize the vehicle collisions in a selected hour of a day
# in 24 hr format
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

# deck gl
# A Layered Approach to Data Visualization
# deck.gl allows complex visualizations to be constructed by composing existing layers,
# and makes it easy to package and share new visualizations as reusable layers.
# for thiswe import pydeck as pydeck


st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom":11,
        "pitch": 50,
        },
    layers = [
    pdk.Layer(
    "HexagonLayer",
    data = data[['date/time', 'latitude','longitude']],
    get_position = ['longitude','latitude'],
    # definingthe radius of the hexagons
    radius = 100,
    # making the hexagons 3-D by making them rod -like
    extruded = True,
    pickable = True,
    # the relative height of hexagons
    elevation_scale =4,
    #
    elevation_range = [0,600],
    ),
    ],
))

#-----------------------------Charts And Histogram ------------------------------------
# using Plotly (library), it allows to create interactive plots
# very Quickly, provided that the input is a tidy dataframe
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) %24))

#creting a new dataframe, which will get data between two specific hrs
filtered = data[
    (data['date/time'].dt.hour >= hour) &(data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins =60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)


#--------------------- Dangerous streets-------------------------------------
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ['Pedestrians', 'Cyclists', 'Motorosts'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ['injured_motorists'], ascending=False).dropna(how='any')[:5])


#--------------------------- Raw Data ---------------------------------------
if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)
