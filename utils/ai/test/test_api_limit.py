"""
Test script to check if Gemini API has reached rate limit
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_gemini_api():
    """Test Gemini API and check for rate limit errors"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    print(f"🔍 Testing Gemini API at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    model = "gemini-2.5-flash-lite"
    base_url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
    
    test_prompt = "Say 'API is working' in one sentence."
    
    try:
        response = requests.post(
            f"{base_url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": test_prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 60)
        
        if response.status_code == 200:
            data = response.json()
            result_text = data['candidates'][0]['content']['parts'][0]['text']
            print("✅ API is WORKING")
            print(f"Response: {result_text}")
            return True
        
        elif response.status_code == 429:
            print("⚠️  RATE LIMIT REACHED (429)")
            print(f"Error: {response.text[:500]}")
            return False
        
        elif response.status_code == 403:
            print("⚠️  FORBIDDEN (403) - Quota exceeded or API key issue")
            print(f"Error: {response.text[:500]}")
            return False
        
        elif response.status_code == 400:
            print("❌ BAD REQUEST (400) - Check API format")
            print(f"Error: {response.text[:500]}")
            return False
        
        else:
            print(f"❌ Unexpected Status Code: {response.status_code}")
            print(f"Error: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  API Request Timeout - Server not responding")
        return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_multiple_calls():
    """Test multiple API calls to check rate limit threshold"""
    
    print("\n🔄 Testing Multiple API Calls...")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    model = "gemini-2.5-flash-lite"
    base_url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
    
    successful_calls = 0
    failed_calls = 0
    
    for i in range(1, 6):  # Test 5 calls
        try:
            print(f"\n[Call {i}] Testing...", end=" ")
            
            response = requests.post(
                f"{base_url}?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": f"Test call number {i}"}]}],
                    "generationConfig": {
                        "temperature": 0.5,
                        "maxOutputTokens": 50
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ Success")
                successful_calls += 1
            elif response.status_code == 429:
                print("⚠️  Rate Limited (429)")
                failed_calls += 1
            else:
                print(f"❌ Error ({response.status_code})")
                failed_calls += 1
        
        except Exception as e:
            print(f"❌ Exception: {str(e)[:50]}")
            failed_calls += 1
    
    print("\n" + "=" * 60)
    print(f"Results: ✅ {successful_calls}/5 successful | ❌ {failed_calls}/5 failed")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GEMINI API RATE LIMIT TEST")
    print("=" * 60)
    
    result = test_gemini_api()
    
    if result:
        test_multiple_calls()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60 + "\n")
