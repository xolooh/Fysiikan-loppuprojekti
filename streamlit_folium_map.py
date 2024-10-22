import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.fft import fft
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# Ladataan CSV-tiedostot
url_location = "https://raw.githubusercontent.com/xolooh/Fysiikan-loppuprojekti/refs/heads/main/Location.csv"
url_acceleration = "https://raw.githubusercontent.com/xolooh/Fysiikan-loppuprojekti/refs/heads/main/Linear%20Acceleration.csv"

df_location = pd.read_csv(url_location, sep='\t')
df_acceleration = pd.read_csv(url_acceleration, sep='\t')

mean_velocity = df_location['Velocity (m/s)'].mean()

df_location['Distance (km)'] = (df_location['Velocity (m/s)'] * (df_location['Time (s)'].diff().fillna(0))).cumsum() / 1000
distance_km = df_location['Distance (km)'].max()

def butter_lowpass_filter(data, cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

fs = 50  
cutoff = 3  

filtered_acc_z = butter_lowpass_filter(df_acceleration['Linear Acceleration z (m/s^2)'], cutoff, fs)

max_acceleration = df_acceleration['Linear Acceleration z (m/s^2)'].max()
max_deceleration = df_acceleration['Linear Acceleration z (m/s^2)'].min()

# Askelten laskeminen
step_threshold = 0.3
steps = np.sum((filtered_acc_z[1:-1] > step_threshold) & 
               (filtered_acc_z[1:-1] > filtered_acc_z[0:-2]) & 
               (filtered_acc_z[1:-1] > filtered_acc_z[2:]))

acceleration_z = df_acceleration['Linear Acceleration z (m/s^2)'].dropna().values

# Fourier-analyysi
n = len(acceleration_z)
yf = fft(acceleration_z)
xf = np.linspace(0.0, fs/2, n//2)

dominant_freq = xf[np.argmax(2.0/n * np.abs(yf[:n//2]))]


steps_fourier = dominant_freq * (df_acceleration['Time (s)'].iloc[-1] - df_acceleration['Time (s)'].iloc[0])

# Askelpituuden laskeminen
distance_km = df_location['Distance (km)'].max()
step_length = (distance_km * 1000) / steps if steps > 0 else 0

st.title('Kurvit suoriksi')

# Tulostetaan lasketut arvot
st.write("Mittaukset ei ole otettu kävellen!")
st.write("Keskinopeus: ", mean_velocity, 'm/s')
st.write("Kokonaismatka: ", distance_km, 'km')
st.write("Askelmäärä laskettuna suodatuksen avulla: ", steps)
st.write("Askelmäärä laskettuna Fourier-analyysin avulla:", int(steps_fourier))
st.write("Askelpituus: ", step_length, 'm')
st.write("Maksimikiihtyvyys: ", max_acceleration, 'm/s²')

st.title("Suodatettu kiihtyvyysdatan Z-komponentti")
fig, ax = plt.subplots()
ax.plot(df_acceleration['Time (s)'], filtered_acc_z, label='Suodatettu Z-akselin kiihtyvyys')
ax.set_xlabel('Aika (s)')
ax.set_ylabel('Kiihtyvyys (m/s^2)')
st.pyplot(fig)

st.title("Tehospektri")
fig, ax = plt.subplots()
ax.plot(xf, 2.0/n * np.abs(yf[:n//2]), label='Z-akselin PSD')
ax.set_xlabel('Taajuus (Hz)')
ax.set_ylabel('Amplitudi')
st.pyplot(fig)

st.title("Karttakuva")
start_lat = df_location['Latitude (°)'].mean()
start_long = df_location['Longitude (°)'].mean()
map = folium.Map(location=[start_lat, start_long], zoom_start=14)

folium.PolyLine(df_location[['Latitude (°)', 'Longitude (°)']], color='blue', weight=3.5, opacity=1).add_to(map)

st_map = st_folium(map, width=900, height=650)