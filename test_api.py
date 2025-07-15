import requests
import json

def test_chat_endpoint():
    url = "https://backend-kapwa.onrender.com/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
    
    print("Testing /chat endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_summarize_endpoint():
    url = "https://backend-kapwa.onrender.com/summarize_chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?", "senderName": "John"},
            {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
            {"role": "user", "content": "What's the weather like?", "senderName": "John"},
            {"role": "assistant", "content": "I don't have access to real-time weather data, but I can help you find weather information."}
        ]
    }
    
    print("\nTesting /summarize_chat endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint()
    test_summarize_endpoint()