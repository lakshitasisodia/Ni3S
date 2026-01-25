from copyreg import pickle
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
from pathlib import Path

from data_pipeline import DataPipeline
from analytics_engine import AnalyticsEngine
from risk_engine import RiskEngine
from recommendation_engine import RecommendationEngine

app = FastAPI(title="NI³S - National Identity Inclusion Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
pipeline = None
analytics = None
risk_engine = None
recommendation_engine = None
initialization_error = None
is_initializing = False

def lazy_init():
    """Lazy initialization - only runs when first API call is made"""
    global pipeline, analytics, risk_engine, recommendation_engine, initialization_error, is_initializing
    
    # If already initialized or currently initializing, return
    if analytics is not None or is_initializing:
        return
    
    is_initializing = True
    
    try:
        print("=== Starting NI³S Data Initialization ===")
        
        # Check if data directory exists
        data_dir = Path("data")
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory '{data_dir}' not found")
        
        # Check for required files
        required_files = [
            "DEMOGRAPHIC_1.csv", "DEMOGRAPHIC_2.csv", "DEMOGRAPHIC_3.csv",
            "DEMOGRAPHIC_4.csv", "DEMOGRAPHIC_5.csv",
            "ENROLLMENT_1.csv", "ENROLLMENT_2.csv", "ENROLLMENT_3.csv"
        ]
        
        missing_files = [f for f in required_files if not (data_dir / f).exists()]
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")
        
        pipeline = DataPipeline()
        pipeline.load_all_datasets()
        pipeline.merge_datasets()
        
        analytics = AnalyticsEngine(pipeline.master_data)
        risk_engine = RiskEngine(analytics)
        recommendation_engine = RecommendationEngine()
        
        print("=== NI³S Initialization Complete ===")
        
    except Exception as e:
        error_msg = f"Initialization error: {str(e)}"
        print(f"=== ERROR: {error_msg} ===")
        initialization_error = error_msg
    finally:
        is_initializing = False

@app.on_event("startup")
async def startup_event():
    global pipeline, analytics, risk_engine, recommendation_engine
    
    try:
        print("Loading pre-processed data...")
        with open('preprocess.py', 'rb') as f:
            data = pickle.load(f)
        
        # This will be MUCH faster - seconds instead of minutes
        analytics = AnalyticsEngine(data['master_data'])
        analytics.district_features = data['district_features']
        risk_engine = RiskEngine(analytics)
        recommendation_engine = RecommendationEngine()
        
        print("System ready!")
    except Exception as e:
        print(f"Error: {e}")

@app.get("/")
def root():
    """Root endpoint - doesn't trigger initialization"""
    return {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": "ready" if analytics is not None else "not initialized",
        "version": "1.0.0",
        "message": "Call any API endpoint to trigger data initialization"
    }

@app.get("/health")
def health_check():
    """Health check endpoint - doesn't trigger initialization"""
    return {
        "status": "healthy",
        "server": "running",
        "data_loaded": analytics is not None
    }

@app.get("/api/national/overview")
def get_national_overview():
    lazy_init()
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing, please try again")
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    lazy_init()
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    lazy_init()
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    lazy_init()
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    lazy_init()
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    lazy_init()
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    district_data = analytics.get_district_analytics(state_name, district_name)
    risk_score = risk_engine.get_district_risk_score(state_name, district_name)
    recommendations = recommendation_engine.generate_recommendations(district_data, risk_score)
    
    return {
        "analytics": district_data,
        "risk": risk_score,
        "recommendations": recommendations
    }

@app.get("/api/risk/rankings")
def get_risk_rankings(limit: Optional[int] = 50):
    lazy_init()
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    lazy_init()
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    lazy_init()
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    lazy_init()
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    lazy_init()
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is initializing")
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)