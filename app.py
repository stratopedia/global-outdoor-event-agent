import streamlit as st
import json
import pandas as pd
from weather_agent_node import fetch_city_weather_tool, GlobalEventPlannerAgent

# Streamlit Page Config
st.set_page_config(
    page_title="Global Outdoor Event Planner Agent",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Outdoor Event Planner Agent")
st.caption("AI Agent Tooling & Real-time Weather Telemetry Evaluation for Outdoor Events")

st.markdown("---")

# Sidebar Controls
st.sidebar.header("🎯 Event Parameters & City Selector")
selected_cities = st.sidebar.multiselect(
    "Select Cities to Analyze:",
    options=[
        "Tokyo", "Bengaluru", "San Francisco", "London", "Barcelona",
        "Sydney", "Singapore", "New York", "Paris", "Berlin", "Dubai"
    ],
    default=["Bengaluru", "Tokyo", "Barcelona", "San Francisco"]
)

custom_city = st.sidebar.text_input("...or add a custom city on the fly:")
if custom_city and custom_city not in selected_cities:
    selected_cities.append(custom_city)

# Run Agent Button
if st.button("🚀 Run Weather Agent Check", type="primary"):
    if not selected_cities:
        st.warning("Please select at least one city.")
    else:
        with st.spinner("🤖 Agent executing tool calls across global hubs..."):
            agent = GlobalEventPlannerAgent(target_cities=selected_cities)
            result = agent.execute_workflow()

        st.subheader("📌 Agent Recommendation Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Cities Analyzed", result["total_analyzed"])
        col2.metric("Shortlisted Venues", result["shortlisted_count"])
        col3.metric("Pass Rate", f"{(result['shortlisted_count']/result['total_analyzed'])*100:.0f}%")

        if result["top_candidates"]:
            st.success(f"✅ **Recommended Host Cities:** {', '.join(result['top_candidates'])}")
        else:
            st.error("❌ No cities currently meet the outdoor event criteria.")

        st.markdown("---")
        st.subheader("📊 Detailed Telemetry Breakdown")
        
        # Convert Telemetry to DataFrame for clean interactive table
        df = pd.DataFrame(result["detailed_telemetry"])
        
        # Re-order and rename columns
        if not df.empty and "error" not in df.columns:
            st.dataframe(
                df[[
                    "city", "temperature_celsius", "precipitation_mm", 
                    "wind_speed_kmh", "condition", "outdoor_event_suitable", "recommendation_reason"
                ]],
                use_container_width=True
            )
        
        with st.expander("🔍 View Raw Agent JSON Output Payload"):
            st.json(result)