"""
Metrics Tracking and Analytics
Handles user engagement metrics and analytics display
"""

import streamlit as st
from typing import Dict
import database


def display_metrics_dashboard(user_id: str):
    """
    Display metrics dashboard in the UI.
    
    Args:
        user_id: User identifier
    """
    metrics = database.get_user_metrics(user_id)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
        <h3 style="color: #00B5AD; margin: 0 0 1rem 0; font-size: 1.1rem;">
            📊 Your Impact
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Posts Generated",
            value=metrics.get("posts_generated", 0),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Likes",
            value=metrics.get("likes_count", 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Shares",
            value=metrics.get("shares_count", 0),
            delta=None
        )


def track_like(user_id: str) -> bool:
    """
    Track a like action.
    
    Args:
        user_id: User identifier
        
    Returns:
        True if successful
    """
    return database.increment_metric(user_id, "likes_count")


def track_share(user_id: str) -> bool:
    """
    Track a share action.
    
    Args:
        user_id: User identifier
        
    Returns:
        True if successful
    """
    return database.increment_metric(user_id, "shares_count")


def get_usage_stats(user_id: str) -> Dict[str, int]:
    """
    Get usage statistics for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict with usage stats
    """
    metrics = database.get_user_metrics(user_id)
    post_count = database.get_user_post_count(user_id)
    
    return {
        "total_posts": post_count,
        "total_likes": metrics.get("likes_count", 0),
        "total_shares": metrics.get("shares_count", 0),
        "engagement_rate": calculate_engagement_rate(metrics)
    }


def calculate_engagement_rate(metrics: Dict) -> float:
    """
    Calculate engagement rate (likes + shares) / posts.
    
    Args:
        metrics: Metrics dict
        
    Returns:
        Engagement rate as percentage
    """
    posts = metrics.get("posts_generated", 0)
    if posts == 0:
        return 0.0
    
    likes = metrics.get("likes_count", 0)
    shares = metrics.get("shares_count", 0)
    
    return ((likes + shares) / posts) * 100


def show_usage_badge(user_id: str, is_subscribed: bool):
    """
    Show usage badge/status.
    
    Args:
        user_id: User identifier
        is_subscribed: Whether user is subscribed
    """
    if is_subscribed:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00B5AD 0%, #0077B5 100%); 
                    padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; margin-bottom: 1rem;">
            <span style="color: white; font-weight: 600;">✨ Premium Access</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        post_count = database.get_user_post_count(user_id)
        remaining = 3 - post_count
        
        if remaining > 0:
            st.markdown(f"""
            <div style="background: #2d3748; padding: 0.5rem 1rem; border-radius: 20px; 
                        display: inline-block; margin-bottom: 1rem; border: 2px solid #00B5AD;">
                <span style="color: #00B5AD; font-weight: 600;">
                    🆓 Free Trial: {remaining} uses remaining
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #742a2a; padding: 0.5rem 1rem; border-radius: 20px; 
                        display: inline-block; margin-bottom: 1rem; border: 2px solid #fc8181;">
                <span style="color: #fc8181; font-weight: 600;">
                    ⚠️ Free trial expired
                </span>
            </div>
            """, unsafe_allow_html=True)
