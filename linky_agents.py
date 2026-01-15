"""
LinkyGen Agents - LangGraph State Machine
Implements the agentic workflow for LinkedIn content generation
"""

import os
import requests
from typing import TypedDict, List, Optional, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import llm_utils

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


class LinkyGenState(TypedDict):
    """State definition for LinkyGen workflow"""
    topic: str
    custom_content: Optional[str]
    tone: str
    content_type: List[str]
    target_word_count: int
    engagement_level: str
    narrative_patterns: List[str]
    creativity_level: float
    target_region: str # New: Target Audience Region
    user_country: Optional[str]
    
    latest_news_and_stats: Optional[str]
    source_links: List[dict]
    key_insights: Optional[str]
    viral_elements: Optional[str]
    sentiment_analysis: Optional[str]
    raw_linkedin_post: Optional[str]
    final_linkedin_post: Optional[str]
    status_message: Optional[str]
    error_message: Optional[str]
    custom_instructions: Optional[str] # New: Global style overrides
    image_prompt: Optional[str] # New: Professional image generation prompt


def retrieve_information(state: LinkyGenState) -> LinkyGenState:
    """
    Retrieve relevant news, stats, and trends based on TARGET REGION.
    """
    try:
        topic = state["topic"]
        region = state.get("target_region", "Global (International)")
        user_country = state.get("user_country", "us").lower()
        
        state["status_message"] = f"Scanning news for {region} audience..."
        
        # Determine query parameters based on region
        api_country = None # Default to None (Global/Everything)
        
        if "Local" in region:
            api_country = user_country
        elif "North America" in region:
            api_country = "us"
        elif "Europe" in region:
            api_country = "gb" # Proxy for EU in NewsAPI free tier (often limited)
        # Global/Asia/etc will use 'everything' endpoint or no country restriction
        
        # If no API keys, skip real retrieval
        if not NEWS_API_KEY and not GNEWS_API_KEY:
            state["latest_news_and_stats"] = "No live news access configured. Using general knowledge."
            state["source_links"] = []
            return state

        combined_info = []
        source_links = []
        
        # 1. NewsAPI
        if NEWS_API_KEY:
            try:
                # Validate country code (must be 2 letters and recognized by NewsAPI free tier)
                valid_api_country = api_country if api_country and len(api_country) == 2 and api_country.lower() != "xx" else None
                
                if valid_api_country:
                    # Specific country search - Headlines first
                    url = f"https://newsapi.org/v2/top-headlines?q={topic}&country={valid_api_country}&apiKey={NEWS_API_KEY}"
                    response = requests.get(url, timeout=5)
                    
                    # Fallback to everything if strict country search fails or returns nothing
                    if response.status_code != 200 or response.json().get("totalResults", 0) == 0:
                        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=relevancy&apiKey={NEWS_API_KEY}"
                        response = requests.get(url, timeout=5)
                else:
                    # Global search - Try popularity first
                    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=popularity&apiKey={NEWS_API_KEY}"
                    response = requests.get(url, timeout=5)
                    
                    # If popularity is too restrictive, try relevancy
                    if response.status_code == 200 and response.json().get("totalResults", 0) == 0:
                        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=relevancy&apiKey={NEWS_API_KEY}"
                        response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    # Filter articles to ensure they have content/titles
                    articles = [a for a in data.get("articles", []) if a.get("title") and a.get("title") != "[Removed]"][:5]
                    for article in articles:
                        combined_info.append(f"- {article['title']} ({article['source']['name']})")
                        if article.get("url"):
                            source_links.append({"title": article['title'], "url": article['url']})
                else:
                    print(f"NewsAPI error response: {response.text}")
            except Exception as e:
                print(f"NewsAPI exception: {e}")

        # 2. GNews API (Fallback/Supplement)
        if GNEWS_API_KEY and len(combined_info) < 2:
            try:
                valid_api_country = api_country if api_country and len(api_country) == 2 and api_country.lower() != "xx" else None
                country_param = f"&country={valid_api_country}" if valid_api_country else ""
                url = f"https://gnews.io/api/v4/search?q={topic}{country_param}&lang=en&max=5&apikey={GNEWS_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", [])[:3]:
                        if article.get("title") not in [info.split(" (")[0][2:] for info in combined_info]:
                            combined_info.append(f"- {article['title']} ({article['source']['name']})")
                            if article.get("url"):
                                source_links.append({"title": article['title'], "url": article['url']})
            except Exception as e:
                print(f"GNews error: {e}")
        
        state["latest_news_and_stats"] = "\n".join(combined_info) if combined_info else "No specific recent news found. Using general knowledge."
        state["source_links"] = source_links
        state["status_message"] = f"Found {len(combined_info)} relevant sources ({region})"
        
        return state

    except Exception as e:
        state["error_message"] = f"Error retrieving info: {str(e)}"
        state["latest_news_and_stats"] = "Error fetching news."
        return state


def research_topic(topic: str, region: str = "Global (International)", user_country: str = "us", is_deep: bool = False) -> dict:
    """
    Standalone research function for the Instant Research tab.
    Supports 'Deep' mode with multiple queries and agentic analysis.
    """
    state = {
        "topic": topic,
        "target_region": region,
        "user_country": user_country,
        "source_links": [],
        "latest_news_and_stats": "",
        "status_message": "Starting research..."
    }
    
    if not is_deep:
        # Standard Instant Research - Single pass
        state = retrieve_information(state)
    else:
        # Deep Research - Agentic Multi-query approach
        # Use simpler query expansion to avoid 0 results
        queries = [
            topic,
            f"{topic} news",
            f"{topic} trends"
        ]
        
        all_info = []
        all_links = []
        seen_urls = set()
        
        for i, q in enumerate(queries):
            state["status_message"] = f"Deep Scanning ({i+1}/{len(queries)}): {q}..."
            temp_state = state.copy()
            temp_state["topic"] = q
            temp_state = retrieve_information(temp_state)
            
            if temp_state.get("latest_news_and_stats") and "No specific recent news found" not in temp_state["latest_news_and_stats"]:
                all_info.append(f"### Research Focus: {q}\n{temp_state['latest_news_and_stats']}")
                
            for link in temp_state.get("source_links", []):
                if link["url"] not in seen_urls:
                    all_links.append(link)
                    seen_urls.add(link["url"])
                    
        state["latest_news_and_stats"] = "\n\n".join(all_info) if all_info else "No specific recent news found."
        state["source_links"] = all_links
        state["status_message"] = f"Deep research complete. Found {len(all_links)} sources."
    
    # Generate the research brief
    if state.get("latest_news_and_stats") and "No live news access configured" not in state["latest_news_and_stats"]:
        if is_deep:
            brief = llm_utils.call_llm_for_deep_research(topic, state["latest_news_and_stats"])
        else:
            brief = llm_utils.call_llm_for_research_brief(topic, state["latest_news_and_stats"])
        state["research_brief"] = brief
    else:
        state["research_brief"] = "No specific news found to generate a brief. Try a broader topic or check your API keys."
        
    return state


# Define the nodes for the workflow
def retrieve_information_node(state: LinkyGenState) -> LinkyGenState:
    """
    Wrapper node for retrieve_information that supports Deep mode.
    """
    is_deep = state.get("is_deep", False)
    topic = state["topic"]
    region = state.get("target_region", "Global (International)")
    user_country = state.get("user_country", "us")
    
    if is_deep:
        # Re-use the Deep logic from research_topic
        # (This avoids duplicating the multi-query logic)
        results = research_topic(topic, region, user_country, is_deep=True)
        state["latest_news_and_stats"] = results.get("latest_news_and_stats")
        state["source_links"] = results.get("source_links", [])
        state["status_message"] = results.get("status_message")
    else:
        state = retrieve_information(state)
        
    return state


def analyze_content(state: LinkyGenState) -> LinkyGenState:
    """
    Analyze retrieved content for insights, viral elements, and sentiment.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with analysis results
    """
    try:
        state["status_message"] = "Analyzing content for insights..."
        
        # Combine news and custom content for analysis
        content_to_analyze = ""
        if state.get("latest_news_and_stats"):
            content_to_analyze += f"News & Stats:\n{state['latest_news_and_stats']}\n\n"
        if state.get("custom_content"):
            content_to_analyze += f"Custom Content:\n{state['custom_content']}\n\n"
        content_to_analyze += f"Topic: {state['topic']}"
        
        # Call LLM for analysis
        analysis = llm_utils.call_llm_for_analysis(content_to_analyze)
        
        if analysis:
            # Parse analysis into components (simplified for MVP)
            state["key_insights"] = analysis
            state["viral_elements"] = "Extracted from analysis"
            state["sentiment_analysis"] = "Analyzed"
        else:
            # Fallback if LLM analysis fails
            state["key_insights"] = f"Topic: {state['topic']}"
            state["viral_elements"] = "To be determined during generation"
            state["sentiment_analysis"] = "Neutral"
        
        state["status_message"] = "Content analysis complete"
        return state
        
    except Exception as e:
        state["error_message"] = f"Error analyzing content: {str(e)}"
        state["status_message"] = "Analysis failed, proceeding with basic insights"
        state["key_insights"] = f"Topic: {state['topic']}"
        return state


def generate_content(state: LinkyGenState) -> LinkyGenState:
    """
    Generate the LinkedIn post using the master system prompt.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with raw_linkedin_post
    """
    try:
        state["status_message"] = "Generating LinkedIn post..."
        
        # Get master system prompt
        system_prompt = llm_utils.get_master_system_prompt()
        
        # Get creativity level (default to 0.7 if missing)
        creativity = state.get("creativity_level", 0.7)
        
        # Format user prompt with all parameters
        user_prompt = llm_utils.format_generation_prompt(
            topic=state["topic"],
            latest_news_and_stats=state.get("latest_news_and_stats", ""),
            custom_content=state.get("custom_content", ""),
            tone=state["tone"],
            content_type=state["content_type"],
            target_word_count=state["target_word_count"],
            engagement_level=state["engagement_level"],
            narrative_patterns=state["narrative_patterns"],
            creativity_level=creativity,
            custom_instructions=state.get("custom_instructions", "")
        )
        
        # Call OpenRouter API (estimate tokens based on words: ~1.3 tokens per word)
        max_tokens = int(state["target_word_count"] * 2)  # Give room for formatting
        generated_post = llm_utils.call_openrouter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=creativity, # Use the user's setting
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        
        if generated_post:
            # Remove code block markers if present
            generated_post = generated_post.replace("```", "").strip()
            state["raw_linkedin_post"] = generated_post
            state["status_message"] = "Post generated successfully"
        else:
            state["error_message"] = "Failed to generate post - all LLM models failed"
            state["status_message"] = "Generation failed"
            state["raw_linkedin_post"] = None
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error generating content: {str(e)}"
        state["status_message"] = "Content generation failed"
        state["raw_linkedin_post"] = None
        return state


def verify_content(state: LinkyGenState) -> LinkyGenState:
    """
    Verify the generated content for factual accuracy.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with verification status and potentially corrected content
    """
    try:
        state["status_message"] = "Verifying factual accuracy..."
        
        if not state.get("raw_linkedin_post"):
            return state
            
        # Construct original context
        original_context = f"Topic: {state['topic']}\n"
        if state.get("latest_news_and_stats"):
            original_context += f"News/Stats: {state['latest_news_and_stats']}\n"
        if state.get("custom_content"):
            original_context += f"Custom Content: {state['custom_content']}"
            
        # Call verification helper
        verification_result = llm_utils.verify_factual_accuracy(
            generated_content=state["raw_linkedin_post"],
            original_context=original_context
        )
        
        if not verification_result.get("is_accurate", True):
            print(f"⚠️ Reality Check Failed: {verification_result.get('issues')}")
            state["status_message"] = "⚠️ Facts verified. Correcting potential inaccuracies..."
            
            # If inaccurate, we could regenerate or refine. 
            # For MVP, we pass the suggestion to the refine step or mark it for strict refinement.
            # Let's append a note for the refinement step to fix it.
            issues = "; ".join(verification_result.get("issues", []))
            suggestion = verification_result.get("suggestion", "Ensure no invented stats.")
            
            # We'll use a specific refinement prompt to fix this
            fix_prompt = f"The previous draft contained these factual hallucinations: {issues}. {suggestion}. REWRITE the post to be 100% factually accurate based ONLY on the provided context."
            
            # Re-generate/Fix immediately (simple loop within this node for now)
            system_prompt = "You are a Fact-Correction Editor. Rewrite the LinkedIn post to remove all invented statistics/facts. Maintain viral structure but use qualitative descriptions if data is missing."
            user_prompt = f"Original Context: {original_context}\n\nDraft Post: {state['raw_linkedin_post']}\n\nCorrection Instructions: {fix_prompt}"
            
            corrected_post = llm_utils.call_openrouter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=int(state.get("target_word_count", 300) * 2),
                temperature=0.3
            )
            
            if corrected_post:
                state["raw_linkedin_post"] = corrected_post.strip()
                state["status_message"] = "Content corrected for factual accuracy"
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error interpreting verification: {str(e)}"
        # Proceed with existing content on error
        return state


def refine_content(state: LinkyGenState) -> LinkyGenState:
    """
    Refine and optimize the generated post for Anti-Slop principles and LinkedIn best practices.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final_linkedin_post
    """
    try:
        state["status_message"] = "Refining and optimizing post..."
        
        if not state.get("raw_linkedin_post"):
            state["error_message"] = "No raw post to refine"
            state["final_linkedin_post"] = None
            return state
        
        raw_post = state["raw_linkedin_post"]
        
        # For MVP, apply basic refinements
        refined_post = raw_post
        
        # Check word count and adjust if needed
        word_count = len(refined_post.split())
        target_words = state.get("target_word_count", 200) # Default if missing
        
        # Stricter word count enforcement (Iterative Loop)
        target_words = state.get("target_word_count", 200)
        attempts = 0
        max_attempts = 2
        
        while attempts < max_attempts:
            word_count = len(refined_post.split())
            diff = abs(word_count - target_words) / target_words
            
            if diff <= 0.1: # Within 10% is acceptable for LLM
                break
                
            attempts += 1
            action = "Shorten" if word_count > target_words else "Expand"
            state["status_message"] = f"Fixing length ({word_count}/{target_words} words). Attempt {attempts}..."
            
            system_prompt = f"""You are a master editor. Your task is to {action.lower()} the provided LinkedIn post to be as close to {target_words} words as possible.
            CURRENT COUNT: {word_count}
            TARGET: {target_words}
            STRICT RULES:
            - Maintain the EXACT hook and surprise element.
            - Do not lose the 'LinkyGen' human voice/no-slop rules.
            - Focus on adding or removing quality insights, not filler."""
            
            user_prompt = f"{action} this post to ~{target_words} words:\n\n{refined_post}"
            
            adjusted = llm_utils.call_openrouter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=int(target_words * 2.5),
                temperature=0.3 # Lower temperature for precision
            )
            
            if adjusted:
                refined_post = adjusted.replace("```", "").strip()
            else:
                break # API failure or no adjustment
        
        # Basic Anti-Slop checks (rule-based for MVP)
        if "—" in refined_post:
            print("Warning: Em-dash detected in post")
        
        # Ensure proper line breaks for LinkedIn
        refined_post = refined_post.strip()
        
        state["final_linkedin_post"] = refined_post
        state["status_message"] = "Post refined and polished."
        return state
        
    except Exception as e:
        state["error_message"] = f"Refinement failed: {str(e)}"
        return state


def generate_image_prompt_node(state: LinkyGenState) -> LinkyGenState:
    """
    Generate a professional image prompt based on the final post.
    """
    try:
        final_post = state.get("final_linkedin_post")
        if not final_post:
            return state
            
        state["status_message"] = "Generating professional image prompt..."
        
        prompt = llm_utils.call_llm_for_image_prompt(final_post)
        if prompt:
            state["image_prompt"] = prompt.strip()
            
        return state
    except Exception as e:
        print(f"Image prompt generation failed: {str(e)}")
        # Don't fail the whole workflow for an image prompt
        return state


# Define the LangGraph workflow
def create_workflow() -> StateGraph:
    """
    Create and compile the LinkyGen LangGraph workflow.
    
    Returns:
        Compiled StateGraph application
    """
    workflow = StateGraph(LinkyGenState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_information_node)
    workflow.add_node("analyze", analyze_content)
    workflow.add_node("generate", generate_content)
    workflow.add_node("verify", verify_content)
    workflow.add_node("refine", refine_content)
    workflow.add_node("image_prompt", generate_image_prompt_node)
    
    # Define edges - The core execution flow
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", "verify")
    workflow.add_edge("verify", "refine")
    workflow.add_edge("refine", "image_prompt")
    workflow.add_edge("image_prompt", END)
    
    # Compile the graph
    return workflow.compile()


# Create the compiled app
app = create_workflow()
