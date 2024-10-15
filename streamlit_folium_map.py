import streamlit as st
import pandas as pd
import folium 
from streamlit_folium import st_folium

# Ladataan kaksi eri CSV-tiedostoa
url_location = "https://raw.githubusercontent.com/xolooh/Fysiikan-loppuprojekti/refs/heads/main/Location.csv"
url_acceleration = "https://raw.githubusercontent.com/xolooh/Fysiikan-loppuprojekti/refs/heads/main/Linear%20Acceleration.csv"

# Ladataan tiedot DataFrameihin
df_location = pd.read_csv(url_location)
df_acceleration = pd.read_csv(url_acceleration)

st.title('My journey to work')

#Print values
st.write("Keskinopeus on :", df_location['Velocity (m/s)'].mean(),'m/s' )
st.write("Kokonaismatka on :", df_location['Distance (km)'].max(),'km' )

#draw line plot
st.line_chart(df_location, x = 'Time (s)', y = 'Distance (km)', y_label = 'Distance',x_label = 'Time')

#Create a map where the center is at start_lat start_long and zoom level is defined
start_lat = df_location['Latitude (°)'].mean()
start_long = df_location['Longitude (°)'].mean()
map = folium.Map(location = [start_lat,start_long], zoom_start = 14)

#Draw the map
folium.PolyLine(df_location[['Latitude (°)','Longitude (°)']], color = 'blue', weight = 3.5, opacity = 1).add_to(map)



#Define map dimensions and show the map
st_map = st_folium(map, width=900, height=650)