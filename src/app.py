"""
Weather Agent API - FastAPI application
Provides REST API for AI-powered weather analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Hugging Face Inference API
from huggingface_hub import InferenceClient

# Import our tools
from tools import BigQueryWeatherTool, WeatherAnalyzer


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ai-weather-analytics")
STATION_ID = os.getenv("WEATHER_STATION_ID", "999999")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("=" * 60)
    print("ERROR: HF_TOKEN not found in environment variables")
    print("=" * 60)
    print("Please set your Hugging Face token in .env file:")
    print("  HF_TOKEN=your_actual_token_here")
    print("\nGet your token at: https://huggingface.co/settings/tokens")
    print("=" * 60)
    raise ValueError("HF_TOKEN environment variable must be set")


# =============================================================================
# Initialize Tools & LLM
# =============================================================================

print("=" * 60)
print("INITIALIZING WEATHER AGENT API")
print("=" * 60)

try:
    # Initialize weather tools
    print(f"✓ Project ID: {PROJECT_ID}")
    print(f"✓ Station ID: {STATION_ID}")
    bq_tool = BigQueryWeatherTool(PROJECT_ID, STATION_ID)
    analyzer = WeatherAnalyzer()
    print("✓ Weather tools initialized")
    
    # Initialize Hugging Face LLM (Llama 3.2)
    llm_client = InferenceClient(token=HF_TOKEN)
    LLM_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
    print(f"✓ LLM initialized: {LLM_MODEL}")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Initialization error: {e}")
    print("=" * 60)
    raise


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Weather Agent API",
    description="AI-powered weather analysis using BigQuery NOAA data and LLM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class AnalysisRequest(BaseModel):
    """Request model for weather analysis"""
    days: int = Field(default=30, ge=7, le=90, description="Number of days to analyze (7-90)")
    custom_question: Optional[str] = Field(default=None, description="Optional custom question about weather")


class AnalysisResponse(BaseModel):
    """Response model for weather analysis"""
    station_id: str
    days_analyzed: int
    statistics: dict
    llm_analysis: str
    timestamp: str
    model_used: str


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Weather Agent API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    try:
        # Test BigQuery connection
        test_data = bq_tool.get_recent_weather(days=1)
        bq_status = "connected" if test_data and test_data != "[]" else "no data"
    except Exception as e:
        bq_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bigquery_connection": bq_status,
        "llm_model": LLM_MODEL,
        "station_id": STATION_ID,
        "project_id": PROJECT_ID
    }


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_weather(request: AnalysisRequest):
    """
    Perform AI-powered weather analysis
    
    Args:
        request: Analysis parameters (days, optional custom question)
        
    Returns:
        Complete weather analysis with statistics and LLM insights
    """
    try:
        # Step 1: Fetch weather data
        print(f"[API] Fetching {request.days} days of weather data...")
        weather_data = bq_tool.get_recent_weather(days=request.days)
        
        if not weather_data or weather_data == "[]":
            raise HTTPException(
                status_code=404,
                detail=f"No weather data found for station {STATION_ID}"
            )
        
        # Step 2: Calculate statistics
        print("[API] Calculating statistics...")
        stats = analyzer.calculate_statistics(weather_data)
        
        if "error" in stats:
            raise HTTPException(
                status_code=500,
                detail=f"Statistics calculation failed: {stats['error']}"
            )
        
        # Step 3: Generate LLM analysis
        print("[API] Generating AI analysis...")
        
        # Build prompt
        if request.custom_question:
            prompt = f"""You are a professional weather analyst. Answer the following question based on the weather data and statistics:

QUESTION: {request.custom_question}

STATION: {STATION_ID}
TIME PERIOD: Last {request.days} days

CALCULATED STATISTICS:
{json.dumps(stats, indent=2)}

RECENT DAILY DATA:
{weather_data[:500]}...

Provide a clear, concise answer (3-4 sentences) with specific numbers from the data."""
        else:
            prompt = f"""You are a professional weather analyst. Analyze the following weather data and statistics:

STATION: {STATION_ID}
TIME PERIOD: Last {request.days} days

CALCULATED STATISTICS:
{json.dumps(stats, indent=2)}

RECENT DAILY DATA:
{weather_data[:500]}...

Provide a concise professional weather analysis covering:
1. Current temperature conditions and comparison to average
2. Any anomalies or unusual patterns (use z-score and changes)
3. Overall weather trends
4. Brief forecast implications

Keep your response to 4-5 sentences, be specific with numbers."""
        
        # Call Hugging Face LLM (UPDATED METHOD)
        try:
            response = llm_client.text_generation(
                prompt,
                model=LLM_MODEL,
                max_new_tokens=500,
                temperature=0.7,
                return_full_text=False
            )
            llm_analysis = response
        except Exception as llm_error:
            print(f"[API] LLM Error: {llm_error}")
            # Fallback to basic analysis if LLM fails
            llm_analysis = f"Current temperature is {stats['current_temp']}°C, compared to average of {stats['mean_temp']}°C. "
            if stats['anomaly_detected']:
                llm_analysis += f"Anomaly detected with z-score of {stats['z_score']}. "
            llm_analysis += f"Day-over-day change: {stats['day_over_day_change']}°C."
        
        print("[API] ✓ Analysis complete")
        
        # Return response
        return AnalysisResponse(
            station_id=STATION_ID,
            days_analyzed=request.days,
            statistics=stats,
            llm_analysis=llm_analysis,
            timestamp=datetime.now().isoformat(),
            model_used=LLM_MODEL
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ✗ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/station-info")
def get_station_info():
    """Get information about the current weather station"""
    return {
        "station_id": STATION_ID,
        "project_id": PROJECT_ID,
        "data_source": "NOAA GSOD (BigQuery public dataset)",
        "dataset": "bigquery-public-data.noaa_gsod.gsod2023"
    }


# =============================================================================
# Startup event
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    print("\n🚀 Weather Agent API is running!")
    print(f"📍 Docs: http://localhost:8000/docs")
    print(f"🔍 Health: http://localhost:8000/health\n")


# =============================================================================
# Run the app (for local development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    print(f"\nStarting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
