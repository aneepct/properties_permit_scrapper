#!/usr/bin/env python3
"""
Mock/Demo Version of Enterprise Scraper
Generates realistic sample data for testing
"""

import os
import json
import csv
import random
from datetime import datetime, timedelta, timezone
import pandas as pd

# Mock data pools
CONTRACTORS = [
    "ABC Construction Corp", "Metro Building Systems", "Elite Contractors LLC",
    "Skyline Construction", "Premier Build Group", "Urban Development Co",
    "Apex Construction Services", "Diamond Building Solutions", "Crown Contractors",
    "Pacific Construction Group", "Summit Building Corp", "Prestige Builders Inc"
]

ADDRESSES = [
    ("123", "Main Street"), ("456", "Broadway"), ("789", "Park Avenue"),
    ("321", "First Street"), ("654", "Second Avenue"), ("987", "Third Street"),
    ("159", "Market Street"), ("753", "Oak Avenue"), ("852", "Pine Street"),
    ("741", "Cedar Lane"), ("963", "Elm Street"), ("147", "Maple Avenue")
]

DESCRIPTIONS = [
    "New 20-story mixed-use commercial building with retail ground floor",
    "High-rise residential tower with 200+ luxury units",
    "Major office building renovation and modernization",
    "New hospital wing construction and medical facilities",
    "Large retail and entertainment complex development",
    "Mixed-use development with residential and commercial spaces",
    "Corporate headquarters building construction",
    "Luxury hotel and conference center development",
    "Educational facility expansion and renovation",
    "Industrial warehouse and distribution center construction"
]

CITIES_DATA = {
    "nyc": {"name": "New York City", "areas": ["Manhattan", "Brooklyn", "Queens", "Bronx"]},
    "chicago": {"name": "Chicago", "areas": ["Downtown", "North Side", "South Side", "West Side"]},
    "la": {"name": "Los Angeles", "areas": ["Downtown", "Hollywood", "Beverly Hills", "Santa Monica"]},
    "sf": {"name": "San Francisco", "areas": ["SOMA", "Financial District", "Mission Bay", "Presidio"]}
}

def generate_mock_permit(city_key, permit_num):
    """Generate a single mock permit"""
    city_data = CITIES_DATA[city_key]
    
    # Random dates within last 30 days
    days_ago = random.randint(0, 30)
    issue_date = datetime.now() - timedelta(days=days_ago)
    
    # Random cost between $1M and $50M
    cost = random.randint(1000000, 50000000)
    
    # Random address
    house_num, street = random.choice(ADDRESSES)
    
    permit = {
        "city": city_data["name"],
        "permit_id": f"{city_key.upper()}-2025-{permit_num:06d}",
        "issue_date": issue_date.isoformat(),
        "full_address": f"{house_num} {street}",
        "borough_area": random.choice(city_data["areas"]),
        "zip_code": f"{random.randint(10000, 99999)}",
        "project_description": random.choice(DESCRIPTIONS),
        "estimated_cost": str(cost),
        "contractor_name": random.choice(CONTRACTORS),
        "contractor_license": f"LIC-{random.randint(100000, 999999)}",
        "applicant_name": f"Development Group {random.randint(1, 100)}",
        "owner_name": f"Property Holdings LLC {random.randint(1, 50)}",
        "architect_name": f"Design Studio {random.randint(1, 25)}",
        "license_status": random.choice(["Active", "Verified", "Pending Review"]),
        "business_address": f"{random.randint(100, 9999)} Business Ave",
        "business_phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        "data_source": f"{city_data['name']} Open Data (Mock)",
        "scraped_at": datetime.now(timezone.utc).isoformat()
    }
    
    return permit

def create_mock_run():
    """Create a full mock run with all cities"""
    print("🎭 Enterprise Permit Scraper - Mock Demo")
    print("="*45)
    
    # Create directories
    for directory in ["output", "state", "logs"]:
        os.makedirs(directory, exist_ok=True)
    
    all_permits = []
    summary = []
    date_tag = datetime.now().strftime("%Y%m%d")
    
    for city_key, city_data in CITIES_DATA.items():
        print(f"\n🏙️ Generating mock data for {city_data['name']}...")
        
        # Generate 3-8 permits per city
        num_permits = random.randint(3, 8)
        city_permits = []
        
        for i in range(num_permits):
            permit = generate_mock_permit(city_key, i + 1)
            city_permits.append(permit)
        
        all_permits.extend(city_permits)
        
        # Save city CSV
        city_filename = f"{city_key}_permits_{date_tag}.csv"
        city_filepath = os.path.join("output", city_filename)
        
        df = pd.DataFrame(city_permits)
        df.to_csv(city_filepath, index=False, quoting=csv.QUOTE_MINIMAL)
        
        total_value = sum(int(p["estimated_cost"]) for p in city_permits)
        
        print(f"  ✅ Generated {num_permits} permits")
        print(f"  💰 Total value: ${total_value:,}")
        print(f"  📄 Saved to: {city_filename}")
        
        summary.append(f"✅ {city_data['name']}: {num_permits} permits (${total_value:,})")
    
    # Create master CSV
    master_df = pd.DataFrame(all_permits)
    master_csv = os.path.join("output", "master_permits.csv")
    master_df.to_csv(master_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    
    # Create state file
    state = {
        city_key: {
            "last_successful_run": datetime.now(timezone.utc).isoformat(),
            "permits_found": len([p for p in all_permits if p["city"] == city_data["name"]]),
            "last_error": None
        }
        for city_key, city_data in CITIES_DATA.items()
    }
    
    with open(os.path.join("state", "last_run.json"), "w") as f:
        json.dump(state, f, indent=2)
    
    # Summary report
    total_permits = len(all_permits)
    total_value = sum(int(p["estimated_cost"]) for p in all_permits)
    
    print(f"\n📊 MOCK RUN SUMMARY")
    print("="*25)
    print(f"🏗️ Total permits: {total_permits}")
    print(f"💰 Combined value: ${total_value:,}")
    print("\nCity breakdown:")
    for line in summary:
        print(f"  {line}")
    print(f"\n📄 Master file: {master_csv}")
    print(f"📁 All files saved to: output/")
    
    print(f"\n🎯 Demo Complete!")
    print("This mock data shows what the real scraper would produce.")
    print("Files are ready for import into CRM or analysis tools.")

if __name__ == "__main__":
    create_mock_run()
