import pickle
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import os
from pathlib import Path

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
analytics = None
risk_engine = None
recommendation_engine = None
initialization_error = None

@app.on_event("startup")
async def startup_event():
    """Load pre-processed data on startup - FAST!"""
    global analytics, risk_engine, recommendation_engine, initialization_error
    
    try:
        print("=== Loading NI³S Pre-processed Data ===")
        
        pickle_file = Path("data/processed_data.pkl")
        
        if not pickle_file.exists():
            raise FileNotFoundError(
                "Processed data file not found. "
                "Please run preprocess_data.py locally and upload processed_data.pkl"
            )
        
        # Load pre-processed data (should be very fast - seconds instead of minutes)
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        print("  ✓ Loaded processed data")
        
        # Initialize analytics with pre-loaded data
        analytics = AnalyticsEngine(data['master_data'])
        analytics.district_features = data['district_features']
        
        print("  ✓ Analytics engine initialized")
        
        # Initialize other engines
        risk_engine = RiskEngine(analytics)
        print("  ✓ Risk engine initialized")
        
        recommendation_engine = RecommendationEngine()
        print("  ✓ Recommendation engine initialized")
        
        print("=== NI³S System Ready! ===")
        
    except Exception as e:
        error_msg = f"Initialization error: {str(e)}"
        print(f"=== ERROR: {error_msg} ===")
        initialization_error = error_msg
        # Don't raise - let the server start but endpoints will return 503

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": "operational" if analytics is not None else "initializing" if initialization_error is None else "error",
        "version": "1.0.0",
        "data_loaded": analytics is not None,
        "error": initialization_error if initialization_error else None
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if analytics is not None else "unhealthy",
        "server": "running",
        "data_loaded": analytics is not None,
        "error": initialization_error if initialization_error else None
    }

@app.get("/api/national/overview")
def get_national_overview():
    if analytics is None:
        if initialization_error:
            raise HTTPException(
                status_code=503, 
                detail=f"System initialization failed: {initialization_error}"
            )
        raise HTTPException(
            status_code=503, 
            detail="System is still initializing"
        )
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    if analytics is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
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
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    if risk_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        if initialization_error:
            raise HTTPException(status_code=503, detail=f"System initialization failed: {initialization_error}")
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)