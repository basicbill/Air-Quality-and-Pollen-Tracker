#!/usr/bin/env python3
"""
Air Quality & Pollen Forecast Tracker
Collects daily air quality and pollen data, tracks forecast accuracy over time.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 11 US locations to track (airport codes for consistency)
LOCATIONS = {
    "KBIS": {"lat": 46.7727, "lon": -100.7461, "name": "Bismarck, ND"},
    "KBOS": {"lat": 42.3656, "lon": -71.0096, "name": "Boston Logan, MA"},
    "KDFW": {"lat": 32.8998, "lon": -97.0403, "name": "Dallas/Fort Worth, TX"},
    "KDEN": {"lat": 39.8561, "lon": -104.6737, "name": "Denver Intl, CO"},
    "KLAX": {"lat": 33.9416, "lon": -118.4085, "name": "Los Angeles Intl, CA"},
    "KMIA": {"lat": 25.7959, "lon": -80.2870, "name": "Miami Intl, FL"},
    "KOMA": {"lat": 41.3032, "lon": -95.8941, "name": "Omaha Eppley, NE"},
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare, IL"},
    "KPDX": {"lat": 45.5898, "lon": -122.5951, "name": "Portland Intl, OR"},
    "KPHX": {"lat": 33.4352, "lon": -112.0101, "name": "Phoenix Sky Harbor, AZ"},
    "KTUS": {"lat": 32.1161, "lon": -110.9413, "name": "Tucson Intl, AZ"}
}

# Accuracy tolerances
TOLERANCES = {
    "aqi": 20,        # AQI within ±20 points = accurate
    "pollen": 1       # Pollen level within ±1 level (0-5 scale) = accurate
}

# API Keys from environment variables
AIRNOW_API_KEY = os.environ.get('AIRNOW_API_KEY', '')
TOMORROW_API_KEY = os.environ.get('TOMORROW_API_KEY', '')

# Data directories
DATA_DIR = Path("data")
AQ_CURRENT_DIR = DATA_DIR / "air_quality" / "current"
AQ_FORECAST_DIR = DATA_DIR / "air_quality" / "forecasts"
POLLEN_CURRENT_DIR = DATA_DIR / "pollen" / "current"
POLLEN_FORECAST_DIR = DATA_DIR / "pollen" / "forecasts"
RESULTS_FILE = DATA_DIR / "results.json"

# Create directories
for directory in [AQ_CURRENT_DIR, AQ_FORECAST_DIR, POLLEN_CURRENT_DIR, POLLEN_FORECAST_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def fetch_air_quality(location_code, lat, lon):
    """Fetch current air quality and forecast from AirNow API"""
    if not AIRNOW_API_KEY:
        print(f"⚠️  No AirNow API key - skipping {location_code}")
        return None
    
    # Current observations
    current_url = "http://www.airnowapi.org/aq/observation/latLong/current/"
    current_params = {
        "format": "application/json",
        "latitude": lat,
        "longitude": lon,
        "distance": 25,
        "API_KEY": AIRNOW_API_KEY
    }
    
    # Forecast
    forecast_url = "http://www.airnowapi.org/aq/forecast/latLong/"
    forecast_params = {
        "format": "application/json",
        "latitude": lat,
        "longitude": lon,
        "distance": 25,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "API_KEY": AIRNOW_API_KEY
    }
    
    try:
        # Get current conditions
        current_response = requests.get(current_url, params=current_params, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        # Get forecast
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Parse current data
        aqi_data = {}
        if current_data:
            # AirNow returns array of measurements
            for measurement in current_data:
                param = measurement.get('ParameterName', '')
                aqi = measurement.get('AQI', 0)
                
                if param == 'O3':
                    aqi_data['o3'] = aqi
                elif param == 'PM2.5':
                    aqi_data['pm25'] = aqi
                elif param == 'PM10':
                    aqi_data['pm10'] = aqi
            
            # Overall AQI is the highest value
            if aqi_data:
                aqi_data['aqi'] = max(aqi_data.values())
        
        # Parse forecast data
        forecast_aqi = []
        if forecast_data:
            for forecast in forecast_data:
                forecast_aqi.append({
                    'date': forecast.get('DateForecast', ''),
                    'aqi': forecast.get('AQI', 0),
                    'category': forecast.get('Category', {}).get('Name', '')
                })
        
        return {
            'current': aqi_data,
            'forecast': forecast_aqi[:3]  # Next 3 days
        }
        
    except Exception as e:
        print(f"❌ Error fetching air quality for {location_code}: {e}")
        return None


def fetch_pollen(location_code, lat, lon):
    """Fetch current pollen and forecast from Tomorrow.io API"""
    if not TOMORROW_API_KEY:
        print(f"⚠️  No Tomorrow.io API key - skipping {location_code}")
        return None
    
    url = "https://api.tomorrow.io/v4/timelines"
    
    # Request both current and forecast data
    params = {
        "location": f"{lat},{lon}",
        "fields": "treeIndex,grassIndex,weedIndex",
        "timesteps": "1d",
        "startTime": "now",
        "endTime": (datetime.now() + timedelta(days=5)).isoformat(),
        "apikey": TOMORROW_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Parse the timeline
        timeline = data.get('data', {}).get('timelines', [])
        if not timeline:
            return None
        
        intervals = timeline[0].get('intervals', [])
        if not intervals:
            return None
        
        # First interval is current/today
        current = intervals[0]['values']
        current_pollen = {
            'tree': current.get('treeIndex', 0),
            'grass': current.get('grassIndex', 0),
            'weed': current.get('weedIndex', 0),
            'overall': max(current.get('treeIndex', 0), 
                          current.get('grassIndex', 0), 
                          current.get('weedIndex', 0))
        }
        
        # Remaining intervals are forecasts
        forecast_pollen = []
        for interval in intervals[1:6]:  # Next 5 days
            values = interval['values']
            forecast_pollen.append({
                'date': interval['startTime'][:10],  # YYYY-MM-DD
                'tree': values.get('treeIndex', 0),
                'grass': values.get('grassIndex', 0),
                'weed': values.get('weedIndex', 0),
                'overall': max(values.get('treeIndex', 0),
                             values.get('grassIndex', 0),
                             values.get('weedIndex', 0))
            })
        
        return {
            'current': current_pollen,
            'forecast': forecast_pollen
        }
        
    except Exception as e:
        print(f"❌ Error fetching pollen for {location_code}: {e}")
        return None


def save_current_conditions(today_str):
    """Collect and save today's current conditions"""
    print(f"\n📊 Collecting current conditions for {today_str}")
    
    aq_data = {}
    pollen_data = {}
    
    for code, info in LOCATIONS.items():
        print(f"  Fetching {code} ({info['name']})...")
        
        # Air quality
        aq_result = fetch_air_quality(code, info['lat'], info['lon'])
        if aq_result:
            aq_data[code] = aq_result['current']
        
        # Pollen
        pollen_result = fetch_pollen(code, info['lat'], info['lon'])
        if pollen_result:
            pollen_data[code] = pollen_result['current']
    
    # Save current conditions
    aq_file = AQ_CURRENT_DIR / f"{today_str}.json"
    with open(aq_file, 'w') as f:
        json.dump(aq_data, f, indent=2)
    print(f"✅ Saved air quality to {aq_file}")
    
    pollen_file = POLLEN_CURRENT_DIR / f"{today_str}.json"
    with open(pollen_file, 'w') as f:
        json.dump(pollen_data, f, indent=2)
    print(f"✅ Saved pollen data to {pollen_file}")


def save_forecasts(today_str):
    """Collect and save forecasts for future dates"""
    print(f"\n🔮 Collecting forecasts from {today_str}")
    
    for code, info in LOCATIONS.items():
        print(f"  Fetching forecasts for {code}...")
        
        # Air quality forecasts
        aq_result = fetch_air_quality(code, info['lat'], info['lon'])
        if aq_result and aq_result.get('forecast'):
            for forecast in aq_result['forecast']:
                forecast_date = forecast['date']
                
                # Calculate lead time
                forecast_dt = datetime.strptime(forecast_date, '%Y-%m-%d')
                today_dt = datetime.strptime(today_str, '%Y-%m-%d')
                lead_days = (forecast_dt - today_dt).days
                
                if lead_days > 0:
                    # Save forecast
                    forecast_file = AQ_FORECAST_DIR / f"{today_str}_lead{lead_days}_{code}.json"
                    forecast_data = {
                        'issued_date': today_str,
                        'forecast_date': forecast_date,
                        'lead_days': lead_days,
                        'location': code,
                        'aqi': forecast['aqi'],
                        'category': forecast['category']
                    }
                    
                    with open(forecast_file, 'w') as f:
                        json.dump(forecast_data, f, indent=2)
        
        # Pollen forecasts
        pollen_result = fetch_pollen(code, info['lat'], info['lon'])
        if pollen_result and pollen_result.get('forecast'):
            for forecast in pollen_result['forecast']:
                forecast_date = forecast['date']
                
                # Calculate lead time
                forecast_dt = datetime.strptime(forecast_date, '%Y-%m-%d')
                today_dt = datetime.strptime(today_str, '%Y-%m-%d')
                lead_days = (forecast_dt - today_dt).days
                
                if lead_days > 0:
                    # Save forecast
                    forecast_file = POLLEN_FORECAST_DIR / f"{today_str}_lead{lead_days}_{code}.json"
                    forecast_data = {
                        'issued_date': today_str,
                        'forecast_date': forecast_date,
                        'lead_days': lead_days,
                        'location': code,
                        'tree': forecast['tree'],
                        'grass': forecast['grass'],
                        'weed': forecast['weed'],
                        'overall': forecast['overall']
                    }
                    
                    with open(forecast_file, 'w') as f:
                        json.dump(forecast_data, f, indent=2)
    
    print(f"✅ Saved forecasts for future dates")


def score_forecasts(today_str):
    """Score any forecasts that are ready (forecast date has arrived)"""
    print(f"\n🎯 Scoring forecasts for {today_str}")
    
    scored_count = 0
    
    # Score air quality forecasts
    for forecast_file in AQ_FORECAST_DIR.glob("*_*.json"):
        with open(forecast_file) as f:
            forecast = json.load(f)
        
        # Check if forecast is for today
        if forecast['forecast_date'] == today_str:
            location = forecast['location']
            
            # Load actual conditions
            actual_file = AQ_CURRENT_DIR / f"{today_str}.json"
            if actual_file.exists():
                with open(actual_file) as f:
                    actuals = json.load(f)
                
                if location in actuals:
                    actual_aqi = actuals[location].get('aqi', 0)
                    forecast_aqi = forecast['aqi']
                    
                    # Calculate accuracy
                    diff = abs(actual_aqi - forecast_aqi)
                    accurate = diff <= TOLERANCES['aqi']
                    
                    # Save result
                    result = {
                        'date': today_str,
                        'type': 'air_quality',
                        'location': location,
                        'lead_days': forecast['lead_days'],
                        'forecast_aqi': forecast_aqi,
                        'actual_aqi': actual_aqi,
                        'diff': diff,
                        'accurate': accurate
                    }
                    
                    save_result(result)
                    scored_count += 1
                    
                    # Delete scored forecast
                    forecast_file.unlink()
    
    # Score pollen forecasts
    for forecast_file in POLLEN_FORECAST_DIR.glob("*_*.json"):
        with open(forecast_file) as f:
            forecast = json.load(f)
        
        # Check if forecast is for today
        if forecast['forecast_date'] == today_str:
            location = forecast['location']
            
            # Load actual conditions
            actual_file = POLLEN_CURRENT_DIR / f"{today_str}.json"
            if actual_file.exists():
                with open(actual_file) as f:
                    actuals = json.load(f)
                
                if location in actuals:
                    actual_overall = actuals[location].get('overall', 0)
                    forecast_overall = forecast['overall']
                    
                    # Calculate accuracy
                    diff = abs(actual_overall - forecast_overall)
                    accurate = diff <= TOLERANCES['pollen']
                    
                    # Save result
                    result = {
                        'date': today_str,
                        'type': 'pollen',
                        'location': location,
                        'lead_days': forecast['lead_days'],
                        'forecast_level': forecast_overall,
                        'actual_level': actual_overall,
                        'diff': diff,
                        'accurate': accurate
                    }
                    
                    save_result(result)
                    scored_count += 1
                    
                    # Delete scored forecast
                    forecast_file.unlink()
    
    if scored_count > 0:
        print(f"✅ Scored {scored_count} forecasts")
    else:
        print("  No forecasts ready to score yet")


def save_result(result):
    """Append a result to the results file"""
    # Load existing results
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            results = json.load(f)
    else:
        results = []
    
    # Add new result
    results.append(result)
    
    # Save
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)


def main():
    """Main execution"""
    print("🌍 Air Quality & Pollen Tracker")
    print("=" * 50)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Step 1: Collect current conditions
    save_current_conditions(today)
    
    # Step 2: Collect forecasts
    save_forecasts(today)
    
    # Step 3: Score any ready forecasts
    score_forecasts(today)
    
    print("\n✨ Done!")


if __name__ == "__main__":
    main()
