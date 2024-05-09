import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import geopandas as gpd

def create_city_df(geo_df):
    city_df = geo_df.groupby(by=['City', 'Region', 'Country']).agg({
    'IP': 'count'
    }).sort_values(by='IP', ascending=False)

    return city_df

def create_geo_df(geo_df):
    geo_df = geo_df
    latitude_df = []
    longitude_df = []

    for coordinate in geo_df['Coordinate']:
        if pd.notna(coordinate):
            loc = str(coordinate).split(',')
            latitude_df.append(loc[0])
            longitude_df.append(loc[1])
        else:
            latitude_df.append(np.nan)
            longitude_df.append(np.nan)

    geo_df['Latitude'] = latitude_df
    geo_df['Longitude'] = longitude_df

    geo_df.dropna()

    return geo_df

def create_main_df(main_df):
    main_df = main_df

    main_df.rename(columns={
    "No.": "Count_id"
    }, inplace=True)

    rounded_time = main_df["Time"].apply(lambda x: int(round(x)))
    main_df["Time"] = rounded_time

    return main_df

def create_source_df(main_df):
    main_df = main_df[main_df['Filter'] == True]

    source_df = main_df.groupby(by=["Source"]).agg({
    "Count_id": "count",
    }).sort_values(by="Count_id", ascending=False)

    return source_df

def create_protocol_df(main_df):
    main_df = main_df[main_df['Filter'] == True]

    protocol_df = main_df.groupby(by=["Protocol"]).agg({
    "Count_id": "count"
    }).sort_values(by="Count_id", ascending=False)
    return protocol_df

def create_per_second_df(main_df):
    main_df["Time"] = pd.to_datetime(main_df["Time"], unit='s')
    main_df = main_df.sort_values("Time")

    per_second_df = main_df.groupby(by="Time").agg({
        "Count_id": "count"
    }).sort_index()

    return per_second_df

main_df = pd.read_csv("mergeWednesday.csv")
geo_df = pd.read_csv("geolocation_data.csv")

main_df = create_main_df(main_df)
city_df = create_city_df(geo_df)
geo_df = create_geo_df(geo_df)

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]



st.header("Data Communication and Computer Networking Project")

st.write("- 2210511050 Adrian Fakhriza Hakim")
st.write("- 2210511052 Widya Amellia Putri")
st.write("- 2210511057 Nicolas Debrito")
st.write("- 2210511072 Edwina Martha Putri")

tab1, tab2 = st.tabs(["Traffic Analisis", "Geo Analisis"])

min_second = main_df["Time"].min()
max_second = main_df["Time"].max()

with tab1:
    st.header("Traffic Analisis")

    start_second, end_second = st.slider('Enter Time (start-end)', value=(min_second, max_second))
    
    filter_df = (main_df['Time'] >= start_second) & (main_df['Time'] <= end_second)
    
    main_df['Filter'] = filter_df

    st.subheader("Most Requests from IP Source")
    
    source_df = create_source_df(main_df)

    top_source_df = source_df.sort_values(by="Count_id", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        total_request = top_source_df.sum()
        st.metric("Total Request", value=total_request)

    with col2:
        highest_request = top_source_df.max()
        st.metric("Highest Request Amount", value=highest_request)
    
    plt.figure(figsize=(10, 5))

    sns.barplot(
        y="Count_id", 
        x="Source",
        data=top_source_df[:5].sort_values(by="Count_id", ascending=False),
        palette=colors
    )

    plt.title("Most Requests from IP Source", loc="center", fontsize=15)
    plt.ylabel("Total Request")
    plt.xlabel("IP Source")
    plt.tick_params(axis='x', labelsize=12)
    
    st.pyplot(plt)

    st.subheader("Highest number of sent protocols")

    protocol_df = create_protocol_df(main_df)

    top_protocol_df = protocol_df.sort_values(by="Count_id", ascending=False)

    plt.figure(figsize=(10, 5))

    sns.barplot(
        y="Count_id", 
        x="Protocol",
        data=top_protocol_df[:3].sort_values(by="Count_id", ascending=False),
        palette=colors
    )

    plt.title("Highest number of sent protocols", loc="center", fontsize=15)
    plt.ylabel("Total Protocol")
    plt.xlabel("Protocol")
    plt.tick_params(axis='x', labelsize=12)
    
    st.pyplot(plt)

    st.subheader('Number of requests per second')

    per_second_df = create_per_second_df(main_df)
    
    plt.figure(figsize=(10, 5))
    plt.plot_date(per_second_df.index, per_second_df["Count_id"], fmt='o-', color="#72BCD4")

    plt.title("Number of requests per second", loc='center', fontsize=20)
    plt.xlabel("Second")
    plt.ylabel("Total Request")
    plt.xticks(fontsize=0)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    
    st.pyplot(plt)

    st.subheader('Package Information Details')

    reference_datetime = pd.Timestamp("1970-01-01 00:00:00")

    main_df["Time"] = (main_df["Time"] - reference_datetime).dt.total_seconds()

    main_df.rename(columns={
    "Count_id": "Jumlah Permintaan"
    }, inplace=True)

    paket_df = main_df.groupby(by=["Time", "Source", "Destination", "Protocol", "Length"]).agg({
    "Jumlah Permintaan": "count"
    })

    st.write(paket_df)


with tab2:
    st.header("Geo Analisis")
    st.subheader("Most IP Source locations")

    city_df.rename(columns={
    "IP": "Jumlah IP"
    }, inplace=True)

    sorted_city_df = city_df.sort_values(by="Jumlah IP", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        total_city = geo_df["City"].nunique()
        st.metric("Total City", value=total_city)

    with col2:
        highest_request = geo_df['City'].value_counts().idxmax()
        st.metric("Highest Request City", value=highest_request)

    plt.figure(figsize=(10, 5))


    sns.barplot(
        y="Jumlah IP", 
        x="City",
        data=sorted_city_df[:5],
        palette=colors
    )

    plt.title("Most IP Source locations", loc="center", fontsize=15)
    plt.ylabel("Total IP")
    plt.xlabel("City")
    plt.tick_params(axis='x', labelsize=12)

    st.pyplot(plt)

    st.subheader('Peta Persebaran IP Source')

    geometry = gpd.points_from_xy(geo_df['Longitude'], geo_df['Latitude'])
    gdf = gpd.GeoDataFrame(geo_df, geometry=geometry)

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(figsize=(10, 6), color='lightgrey')
    gdf.plot(ax=ax, color='red', marker='o', markersize=1)
    plt.title('IP Source IPv4 Location Point Map')
    
    st.pyplot(plt)
