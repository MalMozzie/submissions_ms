import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    day_df = pd.read_csv("data/day.csv")
    hour_df = pd.read_csv("data/hour.csv")
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    return day_df, hour_df

day_df, hour_df = load_data()

# Sidebar Profile
img_path = "assets/dicoding.png"
st.sidebar.image(img_path, width=150)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Profile:")
st.sidebar.markdown("""
    **• Nama: Muhammad Akmal**  
    **• Email: [makmal1709@gmail.com](mailto:makmal1709@gmail.com)**
""", unsafe_allow_html=True)

# Sidebar Filter Data
st.sidebar.header("Filter Data")
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

weather_map = {1: 'Cerah', 2: 'Berawan', 3: 'Hujan ringan', 4: 'Hujan lebat'}
selected_weather = st.sidebar.selectbox("Pilih Kondisi Cuaca", options=list(weather_map.values()))

# Filter Data berdasarkan input pengguna
filtered_day_df = day_df[
    (day_df['dteday'] >= pd.Timestamp(start_date)) & 
    (day_df['dteday'] <= pd.Timestamp(end_date)) &
    (day_df['weathersit'].map(weather_map) == selected_weather)
]

filtered_hour_df = hour_df[
    (hour_df['dteday'] >= pd.Timestamp(start_date)) & 
    (hour_df['dteday'] <= pd.Timestamp(end_date)) &
    (hour_df['weathersit'].map(weather_map) == selected_weather)
]

# Dashboard Title
st.title("Dashboard Analisis Penyewaan Sepeda")

# Sidebar Pilihan Visualisasi
st.sidebar.header("Pilih Visualisasi")
visualization_option = st.sidebar.radio(
    "Pilih jenis visualisasi:", 
    ['Tren Penyewaan Sepeda', 'Perbandingan Hari Kerja & Akhir Pekan', 'Penyewaan Sepeda Berdasarkan Musim']
)

# 1. Tren Penyewaan Sepeda
if visualization_option == 'Tren Penyewaan Sepeda':
    daily_trend = filtered_day_df.groupby('dteday')['cnt'].sum().reset_index()
    fig_trend = px.line(daily_trend, x='dteday', y='cnt', 
                         title=f'Tren Penyewaan Sepeda - {selected_weather}', 
                         labels={'dteday': 'Tanggal', 'cnt': 'Jumlah Penyewaan'})
    st.plotly_chart(fig_trend)

# 2. Perbandingan Hari Kerja & Akhir Pekan
elif visualization_option == 'Perbandingan Hari Kerja & Akhir Pekan':
    filtered_day_df['day_type'] = filtered_day_df['workingday'].map({1: 'Hari Kerja', 0: 'Akhir Pekan'})
    avg_rentals = filtered_day_df.groupby('day_type')['cnt'].mean().reset_index()
    fig_comparison = px.bar(avg_rentals, x='day_type', y='cnt', 
                            title=f'Rata-rata Penyewaan Sepeda: Hari Kerja vs Akhir Pekan - {selected_weather}',
                            labels={'cnt': 'Jumlah Rata-rata Penyewaan'})
    st.plotly_chart(fig_comparison)

# 3. Penyewaan Sepeda Berdasarkan Musim
elif visualization_option == 'Penyewaan Sepeda Berdasarkan Musim':
    season_map = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
    filtered_day_df['season_label'] = filtered_day_df['season'].map(season_map)
    fig_season = px.box(filtered_day_df, x='season_label', y='cnt', 
                         title=f'Distribusi Penyewaan Berdasarkan Musim - {selected_weather}',
                         labels={'season_label': 'Musim', 'cnt': 'Jumlah Penyewaan'})
    st.plotly_chart(fig_season)

# Opsi Tampilkan Data Mentah
if st.sidebar.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Harian")
    st.write(filtered_day_df.head())
    st.subheader("Data Jam")
    st.write(filtered_hour_df.head())

st.caption('Copyright © submission_dataset 2025')
