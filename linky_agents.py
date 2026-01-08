"""
Linky Agents - LangGraph State Machine
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


class LinkyState(TypedDict):
    """State definition for Linky workflow"""
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


def retrieve_information(state: LinkyState) -> LinkyState:
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
                if api_country:
                    # Specific country search
                    url = f"https://newsapi.org/v2/top-headlines?q={topic}&country={api_country}&apiKey={NEWS_API_KEY}"
                    response = requests.get(url, timeout=5)
                    
                    # Fallback to everything if strict country search fails
                    if response.status_code == 200 and response.json().get("totalResults", 0) == 0:
                        url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=relevancy&apiKey={NEWS_API_KEY}"
                        response = requests.get(url, timeout=5)
                else:
                    # Global search (Everything)
                    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=relevancy&apiKey={NEWS_API_KEY}"
                    response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])[:4] # Get top 4
                    for article in articles:
                        combined_info.append(f"- {article['title']} ({article['source']['name']})")
                        if article.get("url"):
                            source_links.append({"title": article['title'], "url": article['url']})
            except Exception as e:
                print(f"NewsAPI error: {e}")

        # 2. GNews API (Fallback/Supplement)
        if GNEWS_API_KEY and len(combined_info) < 2:
            try:
                country_param = f"&country={api_country}" if api_country else ""
                url = f"https://gnews.io/api/v4/search?q={topic}{country_param}&lang=en&max=3&apikey={GNEWS_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", [])[:3]:
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


def analyze_content(state: LinkyState) -> LinkyState:
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


def generate_content(state: LinkyState) -> LinkyState:
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
            creativity_level=creativity
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


def verify_content(state: LinkyState) -> LinkyState:
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


def refine_content(state: LinkyState) -> LinkyState:
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
        
        if word_count > target_words * 1.2:
            # Post is too long, ask LLM to shorten
            system_prompt = f"You are an expert editor. Shorten the following LinkedIn post to approximately {target_words} words while maintaining its impact and message. Keep all Anti-Slop principles and LinkedIn formatting."
            user_prompt = f"Shorten this post to ~{target_words} words:\n\n{refined_post}"
            
            shortened = llm_utils.call_openrouter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=int(target_words * 2),
                temperature=0.5
            )
            
            if shortened:
                refined_post = shortened.replace("```", "").strip()
        
        # Basic Anti-Slop checks (rule-based for MVP)
        if "—" in refined_post:
            print("Warning: Em-dash detected in post")
        
        # Ensure proper line breaks for LinkedIn
        refined_post = refined_post.strip()
        
        state["final_linkedin_post"] = refined_post
        state["status_message"] = "Post ready for publishing!"
        return state
        
    except Exception as e:
        state["error_message"] = f"Error refining content: {str(e)}"
        state["status_message"] = "Refinement failed, using raw post"
        # Fallback to raw post
        state["final_linkedin_post"] = state.get("raw_linkedin_post")
        return state


# Define the LangGraph workflow
def create_workflow() -> StateGraph:
    """
    Create and compile the Linky LangGraph workflow.
    
    Returns:
        Compiled StateGraph application
    """
    workflow = StateGraph(LinkyState)
    
    # Add nodes
    workflow.add_node("retrieve_information", retrieve_information)
    workflow.add_node("analyze_content", analyze_content)
    workflow.add_node("generate_content", generate_content)
    workflow.add_node("verify_content", verify_content)  # NEW NODE
    workflow.add_node("refine_content", refine_content)
    
    # Set entry point
    workflow.set_entry_point("retrieve_information")
    
    # Define edges (sequential flow for MVP)
    workflow.add_edge("retrieve_information", "analyze_content")
    workflow.add_edge("analyze_content", "generate_content")
    workflow.add_edge("generate_content", "verify_content")  # Connect generate -> verify
    workflow.add_edge("verify_content", "refine_content")    # Connect verify -> refine
    workflow.add_edge("refine_content", END)
    
    # Compile the graph
    return workflow.compile()


# Create the compiled app
app = create_workflow()
