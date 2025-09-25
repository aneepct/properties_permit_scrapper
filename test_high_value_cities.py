import requests
import pandas as pd
from datetime import datetime, timedelta

def test_high_value_permits():
    """Test each city for high-value permits"""
    
    print("🔍 Testing High-Value Permits Across Cities")
    print("=" * 60)
    
    # Test Chicago for high-value permits
    print("\n🏙️  CHICAGO - Testing for high-value permits")
    print("-" * 40)
    try:
        # Chicago uses 'reported_cost' for actual project value, 'total_fee' is just fees
        chicago_params = {
            "$limit": 1000,
            "$order": "issue_date DESC",
            "$where": "reported_cost > 1000000"  # Test for $1M+ projects
        }
        response = requests.get("https://data.cityofchicago.org/resource/ydr8-5enu.json", 
                               params=chicago_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['reported_cost'] = pd.to_numeric(df['reported_cost'], errors='coerce')
                high_value = df[df['reported_cost'] > 1000000]
                print(f"✅ Chicago: Found {len(high_value)} permits over $1M")
                if len(high_value) > 0:
                    print(f"   💰 Highest: ${high_value['reported_cost'].max():,.0f}")
                    print(f"   📊 Average: ${high_value['reported_cost'].mean():,.0f}")
            else:
                print("❌ Chicago: No data returned for high-value query")
        else:
            print(f"❌ Chicago: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Chicago error: {e}")
    
    # Test Los Angeles for high-value permits  
    print("\n🏙️  LOS ANGELES - Testing for high-value permits")
    print("-" * 40)
    try:
        la_params = {
            "$limit": 1000,
            "$order": "issue_date DESC", 
            "$where": "valuation > 1000000"
        }
        response = requests.get("https://data.lacity.org/resource/d9aa-v8bm.json", 
                               params=la_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['valuation'] = pd.to_numeric(df['valuation'], errors='coerce')
                high_value = df[df['valuation'] > 1000000]
                print(f"✅ LA: Found {len(high_value)} permits over $1M")
                if len(high_value) > 0:
                    print(f"   💰 Highest: ${high_value['valuation'].max():,.0f}")
                    print(f"   📊 Average: ${high_value['valuation'].mean():,.0f}")
            else:
                print("❌ LA: No data returned for high-value query")
        else:
            print(f"❌ LA: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ LA error: {e}")
    
    # Test San Francisco for high-value permits
    print("\n🏙️  SAN FRANCISCO - Testing for high-value permits") 
    print("-" * 40)
    try:
        sf_params = {
            "$limit": 1000,
            "$order": "issued_date DESC",
            "$where": "estimated_cost > 1000000 OR revised_cost > 1000000"
        }
        response = requests.get("https://data.sfgov.org/resource/i98e-djp9.json", 
                               params=sf_params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['estimated_cost'] = pd.to_numeric(df['estimated_cost'], errors='coerce')
                df['revised_cost'] = pd.to_numeric(df['revised_cost'], errors='coerce')
                
                # Use the higher of estimated or revised cost
                df['max_cost'] = df[['estimated_cost', 'revised_cost']].max(axis=1)
                high_value = df[df['max_cost'] > 1000000]
                
                print(f"✅ SF: Found {len(high_value)} permits over $1M")
                if len(high_value) > 0:
                    print(f"   💰 Highest: ${high_value['max_cost'].max():,.0f}")
                    print(f"   📊 Average: ${high_value['max_cost'].mean():,.0f}")
            else:
                print("❌ SF: No data returned for high-value query")
        else:
            print(f"❌ SF: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ SF error: {e}")

if __name__ == "__main__":
    test_high_value_permits()