
import requests
import time

def check_geo():
    print("Checking Geolocation Service...")
    start = time.time()
    try:
        r = requests.get("https://ipapi.co/json/", timeout=5)
        print(f"Geo Status: {r.status_code} in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"Geo Error: {e}")

def check_supabase():
    print("\nChecking Supabase Connectivity...")
    import os
    from dotenv import load_dotenv
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    start = time.time()
    try:
        r = requests.get(f"{url}/rest/v1/posts?select=count", headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=5)
        print(f"Supabase Status: {r.status_code} in {time.time()-start:.2f}s")
    except Exception as e:
        print(f"Supabase Error: {e}")

if __name__ == "__main__":
    check_geo()
    check_supabase()
