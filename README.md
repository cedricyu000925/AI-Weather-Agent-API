# AI Weather Agent API 🌦️🤖
A production-ready REST API that combines real-time weather data from NOAA's Global Summary of the Day dataset with AI-powered analysis using Large Language Models. Built with FastAPI, Google BigQuery, and Hugging Face LLMs, deployed on Google Cloud Run.

[![Python](https://img.shields.io/badge/Python-3.14.2-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-orange.svg)](https://cloud.google.com/run)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Live API:** [https://weather-agent-api-620429941346.asia-east1.run.app](https://weather-agent-api-620429941346.asia-east1.run.app)  
**API Documentation:** [https://weather-agent-api-620429941346.asia-east1.run.app/docs](https://weather-agent-api-620429941346.asia-east1.run.app/docs)

---

## 🎯 Overview

This project demonstrates the integration of multiple cloud services and AI technologies to create an intelligent weather analysis system. The API fetches historical weather data from NOAA's public BigQuery dataset, performs statistical analysis (including anomaly detection), and generates natural language insights using Llama 3.2.

**Key Capabilities:**
- Fetches real-time weather data from BigQuery (NOAA GSOD dataset)
- Calculates statistical metrics (mean, standard deviation, z-scores)
- Detects temperature anomalies and significant weather events
- Generates AI-powered analysis and answers custom weather questions
- Fully containerized and cloud-deployed for global accessibility

---

## ✨ Features

### 🔍 Data Integration
- **Google BigQuery Integration**: Queries NOAA Global Summary of the Day (GSOD) public dataset
- **Real Historical Data**: Access to weather records from weather stations worldwide
- **Efficient Queries**: Optimized SQL queries with proper type casting and filtering

### 📊 Statistical Analysis
- **Temperature Metrics**: Current, mean, min, max, standard deviation
- **Anomaly Detection**: Z-score calculation to identify unusual weather patterns
- **Trend Analysis**: Day-over-day and week-over-week temperature changes
- **Spike Detection**: Automatic flagging of significant temperature variations (>5°C)

### 🤖 AI-Powered Insights
- **LLM Integration**: Uses Hugging Face's Llama 3.2 3B Instruct model
- **Natural Language Analysis**: Generates human-readable weather summaries
- **Custom Queries**: Ask specific questions about weather patterns
- **Context-Aware Responses**: Incorporates statistical data into AI analysis

### 🌐 Production-Ready API
- **FastAPI Framework**: High-performance, modern Python web framework
- **Auto-Generated Documentation**: Interactive Swagger UI and ReDoc
- **CORS Enabled**: Accessible from web applications
- **Error Handling**: Comprehensive exception handling and validation
- **Health Checks**: Built-in health monitoring endpoint

### ☁️ Cloud Deployment
- **Google Cloud Run**: Serverless, auto-scaling deployment
- **Docker Containerization**: Consistent environment across development and production
- **Environment Variables**: Secure configuration management
- **Regional Deployment**: Optimized for Asia-Pacific region (Hong Kong)

---

**Data Flow:**
1. Client sends HTTP request to API endpoint
2. FastAPI receives and validates request
3. BigQuery tool fetches historical weather data
4. Weather analyzer calculates statistical metrics
5. LLM generates natural language insights
6. API returns combined analysis as JSON

---

## 🛠️ Tech Stack

### Backend
- **Python 3.14.2**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and settings management

### Data & Analytics
- **Google Cloud BigQuery**: Data warehouse and query engine
- **NOAA GSOD Dataset**: Global Summary of the Day weather data
- **Statistical Analysis**: Custom Python implementation (z-score, variance)

### AI/ML
- **Hugging Face Hub**: Model hosting and inference
- **Llama 3.2 3B Instruct**: Large Language Model for text generation
- **InferenceClient**: Hugging Face API client

### DevOps & Deployment
- **Docker**: Containerization for consistent deployments
- **Google Cloud Run**: Serverless container platform
- **Google Cloud Build**: Automated build and deployment
- **gcloud CLI**: Command-line interface for GCP

### Development Tools
- **VS Code**: Primary IDE
- **Git/GitHub**: Version control
- **Python-dotenv**: Environment variable management
- **Requests**: HTTP library for testing

---

## 🔌 API Endpoints

### `GET /Health check endpoint`

**Response:**
{
  "status": "online",
  "service": "Weather Agent API",
  "version": "1.0.0",
  "endpoints": {
    "analyze": "/analyze",
    "docs": "/docs",
    "health": "/health"
  }
}

### `GET /health`

<img width="1153" height="122" alt="Screenshot 2026-01-06 151653" src="https://github.com/user-attachments/assets/31d220c9-c6c8-4715-bdb3-4efbacfb46ca" />

### `POST /analyze`
{
  "days": 30,
  "custom_question": "Has there been unusual weather recently?"
}

* `days` (int, 7–90): Number of recent days to analyze.

* `custom_question` (optional string): If provided, the LLM answers this specific question using the statistics and data.

<img width="1155" height="288" alt="Screenshot 2026-01-06 152802" src="https://github.com/user-attachments/assets/986ee13f-9347-46f8-954e-5dae9045ca37" />

### `GET /station-info`

<img width="1152" height="93" alt="Screenshot 2026-01-06 152933" src="https://github.com/user-attachments/assets/aa66122f-3e13-4ebd-b6b3-8b667ccacd65" />
