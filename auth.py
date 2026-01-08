"""
Authentication and Access Control
Handles access code validation and usage limits
"""

import os
import streamlit as st
from typing import Optional
from dotenv import load_dotenv
import database

load_dotenv()

FREE_USAGE_LIMIT = int(os.getenv("FREE_USAGE_LIMIT", "3"))
REQUIRE_ACCESS_CODE = os.getenv("REQUIRE_ACCESS_CODE", "true").lower() == "true"


def get_user_id() -> str:
    """
    Get or create a unique user ID for the current session.
    
    Returns:
        User ID string
    """
    if "user_id" not in st.session_state:
        # Generate a unique session-based user ID
        import uuid
        st.session_state.user_id = str(uuid.uuid4())
    
    return st.session_state.user_id


def is_authenticated() -> bool:
    """
    Check if the current user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    return st.session_state.get("authenticated", False)


def authenticate_with_code(access_code: str) -> bool:
    """
    Authenticate user with an access code.
    
    Args:
        access_code: 10-character alphanumeric code
        
    Returns:
        True if authentication successful, False otherwise
    """
    # Validate code format
    if len(access_code) != 10:
        return False
    
    # Check if code is valid in database
    if database.validate_access_code(access_code):
        user_id = get_user_id()
        
        # Mark code as used
        database.mark_code_as_used(access_code, user_id)
        
        # Set authentication state
        st.session_state.authenticated = True
        st.session_state.access_code = access_code
        st.session_state.is_subscribed = True  # Users with codes are considered subscribed
        
        return True
    
    return False


def check_usage_limit() -> tuple[bool, int]:
    """
    Check if user has exceeded their free usage limit.
    
    Returns:
        Tuple of (can_use, remaining_uses)
    """
    user_id = get_user_id()
    
    # If user is subscribed (has valid access code), no limit
    if st.session_state.get("is_subscribed", False):
        return (True, -1)  # -1 indicates unlimited
    
    # Check post count
    post_count = database.get_user_post_count(user_id)
    remaining = FREE_USAGE_LIMIT - post_count
    
    return (remaining > 0, remaining)


def show_access_code_screen():
    """
    Display the access code entry screen OR free trial info.
    """
    # Check if user has free uses remaining
    user_id = get_user_id()
    post_count = database.get_user_post_count(user_id)
    free_remaining = FREE_USAGE_LIMIT - post_count
    
    # If user still has free uses, let them through without code
    if free_remaining > 0 and not st.session_state.get("authenticated", False):
        st.session_state.authenticated = True
        st.session_state.is_subscribed = False
        st.session_state.free_trial = True
        st.rerun()
        return
    
    # If free trial expired, show email collection
    if free_remaining <= 0 and not st.session_state.get("authenticated", False):
        show_email_collection_screen()
        return
    
    # Otherwise show access code screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🔗 Linky</h1>
        <p style="font-size: 1.2rem; color: #888; margin-bottom: 2rem;">
            AI-Powered LinkedIn Content Generator
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0077B5 0%, #00B5AD 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0;">Enter Access Code</h2>
            <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">
                Enter your 10-character access code to unlock Linky
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        access_code = st.text_input(
            "Access Code",
            max_chars=10,
            placeholder="XXXXXXXXXX",
            key="access_code_input",
            label_visibility="collapsed"
        )
        
        if st.button("🚀 Unlock Linky", use_container_width=True, type="primary"):
            if access_code:
                if authenticate_with_code(access_code.upper()):
                    st.success("✅ Access granted! Welcome to Linky!")
                    st.rerun()
                else:
                    st.error("❌ Invalid access code. Please try again.")
            else:
                st.warning("⚠️ Please enter an access code.")
        
        st.markdown("---")
        
        st.info("""
        **Don't have an access code?**
        
        Contact us to get your access code and start creating viral LinkedIn content!
        
        **Sample codes for testing:**
        - LINKY2026A
        - BETA123456
        - DEMO789XYZ
        """)


def show_email_collection_screen():
    """
    Show email collection screen after free trial expires.
    """
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🔗 Linky</h1>
        <p style="font-size: 1.2rem; color: #888; margin-bottom: 2rem;">
            AI-Powered LinkedIn Content Generator
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0;">🎉 Free Trial Complete!</h2>
            <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">
                You've used all 3 free content generations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### Continue Creating Viral Content
        
        Enter your email to receive a **free access code** and unlock unlimited content generation!
        """)
        
        email = st.text_input(
            "Email Address",
            placeholder="your@email.com",
            key="email_input"
        )
        
        if st.button("📧 Get Free Access Code", use_container_width=True, type="primary"):
            if email and "@" in email and "." in email:
                # Save email to database
                user_id = get_user_id()
                database.create_or_get_user(user_id, email=email)
                
                st.success(f"""
                ✅ **Access code sent to {email}!**
                
                Check your inbox for your personal access code.
                
                (In demo mode, use any of these codes: LINKY2026A, BETA123456, DEMO789XYZ)
                """)
                
                # Show access code input
                st.markdown("---")
                access_code = st.text_input(
                    "Enter your access code",
                    max_chars=10,
                    placeholder="XXXXXXXXXX",
                    key="email_access_code"
                )
                
                if st.button("Unlock Now", key="unlock_after_email"):
                    if access_code:
                        if authenticate_with_code(access_code.upper()):
                            st.success("✅ Welcome back to Linky!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid code. Check your email.")
            else:
                st.error("⚠️ Please enter a valid email address.")
        
        st.markdown("---")
        st.info("""
        **Already have an access code?**
        
        Enter it above to unlock Linky immediately!
        """)


def show_usage_limit_warning():
    """
    Display a warning when user reaches usage limit.
    """
    st.warning("""
    ⚠️ **Free Usage Limit Reached**
    
    You've used all 3 free content generations. 
    
    To continue using Linky, please enter an access code or subscribe.
    """)
    
    with st.expander("Enter Access Code"):
        access_code = st.text_input(
            "Access Code",
            max_chars=10,
            placeholder="XXXXXXXXXX",
            key="upgrade_access_code"
        )
        
        if st.button("Unlock Full Access", key="upgrade_button"):
            if access_code:
                if authenticate_with_code(access_code.upper()):
                    st.success("✅ Access granted! You now have unlimited access.")
                    st.rerun()
                else:
                    st.error("❌ Invalid access code.")
