"""
Pre-process NI³S data to speed up server startup.

Run this script LOCALLY (not on Render) to generate processed_data.pkl
Then commit and push processed_data.pkl to your repo.
"""

import pickle
from pathlib import Path
from data_pipeline import DataPipeline
from analytics_engine import AnalyticsEngine

def main():
    print("=" * 60)
    print("NI³S Data Pre-processing Script")
    print("=" * 60)
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        print("ERROR: 'data' directory not found!")
        print("Make sure you run this script from the project root.")
        return
    
    # Load and process data
    print("\n1. Loading CSV files...")
    pipeline = DataPipeline()
    pipeline.load_all_datasets()
    
    print("\n2. Merging datasets...")
    pipeline.merge_datasets()
    
    print("\n3. Computing analytics...")
    analytics = AnalyticsEngine(pipeline.master_data)
    
    # Prepare data for pickling
    print("\n4. Preparing data for export...")
    processed_data = {
        'master_data': pipeline.master_data,
        'district_features': analytics.district_features
    }
    
    # Save to pickle file
    output_file = data_dir / "processed_data.pkl"
    print(f"\n5. Saving to {output_file}...")
    
    with open(output_file, 'wb') as f:
        pickle.dump(processed_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Check file size
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"\n✓ Success! Processed data saved.")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Location: {output_file}")
   

if __name__ == "__main__":
    main()