import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


sns.set(style='dark')

def total_regist(day_df):
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual(day_df):
    cas_df = day_df.groupby(by="dteday").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def total_count(hour_df):
    hour_count_df = hour_df.groupby(by="hours").agg({"count_total": "sum"})
    return hour_count_df

def count_day(day_df):
    day_df_count_2011 = day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')
    return day_df_count_2011

def sum_order(hour_df):
    sum_order_items_df = hour_df.groupby("hours")["count_total"].sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def by_season(day_df): 
    season_df = day_df.groupby(by="season")["count_total"].sum().reset_index() 
    return season_df

days_df = pd.read_csv("dashboard/day_clean_ver.csv")
hours_df = pd.read_csv("dashboard/hour_clean_ver.csv")

days_df["dteday"] = pd.to_datetime(days_df["dteday"])
hours_df["dteday"] = pd.to_datetime(hours_df["dteday"])


min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()


with st.sidebar:
    st.image("images/bicycle.jpg", caption="Bike Sharing", use_column_width=True)
    start_date, end_date = st.date_input('Rentang Waktu', value=(min_date_days, max_date_days), min_value=min_date_days, max_value=max_date_days)


main_df_days = days_df[(days_df["dteday"] >= pd.to_datetime(start_date)) & (days_df["dteday"] <= pd.to_datetime(end_date))]
main_df_hour = hours_df[(hours_df["dteday"] >= pd.to_datetime(start_date)) & (hours_df["dteday"] <= pd.to_datetime(end_date))]

day_df_count_2011 = count_day(main_df_days)
reg_df = total_regist(main_df_days)
cas_df = total_casual(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = by_season(main_df_hour)

st.header("Bike Sharing Dataset 🚲")

# Create Tabs for visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Statistik Data Umum", "Registered vs Casual", "Peminjam Terpadat Berdasarkan Jam", "Peminjam Berdasarkan Season"])

with tab1:
    st.markdown("<h2 style='text-align: center;'>🚴‍♂️ Daily Bike Sharing Summary</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Kolom 1: Total Sharing Bike
    with col1:
        total_orders = day_df_count_2011["count_total"].sum()
        st.metric(label="Total Sharing Bike", value=f"{total_orders:,.0f}")

    # Kolom 2: Total Registered
    with col2:
        total_registered_sum = reg_df["register_sum"].sum()
        st.metric(label="Total Registered", value=f"{total_registered_sum:,.0f}")

    # Kolom 3: Total Casual
    with col3:
        total_casual_sum = cas_df["casual_sum"].sum()
        st.metric(label="Total Casual", value=f"{total_casual_sum:,.0f}")

with tab2:

    # Menghitung total casual dan registered
    total_casual = days_df['casual'].sum()
    total_registered = days_df['registered'].sum()

    # Membuat data untuk pie plot
    data = [total_casual, total_registered]
    labels = ['Casual', 'Registered']
    colors = ["#FF9999", "#66B3FF"]
    explode = (0.1, 0) 

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(data, labels=labels, autopct='%1.1f%%', explode=explode, shadow=True, startangle=140, colors=colors)

    ax.axis('equal')
    ax.set_title('Perbandingan Customer Registered dan Casual', fontsize=30)

    # Menampilkan pie chart 
    st.pyplot(fig)

with tab3:
    st.subheader("Jam dengan Banyak dan Sedikit Penyewa Sepeda")

    sum_order_items_df = hours_df.groupby("hours")["count_total"].sum().sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(25, 10))

    # Barplot untuk penyewa sepeda terbanyak
    sns.barplot(
        x="hours",
        y="count_total",
        data=sum_order_items_df.head(5),
        palette=["#FF9999", "#FF9999", "#66B2FF", "#FF9999", "#FF9999"],
        ax=ax[0]
    )

    ax[0].set_xlabel("Hours (PM)", fontsize=25)
    ax[0].set_title("Jam dengan Banyak Penyewa Sepeda", loc="center", fontsize=25)
    ax[0].tick_params(axis='y', labelsize=20)
    ax[0].tick_params(axis='x', labelsize=20)

    # Barplot untuk penyewa sepeda terdikit
    sns.barplot(
        x="hours",
        y="count_total",
        data=sum_order_items_df.sort_values(by="hours").head(5),
        palette=["#FF9999", "#FF9999", "#FF9999", "#FF9999", "#FFD700"],
        ax=ax[1]
    )

    ax[1].set_xlabel("Hours (AM)", fontsize=25)
    ax[1].set_title("Jam dengan Sedikit Penyewa Sepeda", loc="center", fontsize=25)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].tick_params(axis='y', labelsize=20)
    ax[1].tick_params(axis='x', labelsize=20)

    st.pyplot(fig)

with tab4:
    colors = ["#FF9999", "#66B3FF", "#99FF99", "#FFCC99"]
    season_counts = main_df_hour.groupby('season')['count_total'].sum()
    fig, ax = plt.subplots(figsize=(15, 8))

    wedges, texts, autotexts = ax.pie(
        season_counts, 
        labels=season_counts.index, 
        autopct='%1.1f%%', 
        startangle=90,
        colors=colors, 
        textprops={'fontsize': 18, 'color': 'black'},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1, 'alpha': 0.8},
        shadow=True
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(20)
        autotext.set_fontweight('bold')

    ax.set_title("Grafik Penyewaan Sepeda By Season", fontsize=30, loc="center", pad=20)

    plt.tight_layout()

    st.pyplot(fig)
