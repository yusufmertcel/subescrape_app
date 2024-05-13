import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import json
from yolcu360_main import Main
from datetime import datetime
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Yolcu360 Dashboard", page_icon="🚗", layout="wide")

st.title(" :bar_chart: Yolcu360 Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

with open("app/garenta_sube.json", "r") as f:
    loc_dict = json.load(f)


fl = st.file_uploader(":file_folder: Upload a file", type=["csv","xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write(f"Filename: {filename}")
    xl = pd.ExcelFile(fl)
    sheet_names = xl.sheet_names
    if "1 Gunluk" in sheet_names:
        df_one = pd.read_excel(fl, sheet_name="1 Gunluk")
    else:
        df_one = pd.read_excel(fl, sheet_name=0)
    if "7 Gunluk" in sheet_names:
        df_seven = pd.read_excel(fl, sheet_name="7 Gunluk")
    else:
        df_seven = pd.read_excel(fl, sheet_name=0)
    if "30 Gunluk" in sheet_names:
        df_thirty = pd.read_excel(fl, sheet_name="30 Gunluk")
    else:
        df_thirty = pd.read_excel(fl, sheet_name=0)
else:
    files = os.listdir("./app")
    file = [idx for idx in files if idx.lower().endswith(".xlsx")][0]
    print(file)
    try:
        df_one = pd.read_excel("app/"+file, sheet_name="1 Gunluk")
        df_seven = pd.read_excel("app/"+file, sheet_name="7 Gunluk")
        df_thirty = pd.read_excel("app/"+file, sheet_name="30 Gunluk")
    except ValueError:
        df_one = pd.read_excel("app/"+file, sheet_name=0)
        df_seven = pd.read_excel("app/"+file, sheet_name=1)
        df_thirty = pd.read_excel("app/"+file, sheet_name=2)

#Sidebar
def click_button(lvhour, lvday, lvloc_name, lvfname, cols):
    st.session_state.clicked = True
    main_obj = Main("dashboard", lvhour, lvday)
    try:
        df_one, df_seven, df_thirty =  main_obj.main(lvloc_name, lvfname)
        df = pd.concat([df_one, df_seven, df_thirty], ignore_index=True)
    except ValueError:
        st.sidebar.write("Aradığınız tarih ve şubede kiralık araç bulunamamıştır.")
        #print(df_one.head())
        #print(df_seven.head())
        #print(df_thirty.head())
        df = pd.DataFrame([], columns=cols)
    return df_one, df_seven, df_thirty, df

df = pd.concat([df_one, df_seven, df_thirty], ignore_index=True)
columns = df.columns
# arayüzden saat, gün, lokasyon, seçimi yapılacak

# Price Range
col1, col2 = st.columns((2))
startPrice = df["price_amount"].min()
endPrice = df["price_amount"].max()

with col1:
    price1 = st.number_input(label="Start Price", min_value=0, max_value=int(endPrice), step=1000)

with col2:
    price2 = st.number_input(label="End Price", value=int(endPrice), min_value=int(price1), max_value=int(endPrice)*10, step=1000)

df_filtered = df[(df["price_amount"] >= price1) & (df["price_amount"] <= price2)].copy()





#hour = st.sidebar.number_input('Kaç saat sonrasindan baslamak istiyorsunuz? En az 2 saat sonrasını seçmelisiniz.', step=1, min_value=2, max_value=24)
date = datetime.now()
date = st.sidebar.date_input("Araç kiralayacağınız günü seçiniz?", date)
hour = date.hour()
day = date.day
#day = st.sidebar.number_input('Kaç gün sonrasından baslamak istiyorsunuz? Aynı gün için 0 yazmalısınız.', step=1, min_value=0, max_value=30)
loc_name = st.sidebar.selectbox('Hangi lokasyon için veri görmek istersiniz?', list(loc_dict.keys()), placeholder="Default")
filename = st.sidebar.text_input("Dosya Adı", value="yolcu360.xlsx")
btn = st.sidebar.button('Ara')
st.sidebar.write(btn)

if btn:
    df_one, df_seven, df_thirty, df = click_button(hour, day, loc_name, filename, columns)
    df_filtered = df[(df["price_amount"] >= price1) & (df["price_amount"] <= price2)].copy()

st.sidebar.header("Choose your filter: ")
# Filter vendor
vendor = st.sidebar.multiselect("Vendor", df_filtered["vendor"].unique())
if vendor:
    df_filtered = df_filtered[df_filtered["vendor"].isin(vendor)]
    if not df_one.empty:
        df_one = df_one[df_one["vendor"].isin(vendor)]
    if not df_seven.empty:
        df_seven = df_seven[df_seven["vendor"].isin(vendor)]
    if not df_thirty.empty:
        df_thirty = df_thirty[df_thirty["vendor"].isin(vendor)]

# Filter brand
brand = st.sidebar.multiselect("Brand", df_filtered["brand"].unique())
if brand:
    df_filtered = df_filtered[df_filtered["brand"].isin(brand)]
    if not df_one.empty:
        df_one = df_one[df_one["brand"].isin(brand)]
    if not df_seven.empty:
        df_seven = df_seven[df_seven["brand"].isin(brand)]
    if not df_thirty.empty:
        df_thirty = df_thirty[df_thirty["brand"].isin(brand)]


#Dataframe
tab0, tab1, tab2, tab3 = st.tabs(["Tüm Araçlar", "1 Günlük", "7 Günlük", "30 Günlük"])

with tab0:
    st.write("Tüm Araçlar")
    st.dataframe(df_filtered)

with tab1:
    st.write("1 Günlük")
    st.dataframe(df_one)


with tab2:
    st.write("7 Günlük")
    st.dataframe(df_seven)


with tab3:
    st.write("30 Günlük")
    st.dataframe(df_thirty)


#Graphs
st.header("Graphs")
day_interval = st.selectbox("Kaç Günlük Kiralama?", [1,7,30], key="graph")
df_filtered_graph = df_filtered[df_filtered["period"] == day_interval]
fig = px.bar(df_filtered_graph, x='vendor', y='price_amount', color='brand', text="sippCode", barmode='group', title="Price Amount by Vendor and Brand")
st.plotly_chart(fig, theme="streamlit", use_container_width=True)