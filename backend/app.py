from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
import os
import sys
import traceback
import asyncio
from contextlib import asynccontextmanager

# Import modules but don't load data yet
from data_pipeline import DataPipeline
from analytics_engine import AnalyticsEngine
from risk_engine import RiskEngine
from recommendation_engine import RecommendationEngine

# Global variables
pipeline = None
analytics = None
risk_engine = None
recommendation_engine = None
initialization_error = None
is_initializing = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global pipeline, analytics, risk_engine, recommendation_engine, initialization_error, is_initializing
    
    # Start initialization in background
    is_initializing = True
    asyncio.create_task(initialize_system())
    
    # Yield immediately so server can start
    yield
    
    # Shutdown (cleanup if needed)
    pass

async def initialize_system():
    """Initialize system in background without blocking server startup"""
    global pipeline, analytics, risk_engine, recommendation_engine, initialization_error, is_initializing
    
    print("="*60)
    print("Starting NI³S Backend System Initialization...")
    print("="*60)
    
    # Debug info
    print(f"\nCurrent working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    try:
        # List directory contents
        print(f"\nRoot directory contents:")
        for item in os.listdir('.'):
            print(f"  - {item}")
        
        # Check if data directory exists
        data_dir = "data"
        if os.path.exists(data_dir):
            print(f"\n✓ Data directory found at: {os.path.abspath(data_dir)}")
            data_files = os.listdir(data_dir)
            print(f"  Number of files: {len(data_files)}")
            print(f"  Files:")
            for f in sorted(data_files):
                file_path = os.path.join(data_dir, f)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"    - {f} ({size_mb:.2f} MB)")
        else:
            raise FileNotFoundError(f"Data directory not found at: {os.path.abspath(data_dir)}")
        
        print("\n" + "-"*60)
        print("Initializing Data Pipeline...")
        pipeline = DataPipeline()
        
        print("Loading datasets (this may take a while)...")
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
        
    except Exception as e:
        initialization_error = f"Initialization failed: {str(e)}"
        print(f"\n✗ ERROR: {initialization_error}")
        print(f"Error type: {type(e).__name__}")
        print(f"Stack trace:\n{traceback.format_exc()}")
    
    finally:
        is_initializing = False

# Create app with lifespan
app = FastAPI(
    title="NI³S - National Identity Inclusion Intelligence System",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "system": "NI³S - National Identity Inclusion Intelligence System",
        "status": "operational" if analytics is not None else ("initializing" if is_initializing else "degraded"),
        "version": "1.0.0",
        "initialization_error": initialization_error,
        "components_ready": {
            "pipeline": pipeline is not None,
            "analytics": analytics is not None,
            "risk_engine": risk_engine is not None,
            "recommendation_engine": recommendation_engine is not None
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    if is_initializing:
        return {
            "status": "initializing",
            "message": "System is still loading data. Please wait..."
        }
    
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
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_national_overview()

@app.get("/api/national/trends")
def get_national_trends():
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_national_trends()

@app.get("/api/states")
def get_states():
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_states_list()

@app.get("/api/states/{state_name}/districts")
def get_districts(state_name: str):
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_districts_by_state(state_name)

@app.get("/api/states/{state_name}/overview")
def get_state_overview(state_name: str):
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return analytics.get_state_overview(state_name)

@app.get("/api/districts/{state_name}/{district_name}")
def get_district_analytics(state_name: str, district_name: str):
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
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
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_top_risk_districts(limit)

@app.get("/api/risk/heatmap")
def get_risk_heatmap():
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_heatmap_data()

@app.get("/api/risk/distribution")
def get_risk_distribution():
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if risk_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return risk_engine.get_risk_distribution()

@app.get("/api/insights/policy")
def get_policy_insights():
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return recommendation_engine.generate_policy_insights(analytics, risk_engine)

@app.get("/api/insights/state/{state_name}")
def get_state_insights(state_name: str):
    if is_initializing:
        raise HTTPException(status_code=503, detail="System is still initializing. Please wait...")
    
    if analytics is None or risk_engine is None or recommendation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail=f"System not initialized: {initialization_error}"
        )
    
    return recommendation_engine.generate_state_insights(state_name, analytics, risk_engine)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)