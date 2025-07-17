import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Title
st.title("🌍 COVID-19 Data Dashboard")

# Load Data
@st.cache_data
def load_data():
    cases = pd.read_csv("data/time_series_covid19_confirmed_global.csv")
    vacc = pd.read_csv("data/vaccinations.csv")
    return cases, vacc

cases_df, vacc_df = load_data()

# Preprocess cases
cases_long = cases_df.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                           var_name="Date", value_name="Confirmed")
cases_long["Date"] = pd.to_datetime(cases_long["Date"])
cases_grouped = cases_long.groupby(['Country/Region', 'Date'])['Confirmed'].sum().reset_index()

# Preprocess vaccinations
vacc_df = vacc_df[["location", "date", "total_vaccinations"]]
vacc_df = vacc_df.rename(columns={"location": "Country/Region", "date": "Date"})
vacc_df["Date"] = pd.to_datetime(vacc_df["Date"])

# Merge datasets
merged = pd.merge(cases_grouped, vacc_df, on=["Country/Region", "Date"], how="inner")

# Sidebar Country Selection
country = st.sidebar.selectbox("Select a Country", merged["Country/Region"].unique())

# Country Data
data = merged[merged["Country/Region"] == country]

# 📌 Summary Metrics
st.subheader(f"📌 Summary Metrics for {country}")
latest = data[data["Date"] == data["Date"].max()]
# 📌 Summary Metrics (Safe Handling)
confirmed = int(latest["Confirmed"].values[0]) if not pd.isna(latest["Confirmed"].values[0]) else 0
vaccinated = int(latest["total_vaccinations"].values[0]) if not pd.isna(latest["total_vaccinations"].values[0]) else 0

col1, col2 = st.columns(2)
col1.metric("Confirmed Cases", f"{confirmed:,}")
col2.metric("Total Vaccinations", f"{vaccinated:,}")

# 📈 Line Plot - Cases vs Vaccinations
st.subheader(f"📈 {country} - Confirmed Cases vs. Total Vaccinations")
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(data["Date"], data["Confirmed"], label="Confirmed Cases", color='blue')
ax.plot(data["Date"], data["total_vaccinations"], label="Total Vaccinations", color='green')
ax.set_xlabel("Date")
ax.set_ylabel("Count")
ax.legend()
st.pyplot(fig)

# 🌍 Top 10 Countries Bar Chart
st.subheader("🌍 Top 10 Countries by Total Confirmed Cases")
latest_date = cases_grouped["Date"].max()
latest_data = cases_grouped[cases_grouped["Date"] == latest_date]
top10 = latest_data.sort_values(by="Confirmed", ascending=False).head(10)

st.dataframe(top10[["Country/Region", "Confirmed"]])
fig2, ax2 = plt.subplots(figsize=(10,5))
ax2.barh(top10["Country/Region"], top10["Confirmed"], color="crimson")
ax2.set_xlabel("Confirmed Cases")
ax2.set_title(f"Top 10 Countries as of {latest_date.date()}")
ax2.invert_yaxis()
st.pyplot(fig2)

# 🗺️ World Map with Plotly
st.subheader("🗺️ Global COVID-19 Case Map")
map_df = latest_data.copy()
map_df = map_df.rename(columns={"Country/Region": "Country"})
fig3 = px.choropleth(map_df,
                     locations="Country",
                     locationmode="country names",
                     color="Confirmed",
                     hover_name="Country",
                     color_continuous_scale="Reds",
                     title="Total Confirmed Cases by Country")
st.plotly_chart(fig3)
# 🌐 Stylish Footer with GitHub
st.markdown("""
<hr style='border:1px solid #f0f0f0' />

<div style="text-align:center; padding:10px; font-size:14px; color:gray;">
    © 2025 | Made with ❤️ by <b>Ahmad Talha Abid</b><br>
    🔗 <a href="https://github.com/mrahmadtalha" target="_blank">GitHub: mrahmadtalha</a><br>
    📊 Data Source: Johns Hopkins University & Our World in Data
</div>
""", unsafe_allow_html=True)

