# preprocess_data.py
import pandas as pd
from data_pipeline import DataPipeline
from analytics_engine import AnalyticsEngine
import pickle

print("Pre-processing data...")
pipeline = DataPipeline()
pipeline.load_all_datasets()
pipeline.merge_datasets()

analytics = AnalyticsEngine(pipeline.master_data)

# Save processed data
print("Saving processed data...")
with open('data/processed_data.pkl', 'wb') as f:
    pickle.dump({
        'master_data': pipeline.master_data,
        'district_features': analytics.district_features
    }, f)

print("Done! Processed data saved.")