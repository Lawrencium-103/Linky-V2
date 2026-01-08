"""
Test script to debug the Linky workflow
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Test 1: Check environment variables
print("=" * 50)
print("TEST 1: Environment Variables")
print("=" * 50)
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    print(f"[OK] OPENROUTER_API_KEY is set (length: {len(api_key)})")
else:
    print("[ERROR] OPENROUTER_API_KEY is NOT set")

# Test 2: Test OpenRouter API call
print("\n" + "=" * 50)
print("TEST 2: OpenRouter API Call")
print("=" * 50)

import llm_utils

try:
    response = llm_utils.call_openrouter(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Hello, Linky!' in exactly those words.",
        max_tokens=50,
        temperature=0.7
    )
    
    if response:
        print(f"[OK] API call successful!")
        print(f"Response: {response}")
    else:
        print("[ERROR] API call returned None")
except Exception as e:
    print(f"[ERROR] API call failed with error: {str(e)}")

# Test 3: Test workflow with minimal state
print("\n" + "=" * 50)
print("TEST 3: Minimal Workflow Test")
print("=" * 50)

from linky_agents import app, LinkyState

initial_state: LinkyState = {
    "topic": "AI in healthcare",
    "custom_content": None,
    "tone": "Practical Educator",
    "content_type": ["News Breakdown"],
    "content_length": 500,
    "engagement_level": "Medium",
    "narrative_patterns": ["Storytelling Arc"],
    "latest_news_and_stats": None,
    "key_insights": None,
    "viral_elements": None,
    "sentiment_analysis": None,
    "raw_linkedin_post": None,
    "final_linkedin_post": None,
    "status_message": None,
    "error_message": None
}

try:
    print("Running workflow...")
    final_state = None
    for output in app.stream(initial_state):
        node_name = list(output.keys())[0]
        state = output[node_name]
        print(f"\n-> Node: {node_name}")
        if state.get("status_message"):
            print(f"  Status: {state['status_message']}")
        if state.get("error_message"):
            print(f"  ERROR: {state['error_message']}")
        final_state = state
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    
    if final_state:
        if final_state.get("final_linkedin_post"):
            print("[OK] Post generated successfully!")
            print(f"\nPost preview:\n{final_state['final_linkedin_post'][:200]}...")
        else:
            print("[ERROR] No post generated")
            if final_state.get("error_message"):
                print(f"Error: {final_state['error_message']}")
    
except Exception as e:
    print(f"[ERROR] Workflow failed: {str(e)}")
    import traceback
    traceback.print_exc()
