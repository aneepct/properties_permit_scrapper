import requests
import pandas as pd
from datetime import datetime, timedelta

# City APIs
CITY_APIS = {
    "chicago": {
        "name": "Chicago",
        "url": "https://data.cityofchicago.org/resource/ydr8-5enu.json",
        "cost_field_candidates": ["estimated_cost", "total_fee", "fee", "cost", "value"]
    },
    "la": {
        "name": "Los Angeles", 
        "url": "https://data.lacity.org/resource/d9aa-v8bm.json",
        "cost_field_candidates": ["valuation", "estimated_cost", "total_fee", "cost", "value"]
    },
    "sf": {
        "name": "San Francisco",
        "url": "https://data.sfgov.org/resource/i98e-djp9.json", 
        "cost_field_candidates": ["estimated_cost", "valuation", "revised_cost", "cost", "value"]
    }
}

def test_city_api(city_key, city_info):
    """Test a city's API and analyze its data structure"""
    print(f"\n🏙️  Testing {city_info['name']} API")
    print("=" * 50)
    
    try:
        # Test schema
        schema_params = {"$limit": 5}
        response = requests.get(city_info['url'], params=schema_params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}...")
            return None
            
        data = response.json()
        
        if not data:
            print("❌ No data returned")
            return None
            
        df = pd.DataFrame(data)
        print(f"📊 Retrieved {len(df)} sample records")
        print(f"📋 Available columns ({len(df.columns)}): {list(df.columns)}")
        
        # Look for cost-related fields
        cost_fields = []
        for candidate in city_info['cost_field_candidates']:
            if candidate in df.columns:
                cost_fields.append(candidate)
        
        if cost_fields:
            print(f"💰 Cost fields found: {cost_fields}")
            # Test the first cost field
            cost_field = cost_fields[0]
            df[cost_field] = pd.to_numeric(df[cost_field], errors='coerce')
            valid_costs = df[cost_field].dropna()
            if len(valid_costs) > 0:
                print(f"💸 Cost field '{cost_field}' sample values:")
                print(f"   Min: ${valid_costs.min():,.0f}")
                print(f"   Max: ${valid_costs.max():,.0f}")
                print(f"   Avg: ${valid_costs.mean():,.0f}")
        else:
            print("⚠️  No cost fields found in common names")
        
        # Look for address/location fields
        address_fields = [col for col in df.columns if any(word in col.lower() for word in ['address', 'street', 'location', 'site'])]
        if address_fields:
            print(f"🏠 Address fields: {address_fields}")
        
        # Look for date fields
        date_fields = [col for col in df.columns if any(word in col.lower() for word in ['date', 'issued', 'created', 'application'])]
        if date_fields:
            print(f"📅 Date fields: {date_fields}")
        
        # Look for permit ID fields
        id_fields = [col for col in df.columns if any(word in col.lower() for word in ['permit', 'id', 'number', 'filing'])]
        if id_fields:
            print(f"🆔 ID fields: {id_fields}")
        
        # Show sample data for key fields
        key_fields = []
        if cost_fields:
            key_fields.append(cost_fields[0])
        if address_fields:
            key_fields.append(address_fields[0])
        if date_fields:
            key_fields.append(date_fields[0])
        if id_fields:
            key_fields.append(id_fields[0])
            
        if key_fields:
            print(f"\n🔍 Sample data for key fields:")
            sample_fields = [f for f in key_fields[:4] if f in df.columns]  # Limit to 4 fields
            if sample_fields:
                print(df[sample_fields].head(3).to_string(index=False, max_colwidth=40))
        
        return {
            "city": city_key,
            "columns": list(df.columns),
            "cost_fields": cost_fields,
            "address_fields": address_fields,
            "date_fields": date_fields,
            "id_fields": id_fields,
            "sample_data": df.head(3)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Test all city APIs"""
    print("🔍 Testing All City Building Permit APIs")
    print("=" * 60)
    
    results = {}
    
    for city_key, city_info in CITY_APIS.items():
        result = test_city_api(city_key, city_info)
        if result:
            results[city_key] = result
    
    # Summary
    print(f"\n📋 SUMMARY - Tested {len(results)}/{len(CITY_APIS)} APIs successfully")
    print("=" * 60)
    
    for city_key, result in results.items():
        city_name = CITY_APIS[city_key]['name']
        cost_fields = result['cost_fields']
        status = "✅ Ready" if cost_fields else "⚠️  Needs mapping"
        print(f"{city_name}: {status} - Cost fields: {cost_fields}")

if __name__ == "__main__":
    main()