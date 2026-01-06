"""
Test deployed Cloud Run API
"""

import requests
import json

# REPLACE WITH YOUR ACTUAL CLOUD RUN URL
API_URL = "https://weather-agent-api-620429941346.asia-east1.run.app"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check (Cloud)")
    print("="*60)
    
    response = requests.get(f"{API_URL}/health", timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_analyze():
    """Test analysis endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Weather Analysis (Cloud)")
    print("="*60)
    
    payload = {"days": 30}
    
    response = requests.post(
        f"{API_URL}/analyze", 
        json=payload,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Cloud API Works!")
        print(f"\nStation: {data['station_id']}")
        print(f"Days: {data['days_analyzed']}")
        print(f"\nStatistics:")
        for key, value in list(data['statistics'].items())[:5]:
            print(f"  {key}: {value}")
        print(f"\nLLM Analysis:")
        print(f"{data['llm_analysis'][:200]}...")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("="*60)
    print("Testing Cloud Run Deployment")
    print("="*60)
    
    test_health()
    test_analyze()
    
    print("\n" + "="*60)
    print("✓ Cloud API Testing Complete!")
    print("="*60)
