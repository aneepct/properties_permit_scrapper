import requests
import pandas as pd
from datetime import datetime, timedelta

# NYC DOB NOW dataset (Socrata API endpoint)
BASE_URL = "https://data.cityofnewyork.us/resource/8sk9-t6ee.json"

print("🔍 First, let's check the dataset schema...")

# First, get a small sample to see available columns
schema_params = {
    "$limit": 5
}

schema_response = requests.get(BASE_URL, params=schema_params)
schema_data = schema_response.json()

if schema_data:
    schema_df = pd.DataFrame(schema_data)
    print(f"📋 Available columns in dataset: {list(schema_df.columns)}")
    print("\n🔍 Sample data structure:")
    print(schema_df.head(2))
    print("\n" + "="*50)

print("\n🚀 Now fetching recent high-value permits...")

# Start with a simple query to avoid API errors
params = {
    "$limit": 200,
    "$order": "issued_date DESC"
}

print("🔍 Testing simple query first...")

response = requests.get(BASE_URL, params=params)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data)

print(f"📊 Retrieved {len(df)} records from NYC API")
print(f"📋 Available columns: {list(df.columns)}")

# Select useful fields based on actual available columns
desired_fields = [
    "job_filing_number", 
    "issued_date",  # This is the correct field name (not issuance_date)
    "house_no",     # This is the correct field name (not house_number)
    "street_name",
    "borough",
    "block",
    "lot",
    "bin",
    "work_on_floor",
    "work_type",
    "work_permit",
    "estimated_job_costs",
    "job_description",
    "filing_reason"
]

# Only keep fields that actually exist in the DataFrame
keep_fields = [field for field in desired_fields if field in df.columns]
missing_fields = [field for field in desired_fields if field not in df.columns]

print(f"✅ Available fields to keep: {keep_fields}")
if missing_fields:
    print(f"⚠️  Missing fields: {missing_fields}")

# Select only available fields
if keep_fields:
    df = df[keep_fields]
    
    # Add some data processing
    if 'estimated_job_costs' in df.columns:
        # Convert estimated_job_costs to numeric and format
        df['estimated_job_costs'] = pd.to_numeric(df['estimated_job_costs'], errors='coerce')
        df = df.dropna(subset=['estimated_job_costs'])  # Remove rows with invalid costs
        
        # Filter for high-value permits (>$1M)
        high_value_df = df[df['estimated_job_costs'] > 1000000]
        
        print(f"💰 Found {len(high_value_df)} permits over $1M")
        if len(high_value_df) > 0:
            print(f"💸 Total value: ${high_value_df['estimated_job_costs'].sum():,.0f}")
            print(f"📊 Average cost: ${high_value_df['estimated_job_costs'].mean():,.0f}")
            print(f"🏆 Highest cost: ${high_value_df['estimated_job_costs'].max():,.0f}")
        
        # Use high-value permits for output
        df = high_value_df
else:
    print("❌ No matching fields found, keeping all columns")
    print("🔍 First few rows of data:")
    print(df.head())

# Save to CSV
if len(df) > 0:
    output_file = f"nyc_permits_over_1M_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Saved {len(df)} high-value permits to {output_file}")
    
    # Show sample data safely
    print("\n🔍 Sample of saved data:")
    available_cols = [col for col in ['job_filing_number', 'borough', 'street_name', 'estimated_job_costs', 'work_type'] if col in df.columns]
    if available_cols:
        print(df[available_cols].head())
    else:
        print("Available columns:", list(df.columns))
        print(df.head())
else:
    print("⚠️  No high-value permits found in the specified time range")