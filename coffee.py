import streamlit as st
import datetime
import time
import random
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Coffee Shop Sales Dashboard", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #fcfcf9;}
    .block-container {padding-top: 2rem;}
    h1, h2, h3, h4, h5, h6 {color: #2e2e2e;}
    .big-font {font-size:28px !important; color: #4B3F72; font-weight: bold;}
    .section-title {
        font-size:24px !important;
        color: #ec6f66;
        background-color: #fff2ec;
        padding: 0.5rem;
        border-radius: 8px;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .data-check-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }
    .data-check {
        font-size:17px;
        color: #333;
        background-color: #fdf2ec;
        padding: 0.5rem 0.8rem;
        border-left: 4px solid #ec6f66;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .highlight {
        color: #4a90e2;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOCK SALES + SIGNAL DATA FOR TODAY ---
def get_sales_past_week():
    return [312, 289, 265, 350, 299, 330, 280]

def get_today_sales():
    now = datetime.datetime.now()
    hours_open = list(range(6, now.hour + 1))
    total = 0
    for hour in hours_open:
        total += random.randint(10, 35) * random.uniform(3.5, 6.0)
    return round(total, 2)

def get_weather(zip_code):
    return "clear", 68

def get_yelp_reviews(business_id):
    recent_reviews = [
        {"rating": 5, "text": "Incredible service and delicious muffins!"},
        {"rating": 5, "text": "The best espresso I've had in Atlanta."},
        {"rating": 4, "text": "Great vibe and friendly staff."}
    ]
    ratings = [r["rating"] for r in recent_reviews]
    avg_rating = sum(ratings) / len(ratings)
    return len(recent_reviews), avg_rating, recent_reviews

def check_instagram_activity():
    return True

def check_local_events():
    return ["Atlanta Jazz Festival", "Midtown Farmers Market"]

def check_google_trends():
    return 0.95

def check_road_closures():
    return False

def check_transit_delays():
    return False

def check_traffic_congestion():
    return False

def check_google_keyword_interest():
    return 0.87

def compare_popular_times():
    return True

def check_google_live_popularity():
    return 0.76

def get_yesterday_sales():
    return 276.34

def get_percent_change(current, previous):
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 1)



# --- PREDICTOR ENGINE ---
def predict_future_sales(weather, events, keyword_interest, popularity):
    base_sales = 300
    adjustment = 0
    if weather == "rain":
        adjustment -= 30
    if len(events) > 0:
        adjustment += 40
    if keyword_interest < 0.7:
        adjustment -= 20
    if popularity > 0.7:
        adjustment += 25
    return base_sales + adjustment

# --- INSIGHT ENGINE ---
def generate_explanations():
    explanations = []
    details = []
    sales_last_week = get_sales_past_week()
    avg_weekly_sales = sum(sales_last_week) / len(sales_last_week)
    today_sales = get_today_sales()

    weather, temp = get_weather("30308")
    review_count, avg_rating, reviews = get_yelp_reviews("mock-yelp-id")
    inst_posted = check_instagram_activity()
    local_events = check_local_events()
    trends_score = check_google_trends()
    road_closed = check_road_closures()
    transit_delays = check_transit_delays()
    traffic_congestion = check_traffic_congestion()
    keyword_interest = check_google_keyword_interest()
    local_peak_time = compare_popular_times()
    live_area_score = check_google_live_popularity()

    if today_sales < avg_weekly_sales * 0.75:
        if "rain" in weather or temp < 45:
            explanations.append(f"Rainy day with {temp}°F — likely affecting walk-ins.")
        if review_count > 0 and avg_rating < 3.5:
            explanations.append(f"Recent negative reviews (avg {avg_rating:.1f} across {review_count} reviews).")
        if not local_events:
            explanations.append("No local events — less foot traffic today.")
        if not inst_posted:
            explanations.append("No Instagram posts in over 10 days — you're off the radar.")
        if trends_score < 0.7:
            explanations.append("Searches for 'coffee near me' are down this week.")
        if road_closed:
            explanations.append("Nearby road construction could be limiting access.")
        if transit_delays:
            explanations.append("Public transit delays may be keeping commuters away.")
        if traffic_congestion:
            explanations.append("Heavy traffic in the area may reduce drive-in visits.")
        if keyword_interest < 0.6:
            explanations.append("Less search interest in coffee-related keywords today.")
        if not local_peak_time:
            explanations.append("Your sales don’t align with busy hours around the neighborhood.")
        if live_area_score < 0.4:
            explanations.append("The neighborhood is quieter than usual at this hour.")
        if not explanations:
            explanations.append("No external issues found — check internal ops or staff.")
    else:
        explanations.append("Sales are within your typical weekly range. All good!")

    details.append(f"🌤️ Weather Check: Clear skies, 68°F")
    details.append(f"💬 Customer Reviews: Avg rating = {avg_rating:.1f}, e.g., '{reviews[0]['text']}'")
    details.append(f"🎫 Local Events: {', '.join(local_events) if local_events else 'No events today'}")
    details.append("📱 Social Media: You posted recently. Customers may be seeing you online.")
    details.append(f"🔍 Google Trends: Interest level = {trends_score * 100:.0f}/100")
    details.append("🚧 Street Conditions: No known roadblocks or construction affecting your area.")
    details.append("🚆 MARTA: No reported delays or outages on local lines.")
    details.append("🚗 Traffic: Area traffic looks normal today.")
    details.append(f"📈 Google Keywords: Popularity = {keyword_interest * 100:.0f}/100")
    details.append(f"📍 Neighborhood Activity: Real-time crowd score = {live_area_score * 100:.0f}/100")

    return today_sales, avg_weekly_sales, explanations, details

# --- STATISTICAL ANALYSIS ---
def simulate_weekly_data():
    np.random.seed(42)
    data = {
        "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "sales": [312, 289, 265, 350, 299, 330, 280],
        "temp": [70, 68, 66, 65, 60, 58, 55],
        "avg_review": [4.5, 4.2, 3.8, 4.6, 4.0, 3.5, 3.2],
        "days_since_instapost": [2, 3, 4, 5, 6, 7, 8],
        "event_today": [1, 1, 0, 0, 1, 0, 0],
        "is_rainy": [0, 0, 1, 1, 1, 0, 1]
    }
    return pd.DataFrame(data)

def analyze_weekly_data(df):
    correlations = {
        "Temperature and Sales": pearsonr(df["sales"], df["temp"])[0],
        "Customer Reviews and Sales": pearsonr(df["sales"], df["avg_review"])[0],
        "Social Activity and Sales": pearsonr(df["sales"], df["days_since_instapost"])[0],
        "Event Days and Sales": pearsonr(df["sales"], df["event_today"])[0],
        "Bad Weather and Sales": pearsonr(df["sales"], df["is_rainy"])[0],
        "Google Popularity Score": 0.62,
        "Foot Traffic Score": 0.67,
        "Google Keyword Trends": 0.74
    }

    X = df[["temp"]]
    y = df["sales"]
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]
    r_squared = model.score(X, y)
    rain_impact = df[df["is_rainy"] == 1]["sales"].mean() - df[df["is_rainy"] == 0]["sales"].mean()

    summary = {
        "📌 Biggest Influence on Sales": max(correlations, key=lambda k: abs(correlations[k])),
        "🌡️ How Weather Affects Sales": f"${slope:.2f} per degree (based on temp)",
        "📈 Weather-Sales Match Quality": f"{r_squared:.2f} (higher = stronger link)",
        "🌧️ Avg Drop on Bad Weather Days": f"${rain_impact:.2f}"
    }
    return pd.DataFrame([summary]), pd.DataFrame.from_dict(correlations, orient='index', columns=["Relationship Score"])

def show_loading_screen():
    with st.spinner('Gathering real-time signals:'):
        checks = [
            "Checking local weather 🌦️",
            "Analyzing recent Yelp reviews 📊",
            "Reviewing Instagram activity 📱",
            "Scanning for nearby events 🎫",
            "Pulling Google Trends data 🔍",
            "Looking at traffic & MARTA 🚗🚆",
            "Checking live crowd score 📍"
        ]
        for check in checks:
            st.write(f"{check}...")
            time.sleep(0.3)
        st.success("All data sources analyzed!")

# --- STREAMLIT UI ---
st.title("☕ Smart Sales Insight Dashboard")

if st.button("📤 Send Square Data & Generate Insight"):
    show_loading_screen()

    sales_today, weekly_avg, explanations, details = generate_explanations()
    df_week = simulate_weekly_data()
    stats_summary, correlation_table = analyze_weekly_data(df_week)

    sales_yesterday = get_yesterday_sales()
    delta_day = get_percent_change(sales_today, sales_yesterday)
    delta_week = get_percent_change(sales_today, weekly_avg)

    col1, col2, col3 = st.columns(3)
    col1.metric("Today's Sales", f"${sales_today}", f"{delta_day:+.1f}% vs Yesterday")
    col2.metric("Weekly Avg Sales", f"${weekly_avg:.2f}", f"{delta_week:+.1f}% vs Weekly Avg")
    col3.metric("Yesterday's Sales", f"${sales_yesterday}", "")

    st.markdown("<div class='section-title'>📋 Real-Time Insights</div>", unsafe_allow_html=True)
    for e in explanations:
        st.write("-", e)


    st.markdown("<div class='section-title'>📊 Sales Patterns This Week</div>", unsafe_allow_html=True)
    st.table(stats_summary)

    st.markdown("<div class='section-title'>🔍 What Affects Sales Most?</div>", unsafe_allow_html=True)
    st.dataframe(correlation_table.style.background_gradient(cmap='coolwarm').format("{:.2f}"))

    st.markdown("<div class='section-title'>🧠 Insights on Foot Traffic and Google Data</div>", unsafe_allow_html=True)
    st.write("Google's live popularity score (currently 76/100) shows strong foot traffic around your shop. This, combined with steady search trends (95/100), suggests your location remains visible and frequented by potential customers.")

    st.markdown("<div class='section-title'>🔮 Forecast: Tomorrow's Sales Prediction</div>", unsafe_allow_html=True)
    predicted_sales = predict_future_sales("clear", ["Ponce Night Market"], 0.91, 0.83)
    st.write(f"If weather stays clear, and with events like the Ponce Night Market plus good keyword interest, your projected sales are around **${predicted_sales:.2f}**.")
