from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

from data_pipeline import DataPipeline
from analytics_engine import AnalyticsEngine
from risk_engine import RiskEngine
from recommendation_engine import RecommendationEngine

app = FastAPI(title="NI³S - National Identity Inclusion Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:5173",  # Vite local
        "https://*.vercel.app",   # Vercel deployments
    ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = None
analytics = None
risk_engine = None
recommendation_engine = None

@app.on_event("startup")
async def startup_event():
    global pipeline, analytics, risk_engine, recommendation_engine
    print("Initializing NI³S Backend System...")
    
    pipeline = DataPipeline()
    pipeline.load_all_datasets()
    pipeline.merge_datasets()
    
    analytics = AnalyticsEngine(pipeline.master_data)
    risk_engine = RiskEngine(analytics)
    recommendation_engine = RecommendationEngine()
    
    print("System initialization complete.")

@app.get("/")
def root():
    return {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/api/national/overview")
def get_national_overview():
    if analytics is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    if analytics is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    if analytics is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    if analytics is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    if analytics is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
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
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    if risk_engine is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    if risk_engine is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)