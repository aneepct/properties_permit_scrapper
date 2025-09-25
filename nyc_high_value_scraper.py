"""
NYC High-Value Permits Scraper
===============================

This script fetches recent building permits from NYC DOB NOW dataset
and filters for high-value permits (over $1M estimated job costs).

Dataset: NYC Department of Buildings NOW - Job Filing Permits
API Endpoint: https://data.cityofnewyork.us/resource/8sk9-t6ee.json
"""

import requests
import pandas as pd
from datetime import datetime, timedelta

def get_nyc_high_value_permits(min_cost=1000000, days_back=30, limit=1000):
    """
    Fetch high-value building permits from NYC DOB NOW dataset.
    
    Args:
        min_cost (int): Minimum estimated job cost in dollars
        days_back (int): Number of days to look back from today
        limit (int): Maximum number of records to fetch
    
    Returns:
        pd.DataFrame: DataFrame containing high-value permits
    """
    
    # NYC DOB NOW dataset (Socrata API endpoint)
    BASE_URL = "https://data.cityofnewyork.us/resource/8sk9-t6ee.json"
    
    print("🏗️  NYC High-Value Permits Scraper")
    print("="*40)
    
    # First, check dataset schema
    print("🔍 Checking dataset schema...")
    schema_params = {"$limit": 5}
    
    try:
        schema_response = requests.get(BASE_URL, params=schema_params)
        schema_response.raise_for_status()
        schema_data = schema_response.json()
        
        if schema_data:
            schema_df = pd.DataFrame(schema_data)
            available_columns = list(schema_df.columns)
            print(f"📋 Available columns: {', '.join(available_columns)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking schema: {e}")
        return pd.DataFrame()
    
    # Fetch recent permits
    print(f"\n🚀 Fetching permits from last {days_back} days...")
    
    params = {
        "$limit": limit,
        "$order": "issued_date DESC"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print("❌ No data received from API")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        print(f"📊 Retrieved {len(df)} total records")
        
        # Check if we have the expected columns
        required_columns = ['job_filing_number', 'estimated_job_costs', 'issued_date']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            print(f"⚠️  Missing required columns: {missing_cols}")
            print(f"Available columns: {list(df.columns)}")
            return df  # Return what we have
        
        # Process estimated job costs
        df['estimated_job_costs'] = pd.to_numeric(df['estimated_job_costs'], errors='coerce')
        
        # Filter for high-value permits
        high_value_df = df[df['estimated_job_costs'] > min_cost].copy()
        
        # Filter by date if issued_date is available
        if 'issued_date' in df.columns:
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            high_value_df = high_value_df[high_value_df['issued_date'] >= cutoff_date]
        
        print(f"💰 Found {len(high_value_df)} permits over ${min_cost:,}")
        
        if len(high_value_df) > 0:
            total_value = high_value_df['estimated_job_costs'].sum()
            avg_value = high_value_df['estimated_job_costs'].mean()
            max_value = high_value_df['estimated_job_costs'].max()
            
            print(f"💸 Total value: ${total_value:,.0f}")
            print(f"📊 Average cost: ${avg_value:,.0f}")
            print(f"🏆 Highest cost: ${max_value:,.0f}")
            
            # Show borough breakdown
            if 'borough' in high_value_df.columns:
                borough_counts = high_value_df['borough'].value_counts()
                print(f"\n🏙️  By Borough:")
                for borough, count in borough_counts.items():
                    print(f"   {borough}: {count} permits")
        
        return high_value_df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return pd.DataFrame()

def main():
    """Main execution function"""
    
    # Fetch high-value permits
    df = get_nyc_high_value_permits(min_cost=1000000, days_back=60, limit=500)
    
    if len(df) > 0:
        # Save to CSV
        output_file = f"nyc_permits_over_1M_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Saved {len(df)} high-value permits to {output_file}")
        
        # Show sample data
        display_columns = []
        priority_columns = ['job_filing_number', 'borough', 'street_name', 'house_no', 
                          'estimated_job_costs', 'work_type', 'issued_date', 'job_description']
        
        for col in priority_columns:
            if col in df.columns:
                display_columns.append(col)
        
        if display_columns:
            print(f"\n🔍 Sample data ({len(display_columns)} columns shown):")
            sample_df = df[display_columns].head()
            
            # Format the estimated_job_costs column for better display
            if 'estimated_job_costs' in sample_df.columns:
                sample_df = sample_df.copy()
                sample_df['estimated_job_costs'] = sample_df['estimated_job_costs'].apply(
                    lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A"
                )
            
            print(sample_df.to_string(index=False, max_colwidth=30))
        
        print(f"\n📁 Full data saved to: {output_file}")
        
    else:
        print("\n⚠️  No high-value permits found in the specified criteria")

if __name__ == "__main__":
    main()