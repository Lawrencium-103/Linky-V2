"""
Database Integration with Supabase
Handles all database operations for LinkyGen V2
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Global state for bypass mode
_bypass_enabled = os.getenv("BYPASS_DATABASE", "false").lower() == "true"

def is_bypass_active() -> bool:
    """Check if bypass mode is active."""
    global _bypass_enabled
    return _bypass_enabled

# In-memory storage for bypass mode
_bypass_storage = {
    "access_codes": [],
    "users": {},
    "metrics": {},
    "posts": []
}

STORAGE_FILE = "local_storage.json"

def _load_storage():
    import json
    global _bypass_storage
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)
                # Merge with default to ensure required keys exist
                for key in _bypass_storage:
                    if key in data:
                        _bypass_storage[key] = data[key]
        except Exception as e:
            print(f"Error loading local storage: {e}")

def _save_storage():
    import json
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(_bypass_storage, f)
    except Exception as e:
        print(f"Error saving local storage: {e}")

def enable_bypass():
    """Enable bypass mode permanently for this session."""
    global _bypass_enabled
    if not _bypass_enabled:
        print("🔄 Permanently enabling BYPASS_MODE due to connection failure...")
        _bypass_enabled = True
        _load_storage()

# Initialize Supabase client
try:
    if SUPABASE_URL and SUPABASE_KEY and not _bypass_enabled:
        # Check connectivity before initializing or set a very short timeout if possible
        # Supabase-py doesn't have an explicit timeout in create_client, but we can verify
        # DNS Resolution here to fail fast
        import socket
        host = SUPABASE_URL.split("//")[-1].split("/")[0]
        socket.gethostbyname_ex(host) # This will throw Gaierror fast if unreachable
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        enable_bypass()
except Exception as e:
    print(f"⚠️ Supabase connectivity warning: {str(e)}")
    enable_bypass()

# Load initial storage if bypass already active
if is_bypass_active():
    _load_storage()


def validate_access_code(code: str) -> bool:
    """
    Validate if an access code is valid and unused.
    
    Args:
        code: 10-character alphanumeric access code
        
    Returns:
        True if code is valid and unused, False otherwise
    """
    try:
        if is_bypass_active():
            # In bypass mode, check against in-memory list
            return code in _bypass_storage["access_codes"]
        
        response = supabase.table("access_codes").select("*").eq("code", code).eq("is_used", False).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error validating access code: {str(e)}")
        # If it's a connection error, switch to bypass permanently
        if "getaddrinfo" in str(e) or "connection" in str(e).lower():
            enable_bypass()
            return code in _bypass_storage["access_codes"]
        # Fallback to empty for safety
        return False


def mark_code_as_used(code: str, user_id: str) -> bool:
    """
    Mark an access code as used by a specific user.
    
    Args:
        code: Access code to mark as used
        user_id: User ID who used the code
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if is_bypass_active():
            # In bypass mode, just return True (codes can be reused)
            return True
        
        supabase.table("access_codes").update({
            "is_used": True,
            "used_by": user_id
        }).eq("code", code).execute()
        return True
    except Exception as e:
        print(f"Error marking code as used: {str(e)}")
        if "connection" in str(e).lower() or "getaddrinfo" in str(e):
            enable_bypass()
        return False


def create_or_get_user(user_id: str, email: Optional[str] = None, country: Optional[str] = None, timezone: Optional[str] = None) -> Optional[Dict]:
    """
    Create a new user or get existing user data.
    
    Args:
        user_id: Unique user identifier (session ID)
        email: User email (optional)
        country: User country code
        timezone: User timezone
        
    Returns:
        User data dict or None if error
    """
    try:
        # Check if user exists
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if len(response.data) > 0:
            return response.data[0]
        
        # Create new user
        user_data = {
            "id": user_id,
            "email": email,
            "country": country,
            "timezone": timezone,
            "is_subscribed": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error creating/getting user: {str(e)}")
        return None


def get_user_metrics(user_id: str) -> Dict[str, int]:
    """
    Get metrics for a specific user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict with metrics (posts_generated, likes_count, shares_count)
    """
    try:
        if is_bypass_active():
            # In bypass mode, use in-memory storage
            if user_id not in _bypass_storage["metrics"]:
                _bypass_storage["metrics"][user_id] = {
                    "posts_generated": 0,
                    "likes_count": 0,
                    "shares_count": 0
                }
            return _bypass_storage["metrics"][user_id]
        
        response = supabase.table("metrics").select("*").eq("user_id", user_id).execute()
        
        if len(response.data) > 0:
            return response.data[0]
        
        # Create initial metrics
        initial_metrics = {
            "user_id": user_id,
            "posts_generated": 0,
            "likes_count": 0,
            "shares_count": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("metrics").insert(initial_metrics).execute()
        return response.data[0] if response.data else initial_metrics
        
    except Exception as e:
        print(f"Error getting user metrics: {str(e)}")
        if "connection" in str(e).lower() or "getaddrinfo" in str(e):
            enable_bypass()
            return get_user_metrics(user_id)
        return {"posts_generated": 0, "likes_count": 0, "shares_count": 0}


def increment_metric(user_id: str, metric_name: str, increment: int = 1) -> bool:
    """
    Increment a specific metric for a user.
    
    Args:
        user_id: User identifier
        metric_name: Name of metric to increment (posts_generated, likes_count, shares_count)
        increment: Amount to increment by (default 1)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if is_bypass_active():
            # In bypass mode, update in-memory storage
            metrics = get_user_metrics(user_id)
            metrics[metric_name] = metrics.get(metric_name, 0) + increment
            _save_storage()
            return True
        
        # Get current metrics
        current_metrics = get_user_metrics(user_id)
        current_value = current_metrics.get(metric_name, 0)
        
        # Update metric
        supabase.table("metrics").update({
            metric_name: current_value + increment,
            "last_updated": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
        return True
        
    except Exception as e:
        print(f"Error incrementing metric: {str(e)}")
        return False


def save_post(user_id: str, content: str, word_count: int) -> bool:
    """
    Save a generated post to the database.
    
    Args:
        user_id: User identifier
        content: Post content
        word_count: Number of words in post
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if is_bypass_active():
            # In bypass mode, save to in-memory storage
            _bypass_storage["posts"].append({
                "user_id": user_id,
                "content": content,
                "word_count": word_count
            })
            increment_metric(user_id, "posts_generated")
            _save_storage()
            return True
        
        post_data = {
            "user_id": user_id,
            "content": content,
            "word_count": word_count,
            "created_at": datetime.utcnow().isoformat(),
            "liked": False,
            "shared": False
        }
        
        supabase.table("posts").insert(post_data).execute()
        
        # Increment posts_generated metric
        increment_metric(user_id, "posts_generated")
        
        return True
        
    except Exception as e:
        print(f"Error saving post: {str(e)}")
        return False


def get_user_post_count(user_id: str) -> int:
    """
    Get the number of posts a user has generated.
    
    Args:
        user_id: User identifier
        
    Returns:
        Number of posts generated
    """
    try:
        if is_bypass_active():
            # In bypass mode, count from in-memory storage
            return len([p for p in _bypass_storage["posts"] if p["user_id"] == user_id])
        
        response = supabase.table("posts").select("id", count="exact").eq("user_id", user_id).execute()
        return response.count if response.count else 0
    except Exception as e:
        print(f"Error getting post count: {str(e)}")
        return 0


def initialize_database_tables():
    """
    SQL commands to create database tables in Supabase.
    Run these in the Supabase SQL editor.
    """
    sql_commands = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email TEXT UNIQUE,
        access_code TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        country TEXT,
        timezone TEXT,
        is_subscribed BOOLEAN DEFAULT FALSE
    );

    -- Metrics table
    CREATE TABLE IF NOT EXISTS metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        posts_generated INTEGER DEFAULT 0,
        likes_count INTEGER DEFAULT 0,
        shares_count INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT NOW(),
        UNIQUE(user_id)
    );

    -- Posts table
    CREATE TABLE IF NOT EXISTS posts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        word_count INTEGER,
        created_at TIMESTAMP DEFAULT NOW(),
        liked BOOLEAN DEFAULT FALSE,
        shared BOOLEAN DEFAULT FALSE
    );

    -- Access codes table
    CREATE TABLE IF NOT EXISTS access_codes (
        code TEXT PRIMARY KEY,
        is_used BOOLEAN DEFAULT FALSE,
        used_by UUID REFERENCES users(id),
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Insert initial access codes (None by default)
    -- INSERT INTO access_codes (code) VALUES ('YOUR_CODE_HERE');
    """
    
    return sql_commands


# Export SQL for easy setup
SQL_SETUP = initialize_database_tables()
