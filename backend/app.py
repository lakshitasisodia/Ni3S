from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
import asyncio
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

pipeline = None
analytics = None
risk_engine = None
recommendation_engine = None
initialization_error = None

async def initialize_system():
    """Initialize system asynchronously without blocking startup"""
    global pipeline, analytics, risk_engine, recommendation_engine, initialization_error
    
    try:
        print("Initializing NI³S Backend System...")
        
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
        
        print("✓ System initialization complete.")
        
    except FileNotFoundError as e:
        error_msg = str(e)
        print(f"⚠ WARNING: {error_msg}")
        print("System will start but endpoints will return 503 errors.")
        print("To fix this:")
        print("  1. Create a 'data/' directory in your project root")
        print("  2. Add the required CSV files:")
        print("     - DEMOGRAPHIC_1.csv through DEMOGRAPHIC_5.csv")
        print("     - ENROLLMENT_1.csv through ENROLLMENT_3.csv")
        initialization_error = error_msg
        
    except Exception as e:
        error_msg = f"Initialization error: {str(e)}"
        print(f"✗ ERROR: {error_msg}")
        initialization_error = error_msg

@app.on_event("startup")
async def startup_event():
    """Non-blocking startup - allows server to start even if data load fails"""
    print("Starting FastAPI server...")
    print("Server is ready to accept requests")
    
    # Initialize system in background (don't await - let it run async)
    asyncio.create_task(initialize_system())

@app.get("/")
def root():
    status = "operational" if analytics is not None else "initializing" if initialization_error is None else "data not loaded"
    
    response = {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": status,
        "version": "1.0.0",
        "data_loaded": analytics is not None
    }
    
    if initialization_error:
        response["error"] = initialization_error
        response["instructions"] = "Upload CSV files to the 'data/' directory and restart the service"
    
    return response

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "data_loaded": analytics is not None,
        "error": initialization_error
    }

@app.get("/api/national/overview")
def get_national_overview():
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing, please try again in a moment")
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
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
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System not initialized: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)