"""
LinkyGen V2 - Professional AI-Powered LinkedIn Content Generator
Complete redesign with dark theme, access control, metrics, and social sharing
"""

import streamlit as st
from linky_agents import app as linky_workflow, LinkyGenState
import time
import auth
import database
import geo_utils
import metrics
import social_share

# Page configuration
st.set_page_config(
    page_title="LinkyGen - AI LinkedIn Content Generator",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
# Billionaire Design System - Premium Glassmorphism & Typography
st.markdown("""
<style>
    /* 1. GLOBAL RESET & TYPOGRAPHY */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top left, #1a1f3c 0%, #0a0e17 100%);
        font-family: 'Inter', sans-serif;
        color: #e0e6ed;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* 2. GLASSMORPHISM CONTAINERS */
    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-panel:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.15);
    }
    
    /* 3. PREMIUM HEADER */
    .premium-header {
        background: linear-gradient(90deg, #2b5876 0%, #4e4376 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    /* 4. CUSTOM INPUT FIELDS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4e4376 !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 0 0 2px rgba(78, 67, 118, 0.25) !important;
    }
    
    /* 5. LUXURY BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FDB931 100%) !important; /* Gold Gradient option or Deep Blue */
        background: linear-gradient(135deg, #0061ff 0%, #60efff 100%) !important; /* Electric Blue */
        color: #000000 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.85rem 2.5rem !important;
        border-radius: 16px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        font-size: 0.9rem !important;
        box-shadow: 0 10px 20px -10px rgba(96, 239, 255, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 30px -10px rgba(96, 239, 255, 0.7) !important;
    }
    
    /* 6. METRIC CARDS OVERRIDE */
    .metric-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
    }
    
    /* 7. PROGRESS BAR & SLIDERS */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%) !important;
    }
    
    .stSlider > div > div > div {
        background-color: #0072ff !important;
    }

    /* 8. SIDEBAR PREMIUM */
    [data-testid="stSidebar"] {
        background: #0a0e17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 9. FOOTER CLEANUP */
    footer {visibility: hidden;}
    
    /* 10. POST PREVIEW TYPOGRAPHY */
    .post-content {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "linky_state" not in st.session_state:
    st.session_state.linky_state = {
        "topic": "",
        "custom_content": "",
        "tone": "Visionary Tech Analyst",
        "content_type": ["News Breakdown"],
        "target_word_count": 300,
        "engagement_level": "Medium",
        "narrative_patterns": ["Storytelling Arc"],
        "creativity_level": 0.7, # Default balanced
        "generated_post": None,
        "is_editing": False,
        "status_message": None,
        "error_message": None,
        "research_results": None,
        "custom_instructions": "", # New: User custom styles
        "image_prompt": None, # New: Professional image generation prompt
        "source_links": [], # Added
        "target_region": "Global (International)" # Added
    }

# Check authentication
if not auth.is_authenticated():
    auth.show_access_code_screen()
    st.stop()

# Get user info
user_id = auth.get_user_id()
is_subscribed = st.session_state.get("is_subscribed", False)

# Get location data (cached)
if "location_data" not in st.session_state:
    st.session_state.location_data = geo_utils.get_user_location()
    # Save to database
    database.create_or_get_user(
        user_id=user_id,
        country=st.session_state.location_data.get("country"),
        timezone=st.session_state.location_data.get("timezone")
    )

location_data = st.session_state.location_data

# Header with location and time
col_header1, col_header2 = st.columns([3, 1])

with col_header1:
    st.markdown("""
    <div class="glass-panel" style="padding: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 class="premium-header" style="font-size: 2.5rem; text-align: left; margin: 0;">LinkyGen</h1>
            <p style="color: #a0aec0; margin: 0; letter-spacing: 1px;">INTELLIGENT CONTENT ENGINE</p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem; letter-spacing: 1px; color: #60efff;">
            V2.0 PRO
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header2:
    st.markdown(f"""
    <div class="glass-panel" style="padding: 1rem; display: flex; flex-direction: column; justify-content: center; height: 100%;">
        <div style="color: #60efff; font-size: 0.8rem; margin-bottom: 0.3rem;">
            📍 {geo_utils.format_location_display(location_data)}
        </div>
        <div style="color: #ffffff; font-size: 1.2rem; font-weight: 700;">
            {geo_utils.format_time_display(location_data)}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with metrics and usage
with st.sidebar:
    st.markdown("### 📊 DASHBOARD")
    
    # Usage badge
    metrics.show_usage_badge(user_id, is_subscribed)
    
    # Metrics display
    metrics.display_metrics_dashboard(user_id)
    
    st.markdown("---")
    
    # Creativity Control
    st.markdown("### 🎨 CREATIVITY CONTROL")
    creativity_level = st.slider(
        "AI Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.linky_state.get("creativity_level", 0.7),
        step=0.1,
        help="ℹ️ **Temperature Control**\n\n• **Low (0.0-0.4):** Precise, factual, professional. Best for news & data.\n• **Balanced (0.5-0.7):** Engaging yet grounded. Best for standard posts.\n• **High (0.8-1.0):** Experimental, unique, storytelling. Best for viral essays."
    )
    st.session_state.linky_state["creativity_level"] = creativity_level
    
    st.caption(f"Current Mode: {'Strict' if creativity_level < 0.4 else 'Balanced' if creativity_level < 0.8 else 'Wild'}")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ QUICK ACTIONS")
    if st.button("🔄 New Post", use_container_width=True):
        st.session_state.linky_state["generated_post"] = None
        st.rerun()
    
    if st.button("📜 View History", use_container_width=True):
        st.info("History feature coming soon!")

# Main content area
st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="color: #60efff; margin-bottom: 1rem;">📝 CONTENT CONFIGURATION</h3>', unsafe_allow_html=True)

# Check usage limit
can_use, remaining = auth.check_usage_limit()

if not can_use:
    auth.show_usage_limit_warning()
    st.stop()

# Create Tabs
tab_research, tab_gen, tab_about = st.tabs(["🔍 INSTANT RESEARCH", "🚀 CONTENT ENGINE", "👨‍💻 ABOUT US"])

with tab_about:
    st.markdown("### 👨‍💻 ABOUT THE DEVELOPER")
    col_dev1, col_dev2 = st.columns([1, 2])
    
    with col_dev1:
        st.markdown(f"""
        <div class="glass-panel" style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
            <h3 style="margin: 0;">Lawrence Oladeji</h3>
            <p style="color: #60efff; font-size: 0.9rem;">Data Associate & AI Automation Developer</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📫 CONTACT")
        st.markdown("📧 [oladeji.lawrence@gmail.com](mailto:oladeji.lawrence@gmail.com)")
        st.markdown("💬 [Whatsapp +2349038819790](https://wa.me/2349038819790)")
        
    with col_dev2:
        st.markdown("#### 🚀 MISSION: LINKYGEN")
        st.markdown("""
        LinkyGen is engineered to transform how professionals and creators approach LinkedIn. 
        We don't just generate text; we engineer **authority** and **virality**.
        
        **Expected Transformation:**
        - **From:** Spending hours staring at a blank screen.
        - **To:** Launching high-performance content in seconds.
        
        **User Gains:**
        - **Increased Reach:** Built-in viral hooks optimized for the current algorithm.
        - **Authentic Voice:** Human-centric writing that bypasses common AI detectors.
        - **Strategic Insight:** Real-time web scanning ensures you're always talking about what matters.
        """)
        
        st.markdown("---")
        st.markdown("#### 📖 PAGE GUIDE")
        with st.expander("🔍 INSTANT RESEARCH", expanded=True):
            st.write("The web-scale discovery engine. Scans top news sources, big organizations, and global trends to provide you with a factual strategic brief and viral hook ideas.")
        
        with st.expander("🚀 CONTENT ENGINE"):
            st.write("The generator. Combines your unique insights with our proprietary Viral DNA patterns. Now supports **Custom Style Instructions** for total creative control.")

with tab_research:
    st.markdown("### 🔍 INSTANT MARKET RESEARCH")
    st.markdown("Scans Google, NewsSources, and Trends to find the latest for your sector.")
    
    with st.container():
        research_col1, research_col2 = st.columns([3, 1])
        with research_col1:
            research_topic_input = st.text_input(
                "SECTOR OR SPECIFIC TREND",
                placeholder="e.g., Renewable Energy Trends 2026, AI in Legal Tech...",
                key="research_input"
            )
        with research_col2:
            research_region = st.selectbox(
                "REGION",
                options=["Global (International)", "North America (US/CA)", "Europe (EU/UK)", "Asia Pacific", "Local (My Location)"],
                key="research_region_select"
            )
            
        research_mode = st.radio(
            "RESEARCH DEPTH",
            options=["Instant (Fast, News focus)", "Deep (Agentic, Multi-query, Insight focus)"],
            index=0,
            horizontal=True,
            help="Deep research takes 20-30 seconds but performs multiple searches and rigorous analysis."
        )
        
        is_deep = "Deep" in research_mode
        
        if st.button("🔎 SCAN LATEST NEWS & TRENDS", use_container_width=True):
            if not research_topic_input:
                st.warning("Please enter a topic to research.")
            else:
                with st.spinner(f"Running {'Deep' if is_deep else 'Instant'} research for {research_topic_input}..."):
                    from linky_agents import research_topic as run_research
                    results = run_research(
                        topic=research_topic_input, 
                        region=research_region, 
                        user_country=location_data.get("country_code", "US"),
                        is_deep=is_deep
                    )
                    st.session_state.linky_state["research_results"] = results
                    st.rerun()

    # Display Research Results
    if st.session_state.linky_state.get("research_results"):
        res = st.session_state.linky_state["research_results"]
        
        st.markdown("---")
        col_res1, col_res2 = st.columns([2, 1])
        
        with col_res1:
            st.markdown("#### 📝 STRATEGIC BRIEF")
            st.markdown(f"""
            <div class="glass-panel" style="padding: 1.5rem; background: rgba(96, 239, 255, 0.05);">
                {str(res.get('research_brief', 'No brief generated.')).replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ USE THIS RESEARCH TO DRAFT A POST", type="primary", use_container_width=True):
                # Pass research to generation state
                st.session_state.linky_state["topic"] = res["topic"]
                # Extract insights for custom content
                st.session_state.linky_state["custom_content"] = f"Based on latest research for {res['topic']}:\n{res.get('latest_news_and_stats', '')}"
                st.session_state.linky_state["target_region"] = research_region
                st.session_state.linky_state["source_links"] = res.get("source_links", [])
                # Switch to generation tab (implicitly by state change usually, but we'll show success)
                st.success("Research loaded into Content Engine! Switch to the 🚀 tab to generate.")
        
        with col_res2:
            st.markdown("#### 🔗 TOP SOURCES")
            for link in res.get("source_links", []):
                st.markdown(f"• [{link['title']}]({link['url']})")
            
            if not res.get("source_links"):
                st.info("No direct links found, but trend analysis is complete.")

with tab_gen:
    st.markdown('<h3 style="color: #60efff; margin-bottom: 1rem;">📝 CONTENT CONFIGURATION</h3>', unsafe_allow_html=True)
    
    # Input form (wrapped in glass panel purely visual, but st.form needs direct access)
    with st.container():
        with st.form("content_form"):
            # Topic input
            topic = st.text_input(
                "TOPIC / MAIN IDEA",
                value=st.session_state.linky_state["topic"],
                placeholder="e.g., The Future of AI in Personalized Medicine",
                help="What do you want to post about?"
            )
            
            # Custom content
            custom_content = st.text_area(
                "YOUR UNIQUE INSIGHTS (Optional)",
                value=st.session_state.linky_state["custom_content"],
                placeholder="e.g., My recent research shows...",
                height=150,
                help="Add your unique perspective or data"
            )

            custom_instructions = st.text_area(
                "CUSTOM STYLE / TONE INSTRUCTIONS (Optional)",
                value=st.session_state.linky_state["custom_instructions"],
                placeholder="e.g., Use extremely simple language, or write like a cynical Wall Street investor...",
                height=100,
                help="Specify any specific instructions for the AI to follow strictly."
            )
            
            # Display pre-loaded research links if available
            if st.session_state.linky_state.get("source_links"):
                with st.expander("📚 LOADED RESEARCH SOURCES", expanded=True):
                    for link in st.session_state.linky_state["source_links"]:
                        st.markdown(f"• [{link['title']}]({link['url']})")
                    if st.button("🗑️ Clear Research Data", use_container_width=True):
                        st.session_state.linky_state["source_links"] = []
                        st.session_state.linky_state["custom_content"] = ""
                        st.rerun()
            
            col1, col2 = st.columns(2)
            
            with col1:
                tone = st.selectbox(
                    "TONE / PERSONA",
                    options=[
                        "Visionary Tech Analyst",
                        "Solopreneur/Lifestyle Designer",
                        "Practical Educator",
                        "Regional Specialist",
                        "Provocateur",
                        "Insider"
                    ],
                    index=0,
                    help="Choose the voice and perspective"
                )
                
                content_type = st.multiselect(
                    "CONTENT FORMATS",
                    options=[
                        "News Breakdown",
                        "Philosophical Essay",
                        "Tactical Guide",
                        "Case Study",
                        "Personal Story"
                    ],
                    default=["News Breakdown"],
                    help="Select one or more formats"
                )
    
                target_region = st.selectbox(
                    "TARGET AUDIENCE REGION",
                    options=["Global (International)", "North America (US/CA)", "Europe (EU/UK)", "Asia Pacific", "Local (My Location)"],
                    index=0,
                    help="Where is your target audience located?"
                )
            
            with col2:
                engagement_level = st.radio(
                    "ENGAGEMENT LEVEL",
                    options=["Low", "Medium", "High"],
                    index=1,
                    horizontal=True,
                    help="How viral should it be?"
                )
                
                deep_gen = st.toggle(
                    "🧠 AGENTIC DEEP RESEARCH (POST-GENERATION)",
                    value=False,
                    help="If enabled, the AI will perform a deep multi-query strategic scan before writing the post. Takes 20-30s."
                )
                
                narrative_patterns = st.multiselect(
                    "NARRATIVE PATTERNS",
                    options=[
                        "Storytelling Arc",
                        "Us vs. Them Mentality",
                        "Relatability Factor"
                    ],
                    default=["Storytelling Arc"],
                    help="Choose narrative structures"
                )
            
            # Word count slider (50-1700 words)
            target_word_count = st.slider(
                "TARGET WORD COUNT",
                min_value=50,
                max_value=1700,
                value=300,
                step=50,
                help="Target number of WORDS (not characters)"
            )
            
            # Display word count category
            if target_word_count < 200:
                word_label = "Short"
            elif target_word_count < 600:
                word_label = "Medium"
            elif target_word_count < 1000:
                word_label = "Long"
            else:
                word_label = "Very Long"
            
            st.caption(f"📏 {word_label} post (~{target_word_count} words)")
            
            # Submit button
            generate_clicked = st.form_submit_button(
                "✨ GENERATE MASTERPIECE",
                use_container_width=True,
                type="primary"
            )

    # Handle generation
    if generate_clicked:
        if not topic.strip():
            st.error("⚠️ Please enter a topic for your LinkedIn post.")
        else:
            # Update session state
            st.session_state.linky_state.update({
                "topic": topic,
                "custom_content": custom_content,
                "tone": tone,
                "content_type": content_type,
                "target_word_count": target_word_count,
                "engagement_level": engagement_level,
                "narrative_patterns": narrative_patterns,
                "target_region": target_region, # Capture region
                "creativity_level": creativity_level, # Capture current slider value
                "custom_instructions": custom_instructions, # New
                "is_deep": deep_gen
            })
            
            # Show progress
            with st.status("🔄 PROCESS INITIATED...", expanded=True) as status:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Prepare initial state
                    initial_state: LinkyGenState = {
                        "topic": topic,
                        "custom_content": custom_content if custom_content.strip() else None,
                        "tone": tone,
                        "content_type": content_type,
                        "target_word_count": target_word_count,
                        "engagement_level": engagement_level,
                        "narrative_patterns": narrative_patterns,
                        "creativity_level": creativity_level,
                        "target_region": target_region, # Pass to workflow
                        "user_country": st.session_state.location_data.get("country_code", "XX"), # Keep location for reference
                        "latest_news_and_stats": None,
                        "source_links": [],
                        "key_insights": None,
                        "viral_elements": None,
                        "sentiment_analysis": None,
                        "raw_linkedin_post": None,
                        "final_linkedin_post": None,
                        "status_message": None,
                        "error_message": None,
                        "custom_instructions": custom_instructions, # New
                        "image_prompt": None, # Initialize
                        "is_deep": deep_gen
                    }
                    
                    # Check for persistence warning
                    if database.is_bypass_active():
                        st.toast("⚠️ Demo Mode: Database disconnected. Stats won't save on refresh.", icon="⚠️")
                    
                    # Execute workflow
                    step = 0
                    total_steps = 5  # Updated to include verification step
                    
                    for output in linky_workflow.stream(initial_state):
                        step += 1
                        progress = min(step / total_steps, 1.0)  # Cap at 1.0
                        progress_bar.progress(progress)
                        
                        if output:
                            latest_node = list(output.keys())[0]
                            latest_state = output[latest_node]
                            
                            if latest_state.get("status_message"):
                                status_text.text(f"📍 {latest_state['status_message']}")
                            
                            time.sleep(0.3)
                    
                    # Get final state
                    final_state = latest_state
                    
                    # Check for errors
                    if final_state.get("error_message"):
                        status.update(label="❌ Generation failed", state="error")
                        st.error(f"Error: {final_state['error_message']}")
                    elif final_state.get("final_linkedin_post"):
                        status.update(label="✅ Post generated successfully!", state="complete")
                        st.session_state.linky_state["generated_post"] = final_state["final_linkedin_post"]
                        st.session_state.linky_state["image_prompt"] = final_state.get("image_prompt") # Added this line
                        st.session_state.linky_state["source_links"] = final_state.get("source_links", [])
                        
                        # Save to database
                        word_count = len(final_state["final_linkedin_post"].split())
                        database.save_post(user_id, final_state["final_linkedin_post"], word_count)
                        
                        st.rerun()
                    else:
                        status.update(label="❌ Failed to generate", state="error")
                        st.error("Failed to generate post. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Display generated post
if st.session_state.linky_state.get("generated_post"):
    st.markdown('<div class="section-header">👁️ Your LinkedIn Post</div>', unsafe_allow_html=True)
    
    if st.session_state.linky_state.get("is_editing"):
        # Edit mode
        edited_post = st.text_area(
            "Edit your post",
            value=st.session_state.linky_state["generated_post"],
            height=400,
            key="edit_area"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.linky_state["generated_post"] = edited_post
                st.session_state.linky_state["is_editing"] = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.linky_state["is_editing"] = False
                st.rerun()
    else:
        # Display mode
        post_content = st.session_state.linky_state["generated_post"]
        
        st.markdown(f"""
        <div class="post-preview">
        {post_content.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Display Image Prompt if available
        if st.session_state.linky_state.get("image_prompt"):
            with st.expander("🖼️ PROFESSIONAL IMAGE PROMPT", expanded=False):
                st.info("Use this prompt with Midjourney or DALL-E to generate a matching visual.")
                st.code(st.session_state.linky_state["image_prompt"], language="text")
        
        # Display Research Sources if available
        if st.session_state.linky_state.get("source_links"):
            st.markdown("### 📚 Research Sources")
            for source in st.session_state.linky_state["source_links"]:
                st.markdown(f"🔗 [{source['title']}]({source['url']})")
            st.markdown("---")
        
        # Word count
        word_count = len(post_content.split())
        st.caption(f"📊 {word_count} words")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit Post", use_container_width=True):
                st.session_state.linky_state["is_editing"] = True
                st.rerun()
        
        with col2:
            if st.button("❤️ Like", use_container_width=True):
                metrics.track_like(user_id)
                st.success("Liked!")
                time.sleep(0.5)
                st.rerun()
        
        with col3:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.linky_state["generated_post"] = None
                st.rerun()
        
        with col4:
            # Copy button (simplified)
            if st.button("📋 Copy", use_container_width=True):
                st.info("💡 Select the text above and press Ctrl+C to copy")
        
        # Social sharing
        st.markdown("---")
        st.markdown("### 🚀 Share Your Post")
        
        share_urls = social_share.get_all_share_urls(post_content)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <a href="{share_urls['linkedin']}" target="_blank" class="social-btn linkedin-btn">
                📘 Share on LinkedIn
            </a>
            """, unsafe_allow_html=True)
            if st.button("Track LinkedIn Share", key="linkedin_share", use_container_width=True):
                metrics.track_share(user_id)
                st.success("Share tracked!")
        
        with col2:
            st.markdown(f"""
            <a href="{share_urls['twitter']}" target="_blank" class="social-btn twitter-btn">
                🐦 Share on Twitter
            </a>
            """, unsafe_allow_html=True)
            if st.button("Track Twitter Share", key="twitter_share", use_container_width=True):
                metrics.track_share(user_id)
                st.success("Share tracked!")
        
        with col3:
            st.markdown(f"""
            <a href="{share_urls['facebook']}" target="_blank" class="social-btn facebook-btn">
                📱 Share on Facebook
            </a>
            """, unsafe_allow_html=True)
            if st.button("Track Facebook Share", key="facebook_share", use_container_width=True):
                metrics.track_share(user_id)
                st.success("Share tracked!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #a0aec0; padding: 2rem;">
    <p style="font-family: 'Space Grotesk'; font-size: 1.1rem; margin-bottom: 0.5rem;">LinkyGen V2.0 PRO</p>
    <p style="font-size: 0.9rem; margin-bottom: 1rem;">ENGINEERED FOR IMPACT</p>
    <div style="display: flex; justify-content: center; gap: 1rem; opacity: 0.6; font-size: 0.8rem;">
        <span>PRIVACY</span>
        <span>TERMS</span>
        <span>SUPPORT</span>
    </div>
    <div style="margin-top: 2rem; opacity: 0.4; font-size: 0.7rem;">
        © 2026 PROVENANCE AUD. ALL RIGHTS RESERVED.
    </div>
</div>
""", unsafe_allow_html=True)
