#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enterprise Permit Scraper - Production Ready
Fast execution with immediate mock data generation for testing
"""

import os
import json
import csv
import logging
import random
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd

# ---------- Configuration ----------
class Config:
    OUTPUT_DIR = "output"
    STATE_DIR = "state" 
    LOGS_DIR = "logs"
    
    STATE_FILE = os.path.join(STATE_DIR, "last_run.json")
    MASTER_CSV = os.path.join(OUTPUT_DIR, "master_permits.csv")
    LOG_FILE = os.path.join(LOGS_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")

# Cities to scrape
CITIES = {
    "nyc": {"name": "New York City", "areas": ["Manhattan", "Brooklyn", "Queens", "Bronx"]},
    "chicago": {"name": "Chicago", "areas": ["Downtown", "North Side", "South Side", "West Side"]},
    "la": {"name": "Los Angeles", "areas": ["Downtown", "Hollywood", "Beverly Hills", "Santa Monica"]}, 
    "sf": {"name": "San Francisco", "areas": ["SOMA", "Financial District", "Mission Bay", "Presidio"]}
}

# Sample data pools
CONTRACTORS = [
    "ABC Construction Corp", "Metro Building Systems", "Elite Contractors LLC",
    "Skyline Construction", "Premier Build Group", "Urban Development Co",
    "Apex Construction Services", "Diamond Building Solutions", "Crown Contractors",
    "Pacific Construction Group", "Summit Building Corp", "Prestige Builders Inc"
]

ADDRESSES = [
    ("123", "Main Street"), ("456", "Broadway"), ("789", "Park Avenue"), 
    ("321", "First Street"), ("654", "Second Avenue"), ("987", "Third Street"),
    ("159", "Market Street"), ("753", "Oak Avenue"), ("852", "Pine Street")
]

DESCRIPTIONS = [
    "New 30-story mixed-use commercial building with retail ground floor",
    "High-rise residential tower with 300+ luxury units", 
    "Major office building renovation and modernization project",
    "New hospital wing construction and medical facilities expansion",
    "Large retail and entertainment complex development",
    "Mixed-use development with residential and commercial spaces",
    "Corporate headquarters building construction project",
    "Luxury hotel and conference center development",
    "Educational facility expansion and renovation project",
    "Industrial warehouse and distribution center construction"
]

def setup_logging():
    """Setup logging with UTF-8 encoding"""
    os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def ensure_directories():
    """Create required directories"""
    for directory in [Config.OUTPUT_DIR, Config.STATE_DIR, Config.LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)

def load_state():
    """Load previous run state"""
    if not os.path.exists(Config.STATE_FILE):
        return {}
    try:
        with open(Config.STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    """Save current run state"""
    try:
        with open(Config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        logging.info("State saved successfully")
    except Exception as e:
        logging.error(f"Failed to save state: {e}")

def generate_permit(city_key, permit_num):
    """Generate a realistic permit record"""
    city_data = CITIES[city_key]
    
    # Random date within last 30 days
    days_ago = random.randint(0, 30)
    issue_date = datetime.now() - timedelta(days=days_ago)
    
    # Random cost between $1M and $50M
    cost = random.randint(1000000, 50000000)
    
    # Random address
    house_num, street = random.choice(ADDRESSES)
    
    return {
        "city": city_data["name"],
        "permit_id": f"{city_key.upper()}-2025-{permit_num:06d}",
        "issue_date": issue_date.strftime("%Y-%m-%d"),
        "full_address": f"{house_num} {street}",
        "borough_area": random.choice(city_data["areas"]),
        "zip_code": f"{random.randint(10000, 99999)}",
        "project_description": random.choice(DESCRIPTIONS),
        "estimated_cost": str(cost),
        "contractor_name": random.choice(CONTRACTORS),
        "contractor_license": f"LIC-{random.randint(100000, 999999)}",
        "applicant_name": f"Development Group {random.randint(1, 100)} LLC",
        "owner_name": f"Property Holdings {random.randint(1, 50)} Inc",
        "architect_name": f"Design Studio {random.randint(1, 25)}",
        "license_status": random.choice(["Active", "Verified", "Good Standing"]),
        "business_address": f"{random.randint(100, 9999)} Business Ave",
        "business_phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        "data_source": f"{city_data['name']} DOB (Demo Data)",
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_contact_by_type(row, contact_type):
    """
    Extract contact name by type from Chicago permit data.
    Looks through contact_1_type through contact_5_type fields.
    """
    for i in range(1, 6):
        type_field = f'contact_{i}_type'
        name_field = f'contact_{i}_name'
        if type_field in row and name_field in row:
            type_value = str(row.get(type_field, '')).upper()
            if contact_type.upper() in type_value:
                return str(row.get(name_field, 'N/A'))
    return "N/A"

def scrape_real_city_data(city_key, min_cost=1000000, days_back=60, limit=500):
    """
    Scrape real permit data for any city.
    Returns list of permits in the format expected by the main scraper.
    """
    
    # City API configurations
    city_configs = {
        "nyc": {
            "name": "New York City",
            "url": "https://data.cityofnewyork.us/resource/8sk9-t6ee.json",
            "cost_field": "estimated_job_costs",
            "date_field": "issued_date",
            "id_field": "job_filing_number",
            "address_fields": ["house_no", "street_name"],
            "area_field": "borough"
        },
        "chicago": {
            "name": "Chicago", 
            "url": "https://data.cityofchicago.org/resource/ydr8-5enu.json",
            "cost_field": "reported_cost",  # This is the actual project cost, not fees
            "date_field": "issue_date",
            "id_field": "permit_",
            "address_fields": ["street_number", "street_direction", "street_name"],
            "area_field": "community_area"
        },
        "la": {
            "name": "Los Angeles",
            "url": "https://data.lacity.org/resource/d9aa-v8bm.json", 
            "cost_field": "valuation",
            "date_field": "issue_date",
            "id_field": "pcis_permit",
            "address_fields": ["address_start", "street_direction", "street_name", "street_suffix"],
            "area_field": "council_district"
        },
        "sf": {
            "name": "San Francisco",
            "url": "https://data.sfgov.org/resource/i98e-djp9.json",
            "cost_field": "estimated_cost",
            "date_field": "issued_date", 
            "id_field": "permit_number",
            "address_fields": ["street_number", "street_name", "street_suffix"],
            "area_field": "supervisor_district"
        }
    }
    
    if city_key not in city_configs:
        logging.error(f"No configuration for city: {city_key}")
        return []
        
    config = city_configs[city_key]
    logging.info(f"🏗️  Scraping REAL {config['name']} permit data from API...")
    
    try:
        # Fetch recent permits (start with basic query to avoid API errors)
        params = {
            "$limit": limit,
            "$order": f"{config['date_field']} DESC"
        }
        
        response = requests.get(config['url'], params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            logging.warning(f"No data received from {config['name']} API")
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        logging.info(f"Retrieved {len(df)} total {config['name']} records")
        
        # Check required columns
        if config['cost_field'] not in df.columns:
            logging.error(f"Missing {config['cost_field']} column in {config['name']} data")
            return []
        
        # Process cost field
        df[config['cost_field']] = pd.to_numeric(df[config['cost_field']], errors='coerce')
        df = df.dropna(subset=[config['cost_field']])  # Remove invalid costs
        
        # Filter for high-value permits
        high_value_df = df[df[config['cost_field']] > min_cost].copy()
        
        # Filter by date if available
        if config['date_field'] in df.columns and len(high_value_df) > 0:
            try:
                cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                high_value_df = high_value_df[high_value_df[config['date_field']] >= cutoff_date]
            except Exception:
                logging.warning(f"Could not filter by date for {config['name']}")
        
        logging.info(f"Found {len(high_value_df)} {config['name']} permits over ${min_cost:,}")
        
        # Convert to the format expected by main scraper
        permits = []
        for idx, row in high_value_df.iterrows():
            
            # Build address from available fields
            address_parts = []
            for field in config['address_fields']:
                if field in row and pd.notnull(row[field]):
                    address_parts.append(str(row[field]))
            full_address = ' '.join(address_parts).strip()
            
            # Extract contractor name - special handling for Chicago contact structure
            contractor_name = "N/A"
            if city_key == "chicago":
                # Look for contractor in contact_1_type through contact_5_type fields
                for i in range(1, 6):
                    contact_type = row.get(f'contact_{i}_type', '')
                    if contact_type and 'CONTRACTOR' in str(contact_type).upper():
                        contractor_name = str(row.get(f'contact_{i}_name', 'N/A'))
                        # Prefer general contractor over specific trades
                        if 'GENERAL CONTRACTOR' in str(contact_type).upper():
                            break
            else:
                # Default contractor name extraction for other cities
                contractor_name = str(row.get('contractors_business_name', row.get('contractor_name', 'N/A')))
            
            permit = {
                "city": config['name'],
                "permit_id": str(row.get(config['id_field'], f"{city_key.upper()}-{idx}")),
                "issue_date": str(row.get(config['date_field'], datetime.now().strftime("%Y-%m-%d")))[:10],
                "full_address": full_address or "Address Not Available",
                "borough_area": str(row.get(config['area_field'], 'Unknown')),
                "zip_code": str(row.get('zip_code', row.get('zipcode', 'N/A'))),
                "project_description": str(row.get('work_description', row.get('description', row.get('job_description', 'Construction project'))))[:500],
                "estimated_cost": str(int(row.get(config['cost_field'], 0))),
                "contractor_name": contractor_name,
                "contractor_license": str(row.get('license', row.get('contractor_license', 'N/A'))),
                "applicant_name": f"{row.get('applicant_first_name', '')} {row.get('applicant_last_name', '')}".strip() or "N/A",
                "owner_name": get_contact_by_type(row, "OWNER") if city_key == "chicago" else "N/A",
                "architect_name": get_contact_by_type(row, "ARCHITECT") if city_key == "chicago" else "N/A",
                "license_status": str(row.get('license_status', 'N/A')),
                "business_address": str(row.get('contractor_address', 'N/A')),
                "business_phone": "N/A",
                "work_type": str(row.get('work_type', row.get('permit_type', 'General Construction'))),
                "block": str(row.get('block', '')),
                "lot": str(row.get('lot', '')),
                "bin": str(row.get('bin', '')),
                "data_source": f"{config['name']} Open Data (Real Data)",
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            permits.append(permit)
        
        if permits:
            total_value = sum(int(p["estimated_cost"]) for p in permits)
            logging.info(f"{config['name']} real data: {len(permits)} permits, total value: ${total_value:,}")
        
        return permits
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {config['name']} data: {e}")
        return []
    except Exception as e:
        logging.error(f"Error processing {config['name']} data: {e}")
        return []

def process_city(city_key):
    """Process permits for a single city"""
    city_data = CITIES[city_key]
    logging.info(f"Processing {city_data['name']}...")
    
    permits = []
    
    # Use real data for all cities now!
    if city_key in ["nyc", "chicago", "la", "sf"]:
        logging.info(f"🔥 Using REAL {city_data['name']} permit data from Open Data API...")
        # Fetch permits over $1M from last 60 days, max 500 records
        permits = scrape_real_city_data(city_key, min_cost=1000000, days_back=60, limit=500)
        
        # If real data fails, fall back to mock data
        if not permits:
            logging.warning(f"Real {city_data['name']} data failed, falling back to mock data")
            num_permits = random.randint(3, 8)
            for i in range(num_permits):
                permit = generate_permit(city_key, i + 1)
                permits.append(permit)
    else:
        # Generate mock data for any other cities
        num_permits = random.randint(2, 8)
        for i in range(num_permits):
            permit = generate_permit(city_key, i + 1)
            permits.append(permit)
    
    # Calculate total value
    total_value = sum(int(p["estimated_cost"]) for p in permits)
    
    # Log results based on data source
    if city_key == "nyc" and permits and permits[0].get("data_source") == "NYC DOB NOW (Real Data)":
        logging.info(f"Retrieved {len(permits)} REAL permits for {city_data['name']} (${total_value:,})")
    else:
        logging.info(f"Generated {len(permits)} permits for {city_data['name']} (${total_value:,})")
    
    return permits

def save_city_csv(city_key, permits):
    """Save permits to city-specific CSV"""
    if not permits:
        return ""
    
    date_tag = datetime.now().strftime("%Y%m%d")
    filename = f"{city_key}_permits_{date_tag}.csv"
    filepath = os.path.join(Config.OUTPUT_DIR, filename)
    
    df = pd.DataFrame(permits)
    df.to_csv(filepath, index=False, quoting=csv.QUOTE_MINIMAL)
    
    logging.info(f"Saved {city_key} permits to {filename}")
    return filepath

def update_master_csv(all_permits):
    """Update master CSV with all permits"""
    if not all_permits:
        return
    
    df = pd.DataFrame(all_permits)
    
    # If master exists, load and merge
    if os.path.exists(Config.MASTER_CSV):
        try:
            existing_df = pd.read_csv(Config.MASTER_CSV, dtype=str)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Remove duplicates based on city + permit_id
            combined_df = combined_df.drop_duplicates(subset=["city", "permit_id"], keep="last")
        except Exception:
            combined_df = df
    else:
        combined_df = df
    
    # Save master file
    combined_df.to_csv(Config.MASTER_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
    logging.info(f"Master CSV updated: {len(combined_df)} total permits")

def main():
    """Main execution function"""
    logger = setup_logging()
    ensure_directories()
    
    start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("ENTERPRISE PERMIT SCRAPER - PRODUCTION RUN")
    logger.info("=" * 60)
    logger.info(f"Started at: {start_time}")
    
    state = load_state()
    all_permits = []
    city_summaries = []
    
    try:
        # Process each city
        for city_key in CITIES.keys():
            try:
                permits = process_city(city_key)
                
                if permits:
                    # Save city CSV
                    filepath = save_city_csv(city_key, permits)
                    
                    # Add to master list
                    all_permits.extend(permits)
                    
                    # Update state
                    state[city_key] = {
                        "last_run": datetime.now().isoformat(),
                        "permits_found": len(permits),
                        "last_file": filepath,
                        "last_error": None
                    }
                    
                    total_value = sum(int(p["estimated_cost"]) for p in permits)
                    city_summaries.append(f"SUCCESS {CITIES[city_key]['name']}: {len(permits)} permits (${total_value:,})")
                    
                else:
                    city_summaries.append(f"WARNING {CITIES[city_key]['name']}: No permits found")
                    
            except Exception as e:
                error_msg = f"Error processing {CITIES[city_key]['name']}: {str(e)}"
                logger.error(error_msg)
                city_summaries.append(f"ERROR {CITIES[city_key]['name']}: {str(e)}")
                
                # Update state with error
                if city_key not in state:
                    state[city_key] = {}
                state[city_key]["last_error"] = error_msg
        
        # Update master CSV
        update_master_csv(all_permits)
        
        # Save final state
        save_state(state)
        
        # Generate final summary
        end_time = datetime.now()
        duration = end_time - start_time
        total_permits = len(all_permits)
        total_value = sum(int(p["estimated_cost"]) for p in all_permits)
        
        summary = f"""
PERMIT SCRAPER RUN COMPLETED
============================
Runtime: {duration}
Total permits found: {total_permits}
Combined project value: ${total_value:,}

City Results:
{chr(10).join(city_summaries)}

Output Files:
- Master CSV: {Config.MASTER_CSV}
- Individual city files in: {Config.OUTPUT_DIR}
- State file: {Config.STATE_FILE}
- Log file: {Config.LOG_FILE}

Next Steps:
1. Review the CSV files for data quality
2. Import into your CRM system
3. Set up daily automation
4. Configure API integrations for live data
"""
        
        logger.info(summary)
        print("\nSUCCESS! Check the output folder for your permit data.")
        
    except KeyboardInterrupt:
        logger.info("Scraper interrupted by user")
        
    except Exception as e:
        logger.error(f"Critical error in main execution: {str(e)}")
        raise
    
    logger.info("Permit scraper execution completed")

if __name__ == "__main__":
    main()
