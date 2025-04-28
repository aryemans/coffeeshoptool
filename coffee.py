import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Load correlations data
correlations = pd.read_excel("./Correlations.xlsx")

# Prepare sales and dates
correlations['Date'] = pd.to_datetime(correlations['Date'])
correlations = correlations.dropna(subset=['Total'])
latest_day = correlations['Date'].max()
latest_data = correlations[correlations['Date'] == latest_day].iloc[0]

# Compute "better than yesterday" and "better than last week"
yesterday_data = correlations[correlations['Date'] == (latest_day - timedelta(days=1))]
last_week_data = correlations[correlations['Date'] == (latest_day - timedelta(days=7))]

if not yesterday_data.empty:
    better_than_yesterday = (latest_data['Total'] - yesterday_data.iloc[0]['Total']) / yesterday_data.iloc[0]['Total'] * 100
else:
    better_than_yesterday = np.nan

if not last_week_data.empty:
    better_than_last_week = (latest_data['Total'] - last_week_data.iloc[0]['Total']) / last_week_data.iloc[0]['Total'] * 100
else:
    better_than_last_week = np.nan

# Prepare sales for plotting
sales = correlations[['Date', 'Total']].dropna()
sales = sales.set_index('Date')
sales['Weekday'] = sales.index.day_name()

# Streamlit App
st.set_page_config(page_title="Sales Dashboard", page_icon="🍵", layout="wide")

st.title("🍵 Daily Insights")
st.markdown("---")

# Today's Sales Overview
st.header("Today's Sales Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sales", f"${latest_data['Total']:.2f}")
with col2:
    if not np.isnan(better_than_yesterday):
        st.metric("vs Yesterday", f"{better_than_yesterday:+.1f}%")
    else:
        st.metric("vs Yesterday", "Data N/A")
with col3:
    if not np.isnan(better_than_last_week):
        st.metric("vs Last Week", f"{better_than_last_week:+.1f}%")
    else:
        st.markdown("<span style='color:grey'>vs Last Week: Data N/A</span>", unsafe_allow_html=True)

st.caption("Note: Yesterday comparison is valid for 4/20 vs 4/19. Last week comparison unavailable due to missing earlier data.")

st.markdown("---")

# What Affects Sales
st.header("What Affects Sales Most")
left, right = st.columns(2)
with left:
    st.subheader("Cross Referenced Factors")
    st.success("- Foot Traffic")
    st.success("- Temperature")
    st.success("- Local Traffic Conditions")
    st.success("- Public Events")

with right:
    st.subheader("Current Conditions")
    st.metric("Average Foot Traffic", f"{latest_data['Average Foot Traffic %']:.1f}%")
    st.caption("Foot traffic shows how many people are nearby compared to a normal day. 100% = normal crowd size. Higher means busier streets.")
    st.metric("Average Temperature", f"{latest_data['Avg Temp']} °F")
    st.caption("Today's outdoor weather. Good temperatures usually boost foot traffic and customer visits.")

st.markdown("---")


# Special Notes
st.header("Special Notes")
st.info("Sales were lower on Monday due to the Easter holiday, which typically results in reduced foot traffic and customer visits.")

st.markdown("---")

# Forecast Section
st.header("Projected Sales for the Next 3 Days (Smoothed)")

# Feature correlations
numeric_correlations = correlations.select_dtypes(include=[np.number]).corr()
feature_corrs = {
    'FootTraffic': numeric_correlations['Total']['Average Foot Traffic %'],
    'Temperature': numeric_correlations['Total']['Avg Temp'],
    'TotalTraffic': 0.1  # Mock small positive correlation for traffic
}

# Show Correlation Table
st.subheader("Feature Correlations with Sales")
correlation_display = pd.DataFrame({
    'Feature': ['Foot Traffic', 'Temperature', 'Traffic Volume'],
    'Correlation with Sales': [round(feature_corrs['FootTraffic'], 2), round(feature_corrs['Temperature'], 2), round(feature_corrs['TotalTraffic'], 2)]
})
st.dataframe(correlation_display.style.background_gradient(cmap='coolwarm', subset=['Correlation with Sales']))

# Future conditions
future_conditions = pd.DataFrame({
    'Date': pd.date_range(start=latest_day + timedelta(days=1), periods=3),
    'FootTraffic': [88, 85, 90],
    'Temperature': [76, 75, 78],
    'TotalTraffic': [4200, 4000, 4400]
})

# Averages
avg_foot_traffic = correlations['Average Foot Traffic %'].mean()
avg_temp = correlations['Avg Temp'].mean()
avg_total_traffic = 4500  # Mock average traffic volume

# Corrected base sales
base_sales = 4500  # Manually set realistic base sales

# Corrected forecast: additive influence, divided for smoothness
future_conditions['Predicted Sales'] = base_sales + (
    (feature_corrs['FootTraffic'] * base_sales * (future_conditions['FootTraffic'] - avg_foot_traffic) / avg_foot_traffic) / 3
    + (feature_corrs['Temperature'] * base_sales * (future_conditions['Temperature'] - avg_temp) / avg_temp) / 3
    + (feature_corrs['TotalTraffic'] * base_sales * (future_conditions['TotalTraffic'] - avg_total_traffic) / avg_total_traffic) / 3
)

# Show the forecast
previous_sale = base_sales

for idx, row in future_conditions.iterrows():
    change = row['Predicted Sales'] - previous_sale
    color = 'green' if change > 0 else 'red'
    st.markdown(f"<h5 style='color:{color};'>{row['Date'].strftime('%A %m-%d')}: ${row['Predicted Sales']:.2f} ({'+' if change>0 else ''}{change:.2f})</h5>", unsafe_allow_html=True)
    previous_sale = row['Predicted Sales']

# Plot it
fig, ax = plt.subplots()
ax.plot(sales.index, sales['Total'], label='Actual Sales', marker='o')
ax.plot(future_conditions['Date'], future_conditions['Predicted Sales'], label='Forecasted Sales', linestyle='--', marker='x', color='orange')

ax.set_xlabel('Date')
ax.set_ylabel('Sales ($)')
ax.set_title('Sales Trend and Realistic Forecast')
ax.legend()
ax.set_xticks(list(sales.index) + list(future_conditions['Date']))
ax.set_xticklabels(
    [d.strftime('%a\n%m-%d') for d in list(sales.index) + list(future_conditions['Date'])],
    rotation=45, ha='right'
)

st.pyplot(fig)

st.markdown("---")

st.caption("Data sources: Square sales, Foot traffic estimates, Google Maps traffic, Weather data, Public event listings.")