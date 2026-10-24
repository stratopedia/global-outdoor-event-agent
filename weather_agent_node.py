import os
import requests
from typing import List, Dict, Any
from dataclasses import dataclass

# ==========================================
# 1. State & Data Models (Pydantic / Dataclass)
# ==========================================
@dataclass
class WeatherReport:
    city: str
    temperature_celsius: float
    precipitation_mm: float
    wind_speed_kmh: float
    condition: str
    outdoor_event_suitable: bool
    recommendation_reason: str

# ==========================================
# 2. Tool Definition (Decorated / Standalone)
# ==========================================
def fetch_city_weather_tool(city_name: str) -> Dict[str, Any]:
    """
    Tool: Queries global meteorological telemetry via Open-Meteo API 
    to analyze micro-climates for outdoor event viability.
    """
    # Geocoding resolution
    geo_endpoint = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    geo_response = requests.get(geo_endpoint).json()
    
    if not geo_response.get("results"):
        return {"city": city_name, "error": "Location metadata lookup failed."}
        
    loc = geo_response["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    country_tag = loc.get("country", "Global")

    # Meteorological telemetry fetch
    weather_endpoint = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
    )
    w_data = requests.get(weather_endpoint).json().get("current", {})

    temp = w_data.get("temperature_2m", 0.0)
    precip = w_data.get("precipitation", 0.0)
    wind = w_data.get("wind_speed_10m", 0.0)
    w_code = w_data.get("weather_code", 0)

    # Condition synthesis
    condition = "Clear / Sunny" if w_code <= 2 else "Overcast" if w_code <= 3 else "Active Precipitation"
    
    # Deterministic evaluation heuristics for outdoor events
    is_suitable = (precip == 0.0) and (16.0 <= temp <= 27.0) and (wind < 20.0)
    
    reason = (
        "Optimal outdoor conditions: Comfortable temperature, zero rain risk, calm winds."
        if is_suitable
        else f"Flagged: Temp ({temp}°C), Precip ({precip}mm), or Wind ({wind}km/h) outside safe event tolerances."
    )

    return {
        "city": f"{city_name}, {country_tag}",
        "temperature_celsius": temp,
        "precipitation_mm": precip,
        "wind_speed_kmh": wind,
        "condition": condition,
        "outdoor_event_suitable": is_suitable,
        "recommendation_reason": reason
    }

# ==========================================
# 3. Agent Orchestrator Node
# ==========================================
class GlobalEventPlannerAgent:
    """
    Orchestration agent designed to evaluate multi-city operational parameters 
    for large-scale outdoor gatherings.
    """
    def __init__(self, target_cities: List[str]):
        self.target_cities = target_cities

    def execute_workflow(self) -> Dict[str, Any]:
        print(f"🌍 [Agent Orchestrator]: Initializing sweep across {len(self.target_cities)} global target hubs...")
        
        evaluated_reports: List[Dict[str, Any]] = []
        shortlisted_venues: List[str] = []

    
        for city in self.target_cities:
            print(f"   -> Invoking tool: fetch_city_weather_tool for '{city}'...")
            report = fetch_city_weather_tool(city)
            evaluated_reports.append(report)
            
            if report.get("outdoor_event_suitable"):
                shortlisted_venues.append(report["city"])

        # for city in self.target_cities:
        #     print(lambda: f"   -> Invoking tool: fetch_city_weather_tool for '{city}'...")()
        #     report = fetch_city_weather_tool(city)
        #     evaluated_reports.append(report)
            
        #     if report.get("outdoor_event_suitable"):
        #         shortlisted_venues.append(report["city"])

        return {
            "status": "success",
            "total_analyzed": len(self.target_cities),
            "shortlisted_count": len(shortlisted_venues),
            "top_candidates": shortlisted_venues,
            "detailed_telemetry": evaluated_reports
        }

# ==========================================
# 4. Execution Entrypoint
# ==========================================
if __name__ == "__main__":
    global_hubs = ["Tokyo", "Bengaluru", "San Francisco", "Reykjavik", "Singapore"]
    
    agent = GlobalEventPlannerAgent(target_cities=global_hubs)
    result_payload = agent.execute_workflow()

    # Pretty-print final agent payload response
    import json
    print("\n📦 === Final Agent Execution Output Payload ===")
    print(json.dumps(result_payload, indent=4))