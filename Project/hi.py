import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Safe Route BD",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
# Injecting custom CSS for a more polished look.
st.markdown("""
<style>
    /* Clean up the main layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Style the metric labels */
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #4B5563; /* Gray-600 */
    }
    /* Custom justification card styling */
    .justification-card {
        padding: 1.25rem;
        border-radius: 0.5rem;
        background-color: #F9FAFB; /* Gray-50 */
        border-left: 5px solid;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Mock Data Generation (Bangladesh Context) ---
# In a real app, this data would come from your backend/database.
def generate_mock_heatmap_data(lat, lon):
    """Generates random data points around a central coordinate for the heatmap."""
    num_points = 350
    np.random.seed(42)
    lats = np.random.normal(loc=lat, scale=0.03, size=num_points)
    lons = np.random.normal(loc=lon, scale=0.04, size=num_points)
    # Weights simulate crime intensity
    weights = np.random.randint(1, 15, size=num_points)
    return list(zip(lats, lons, weights))

def get_mock_route_suggestion(destination, age, gender, current_time):
    """Generates a mock route suggestion based on inputs, with a Dhaka context."""
    hour = current_time.hour
    if hour > 21 or hour < 6: # Night time in Dhaka
        return {
            "name": "Route via Hatirjheel Expressway",
            "description": "This route is recommended for late-night travel. It is well-lit, consistently monitored, and has steady traffic flow, which generally reduces risks.",
            "risk_level": "Low",
            "eta": "22 minutes",
            "color": "#10B981" # Green
        }
    else: # Day time
        return {
            "name": "Direct Route via Mohakhali",
            "description": "This is the most direct route but passes through heavily congested areas. While generally safe during the day, be mindful of valuables in crowded spots.",
            "risk_level": "Moderate",
            "eta": "28 minutes",
            "color": "#F59E0B" # Amber/Orange
        }

# --- UI Components ---

# --- Sidebar ---
with st.sidebar:
    st.image("https://placehold.co/300x100/8B5CF6/FFFFFF?text=SafeRoute+BD&font=raleway", use_column_width=True)
    st.markdown("<h2 style='text-align: center; font-weight: 300;'>Trip Planner</h2>", unsafe_allow_html=True)
    st.info("Provide your details to find the safest route in Dhaka.", icon="💡")
    
    # Input fields
    destination_input = st.text_input("📍 Destination", placeholder="e.g., Gulshan 1, Dhaka")
    age_input = st.number_input("👤 Your Age", min_value=1, max_value=120, value=25, step=1)
    gender_input = st.selectbox("⚧️ Your Gender", ["Female", "Male", "Other", "Prefer not to say"])
    
    # Time is automatically fetched
    current_time = datetime.now()
    st.write(f"🕒 **Time:** `{current_time.strftime('%I:%M %p')}`")

    find_route_button = st.button("Find Safest Route", type="primary", use_container_width=True)


# --- Main Content Area ---
st.title("🛡️ Safe Route Dashboard")
st.markdown("An AI-powered tool to navigate Dhaka more safely.")

if not find_route_button:
    st.info("Enter your destination in the sidebar and click 'Find Safest Route' to begin.", icon="👈")

if find_route_button and not destination_input:
    st.error("Please enter a destination location to proceed.")

# Use columns for the main layout
col1, col2 = st.columns([5, 4]) # Give map a bit more space

# --- Left Column: Map ---
with col1:
    with st.container(border=True, height=600):
        st.subheader("🗺️ Crime Hotspot Heatmap")
        
        # Default map center for Dhaka, Bangladesh
        map_center = [23.8103, 90.4125]
        
        m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB positron")

        if find_route_button and destination_input:
            with st.spinner("Generating crime heatmap..."):
                heatmap_data = generate_mock_heatmap_data(map_center[0], map_center[1])
                folium.plugins.HeatMap(heatmap_data, radius=15).add_to(m)
            st.success(f"Displaying crime hotspots around **{destination_input}**.", icon="✅")
        
        st_folium(m, use_container_width=True, height=480)

# --- Right Column: Route Suggestion ---
with col2:
    with st.container(border=True, height=600):
        st.subheader("🚦 Suggested Route")
        
        if find_route_button and destination_input:
            with st.spinner('Analyzing routes...'):
                route = get_mock_route_suggestion(destination_input, age_input, gender_input, current_time)
                
                st.markdown(f"### {route['name']}")

                # Display metrics side-by-side
                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric(label="Calculated Risk Level", value=route['risk_level'])
                metric_col2.metric(label="Estimated Arrival Time", value=route['eta'])
                
                # Display justification in a styled card
                st.markdown(f"""
                <div class="justification-card" style="border-color: {route['color']};">
                    <p style="font-weight: bold; margin-bottom: 0.5rem;">Route Analysis:</p>
                    <p style="margin: 0;">{route['description']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Placeholder content
            st.markdown("<div style='display: flex; flex-direction: column; justify-content: center; align-items: center; height: 400px; text-align: center; color: #9CA3AF;'> <p style='font-size: 1.5rem;'>📊</p> <p>Your route analysis will appear here.</p> </div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'><i>Disclaimer: This is a demo application using mock data for Dhaka. Always prioritize personal safety and be aware of your surroundings.</i></p>", unsafe_allow_html=True)

