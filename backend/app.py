from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
import sys
import traceback

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

pipeline = None
analytics = None
risk_engine = None
recommendation_engine = None
initialization_error = None

@app.on_event("startup")
async def startup_event():
    global pipeline, analytics, risk_engine, recommendation_engine, initialization_error
    
    print("="*60)
    print("Starting NI³S Backend System Initialization...")
    print("="*60)
    
    # Debug info
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Directory contents: {os.listdir('.')}")
    
    # Check if data directory exists
    data_dir = "data"
    if os.path.exists(data_dir):
        print(f"\n✓ Data directory found at: {os.path.abspath(data_dir)}")
        print(f"  Contents: {os.listdir(data_dir)}")
    else:
        print(f"\n✗ Data directory NOT found!")
        print(f"  Looking for: {os.path.abspath(data_dir)}")
    
    try:
        print("\nInitializing Data Pipeline...")
        pipeline = DataPipeline()
        
        print("Loading datasets...")
        pipeline.load_all_datasets()
        
        print("Merging datasets...")
        pipeline.merge_datasets()
        
        print("Initializing Analytics Engine...")
        analytics = AnalyticsEngine(pipeline.master_data)
        
        print("Initializing Risk Engine...")
        risk_engine = RiskEngine(analytics)
        
        print("Initializing Recommendation Engine...")
        recommendation_engine = RecommendationEngine()
        
        print("\n" + "="*60)
        print("✓ System initialization complete successfully!")
        print("="*60)
        
    except FileNotFoundError as e:
        initialization_error = f"Data files not found: {str(e)}"
        print(f"\n✗ ERROR: {initialization_error}")
        print(f"Stack trace:\n{traceback.format_exc()}")
        print("\nThe API will start but endpoints will return 503 errors.")
        print("Please ensure all required CSV files are in the data/ directory.")
        
    except Exception as e:
        initialization_error = f"Initialization failed: {str(e)}"
        print(f"\n✗ ERROR: {initialization_error}")
        print(f"Stack trace:\n{traceback.format_exc()}")
        print("\nThe API will start but endpoints will return 503 errors.")

@app.get("/")
def root():
    return {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": "operational" if analytics is not None else "degraded",
        "version": "1.0.0",
        "initialization_error": initialization_error
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    if analytics is None:
        return {
            "status": "unhealthy",
            "error": initialization_error or "System not initialized",
            "components": {
                "pipeline": pipeline is not None,
                "analytics": analytics is not None,
                "risk_engine": risk_engine is not None,
                "recommendation_engine": recommendation_engine is not None
            }
        }
    
    return {
        "status": "healthy",
        "components": {
            "pipeline": True,
            "analytics": True,
            "risk_engine": True,
            "recommendation_engine": True
        }
    }

@app.get("/api/national/overview")
def get_national_overview():
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
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
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)