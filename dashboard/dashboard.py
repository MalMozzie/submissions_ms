import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load Data ---
@st.cache_data
def load_data():
    day_df = pd.read_csv("data/day.csv")
    hour_df = pd.read_csv("data/hour.csv")
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    return day_df, hour_df

day_df, hour_df = load_data()

# --- Sidebar Profile ---
img_path = "assets/dicoding.png"
st.sidebar.image(img_path, width=150)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.title("Profile:")
st.sidebar.markdown("**• Nama: Muhammad Akmal**")
st.sidebar.markdown("**• Email: makmal1709@gmail.com**")

# --- Sidebar Filter Data ---
st.sidebar.header("Filter Data")
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

start_date, end_date = st.sidebar.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# --- Pemetaan Kondisi Cuaca ---
weather_map = {1: 'Cerah', 2: 'Berawan', 3: 'Hujan ringan', 4: 'Hujan lebat'}
day_df['weather_label'] = day_df['weathersit'].replace(weather_map)
hour_df['weather_label'] = hour_df['weathersit'].replace(weather_map)

# **Filter Rentang Waktu**
filtered_day_df = day_df[
    (day_df['dteday'] >= pd.Timestamp(start_date)) &   
    (day_df['dteday'] <= pd.Timestamp(end_date))
]

filtered_hour_df = hour_df[
    (hour_df['dteday'] >= pd.Timestamp(start_date)) &   
    (hour_df['dteday'] <= pd.Timestamp(end_date))
]

# **Filter Berdasarkan Kondisi Cuaca**
selected_weather = st.sidebar.selectbox("Pilih Kondisi Cuaca", options=list(weather_map.values()))
filtered_day_weather = filtered_day_df[filtered_day_df['weather_label'] == selected_weather]
filtered_hour_weather = filtered_hour_df[filtered_hour_df['weather_label'] == selected_weather]

# --- Dashboard Title ---
st.title("Dashboard Analisis Penyewaan Sepeda")

# --- Sidebar Pilihan Visualisasi ---
st.sidebar.header("Pilih Visualisasi")
visualization_option = st.sidebar.radio(
    "Pilih jenis visualisasi:",  
    ['Pengaruh Kondisi Cuaca', 'Waktu Paling Sibuk', 'Hari Kerja vs Akhir Pekan']
)

# 1. Pengaruh Kondisi Cuaca terhadap Penyewaan
if visualization_option == 'Pengaruh Kondisi Cuaca':
    if filtered_day_df.empty:
        st.warning("Tidak ada data untuk rentang waktu yang dipilih.")
    else:
        # Pastikan urutan kondisi cuaca sesuai
        weather_rentals = filtered_day_df.groupby('weather_label')['cnt'].mean().reset_index()
        weather_rentals['weather_label'] = pd.Categorical(
            weather_rentals['weather_label'], categories=['Cerah', 'Berawan', 'Hujan ringan', 'Hujan lebat'], ordered=True
        )

        # Urutkan berdasarkan kategori
        weather_rentals = weather_rentals.sort_values('weather_label')

        # Warna dari terang ke gelap
        color_map = {'Cerah': '#4A90E2', 'Berawan': '#357ABD', 'Hujan ringan': '#2A5F9E', 'Hujan lebat': '#1D4377'}

        fig_weather = px.bar(
            weather_rentals, x='weather_label', y='cnt',
            title=f'Pengaruh Kondisi Cuaca terhadap Penyewaan Sepeda ({start_date} - {end_date})',
            labels={'weather_label': 'Kondisi Cuaca', 'cnt': 'Jumlah Penyewaan'},
            color='weather_label',
            color_discrete_map=color_map
        )

        st.plotly_chart(fig_weather)

# --- 2. Kapan Waktu Paling Sibuk untuk Penyewaan Sepeda? ---
elif visualization_option == 'Waktu Paling Sibuk':
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Harian", "Mingguan", "Bulanan", "Tahunan", "Jam"])

    # **Harian (Penyewaan per Hari dalam Seminggu)**
    with tab1:
        if filtered_day_weather.empty:
            st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
        else:
            rentals_per_day = filtered_day_weather.groupby(filtered_day_weather['dteday'].dt.dayofweek)['cnt'].mean()
            rentals_per_day = rentals_per_day.reindex(range(7), fill_value=0)

            fig_day = px.bar(
                x=["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"], y=rentals_per_day.values,  
                title=f"Rata-rata Penyewaan Sepeda per Hari dalam Seminggu ({selected_weather})",
                labels={'x': 'Hari', 'y': 'Jumlah Penyewaan'}
            )
            st.plotly_chart(fig_day)

    # **Mingguan (Penyewaan per Minggu dalam Sebulan)**
    with tab2:
        if filtered_day_weather.empty:
            st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
        else:
            filtered_day_weather['week_of_month'] = (filtered_day_weather['dteday'].dt.day - 1) // 7 + 1
            rentals_per_week = filtered_day_weather.groupby("week_of_month")["cnt"].mean()

            fig_week = px.bar(
                x=rentals_per_week.index, y=rentals_per_week.values,  
                title=f"Rata-rata Penyewaan Sepeda per Minggu dalam Sebulan ({selected_weather})",
                labels={'x': 'Minggu ke-', 'y': 'Jumlah Penyewaan'}
            )
            st.plotly_chart(fig_week)

    # **Bulanan (Penyewaan per Bulan dalam Setahun)**
    with tab3:
        if filtered_day_weather.empty:
            st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
        else:
            rentals_per_month = filtered_day_weather.groupby(filtered_day_weather['dteday'].dt.month)['cnt'].mean()

            fig_month = px.bar(
                x=rentals_per_month.index, y=rentals_per_month.values,  
                title=f"Rata-rata Penyewaan Sepeda per Bulan ({selected_weather})",
                labels={'x': 'Bulan', 'y': 'Jumlah Penyewaan'}
            )
            st.plotly_chart(fig_month)

    # **Tahunan (Tren Penyewaan per Tahun)**
    with tab4:
        if filtered_day_weather.empty:
            st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
        else:
            rentals_per_year = filtered_day_weather.groupby(filtered_day_weather['dteday'].dt.year)['cnt'].mean()

            fig_year = px.line(
                x=rentals_per_year.index, y=rentals_per_year.values, markers=True,  
                title=f"Tren Penyewaan Sepeda per Tahun ({selected_weather})",
                labels={'x': 'Tahun', 'y': 'Jumlah Penyewaan'}
            )
            st.plotly_chart(fig_year)

    # **Jam (Penyewaan per Jam)**
    with tab5:
        if filtered_hour_weather.empty:
            st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
        else:
            rentals_per_hour = filtered_hour_weather.groupby('hr')['cnt'].mean()
            peak_hour = rentals_per_hour.idxmax()
            fig_hour = px.line(
                x=rentals_per_hour.index, y=rentals_per_hour.values, markers=True,  
                title=f"Rata-rata Penyewaan Sepeda per Jam ({selected_weather})",
                labels={'x': 'Jam', 'y': 'Jumlah Penyewaan'}
            )
            st.plotly_chart(fig_hour)
            st.write(f"**Jam tersibuk:** {peak_hour}:00")

# 3. Perbandingan Hari Kerja vs Akhir Pekan
elif visualization_option == 'Hari Kerja vs Akhir Pekan':
    # Filter berdasarkan rentang waktu dan kondisi cuaca
    filtered_day_df_time = day_df[
        (day_df['dteday'] >= pd.Timestamp(start_date)) &   
        (day_df['dteday'] <= pd.Timestamp(end_date)) &
        (day_df['weather_label'] == selected_weather)  # Filter kondisi cuaca
    ]

    if filtered_day_df_time.empty:
        st.warning("Tidak ada data untuk rentang waktu dan kondisi cuaca yang dipilih.")
    else:
        # Menentukan kategori hari
        filtered_day_df_time['day_type'] = filtered_day_df_time['workingday'].map({1: 'Hari Kerja', 0: 'Akhir Pekan'})

        # Rata-rata penyewaan sepeda per kategori hari
        avg_rentals = filtered_day_df_time.groupby('day_type')['cnt'].mean().reset_index()

        # Visualisasi menggunakan plotly
        fig_comparison = px.bar(avg_rentals, x='day_type', y='cnt',
                                title=f'Rata-rata Penyewaan Sepeda: Hari Kerja vs Akhir Pekan ({selected_weather})',
                                labels={'cnt': 'Jumlah Rata-rata Penyewaan'},
                                color='day_type', color_discrete_map={'Hari Kerja': 'blue', 'Akhir Pekan': 'orange'})

        st.plotly_chart(fig_comparison)

# --- Opsi Tampilkan Data Mentah ---
if st.sidebar.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Harian")
    st.write(filtered_day_df.head())
    st.subheader("Data Jam")
    st.write(filtered_hour_df.head())

st.caption('Copyright © submission_dataset 2025')
