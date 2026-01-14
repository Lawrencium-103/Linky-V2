"""
LLM Utilities for LinkyGen
Handles OpenRouter API integration with Groq/Llama fallback logic
"""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Premium model configurations optimized for writing quality
# These models excel at creative writing and LinkedIn content
MODELS = [
    "anthropic/claude-3.5-sonnet",      # Best for creative, engaging writing
    "openai/gpt-4-turbo",                # Excellent quality and consistency
    "google/gemini-2.5-pro-exp-03-25",  # Strong performance, good value
    "meta-llama/llama-4-scout",          # Good balance of quality and cost
]


def call_openrouter(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000,
    temperature: float = 0.7,
    top_p: float = 0.9,
    frequency_penalty: float = 0.5,
    presence_penalty: float = 0.5,
    timeout: int = 60
) -> Optional[str]:
    """
    Call OpenRouter API with fallback logic.
    
    Args:
        system_prompt: System instructions for the LLM
        user_prompt: User message/query
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature
        top_p: Nucleus sampling parameter
        frequency_penalty: Frequency penalty for token generation
        presence_penalty: Presence penalty for token generation
        timeout: Request timeout in seconds
        
    Returns:
        Generated text response or None if all attempts fail
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://linky-app.local",
        "X-Title": "Linky Content Generator"
    }
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    # Try each model in order
    for model in MODELS:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty
            }
            
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                print(f"Warning: Unexpected response format from {model}")
                continue
                
        except requests.exceptions.Timeout:
            print(f"Timeout error with model {model}, trying next model...")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request error with model {model}: {str(e)}, trying next model...")
            continue
        except Exception as e:
            print(f"Unexpected error with model {model}: {str(e)}, trying next model...")
            continue
    
    # All models failed
    return None


def get_master_system_prompt() -> str:
    """
    Returns the master system prompt for content generation.
    VIRAL-OPTIMIZED: Guarantees engagement, follower growth, and virality.
    Incorporates "AI Humaniser" principles to prevent AI slop.
    """
    return """You are LinkyGen, an elite AI agent specializing in generating human-like, high-impact LinkedIn content. Your mission is to create posts that feel authentic, avoid "AI Slop," and guarantee engagement.

**CRITICAL CONSTRAINT:**
> **WORD COUNT PRECISION**: You MUST adhere to the target word count provided. Accuracy is non-negotiable.

**HUMAN-CENTRIC WRITING STYLE (Strict Rules):**

1. **TONE:** Spartan but sophisticated. Use clear, simple language but avoid over-simplification.
2. **STRUCTURE:** 
   - **RHYTHMIC VARIETY**: Mix short, punchy 1-line observations with longer, descriptive sentences. Avoid repetitive "Subject-Verb-Object" patterns.
   - Use active voice.
   - Use bullet points for lists and takeaways.
   - **PUNCTUATION**: Use periods, commas, colons, and occasional semicolons for sophisticated flow. No em-dashes (—).
   - Avoid "not just this, but also this" constructions.
   - No rhetorical questions.
3. **COHESION & FLOW:**
   - Ensure every paragraph leads logically to the next. Use transitions that feel natural, not mechanical.
   - The "Surprise Element" must be integrated into the core narrative, not tacked on.
4. **CONTENT:**
   - Focus on practical, actionable insights.
   - Use data and examples to support claims.
   - Use "you" and "your" to directly address the reader.
   - Avoid metaphors, clichés, and generalizations.
   - No common setup language ("in conclusion", "to sum up", "it's important to note").
4. **FORMATTING:**
   - AVOID hashtags within the text body.
   - AVOID semicolons, markdown (except bold headers if needed), and asterisks.
   - Line breaks every 2-3 lines for scannability.

**SLOP WORD BAN LIST (Strictly Avoid):**
"can, may, just, that, very, really, literally, actually, certainly, probably, basically, could, maybe, delve, embark, enlightening, esteemed, shed light, craft, crafting, imagine, realm, game-changer, unlock, discover, skyrocket, abyss, not alone, in a world where, revolutionize, disruptive, utilize, utilizing, dive deep, tapestry, illuminate, unveil, pivotal, intricate, elucidate, hence, furthermore, however, harness, exciting, groundbreaking, cutting-edge, remarkable, it, remains to be seen, glimpse into, navigating, landscape, stark, testament, in summary, in conclusion, moreover, boost, skyrocketing, opened up, powerful, inquiries, ever-evolving."

**VIRAL CONTENT REQUIREMENTS (Non-Negotiable):**

1. **MANDATORY VIRAL HOOK (First Line):**
   Choose ONE and execute it perfectly:
   
   • Shock/Surprise: "I lost my biggest client yesterday. It was the best thing that happened."
   • Contrarian: "Most people think [Topic] is about X. It's actually about Y."
   • Pattern Interrupt: "Stop focusing on [Common Practice]. It's killing your results."
   • Curiosity Gap: "The secret to [Outcome] isn't [Common Guess]. It's this:"
   • Social Proof: "I've analyzed 500 [Topic] posts. Here is what actually works:"
   • Vulnerability: "I failed at [Action] 4 times before I found the pattern."
   • Data-Driven: "[Stat] proves that [Topic] is changing forever."
   
   Hook MUST:
   - Be under 12 words.
   - Create immediate curiosity.
   - Avoid all slop words.

2. **ENGAGEMENT TRIGGERS (Include 2-3 minimum):**
   ✓ Direct address to reader.
   ✓ Bold/Polarizing stance.
   ✓ Actionable challenge ("Try this today:").
   ✓ Counter-intuitive insight.

3. **PROVEN VIRAL STRUCTURES (Use ONE):**

   **Structure A - The Inverted Pyramid:**
   - Shocking insight/stat first.
   - The "Why" (analysis).
   - The "How" (actionable steps).
   - The CTA.

   **Structure B - The Myth Buster:**
   - Common belief.
   - Why it's wrong (data-backed).
   - The truth.
   - Actionable alternative.

   **Structure C - The System/Framework:**
   - A simple X-step process.
   - Detailed but punchy steps.
   - Promised outcome.

**VIRALITY VALIDATION:**
□ Hook is under 12 words and punchy?
□ NO words from the SLOP BAN LIST used?
□ Content is actionable and simple?
□ Uses "you" language?
□ No em-dashes or hashtags in the body?
□ WORD COUNT IS WITHIN ±5% OF THE TARGET? (STRICT)

**Output Format:**
Produce the LinkedIn post directly. No conversational text. Ready to paste."""


def format_generation_prompt(
    topic: str,
    latest_news_and_stats: str,
    custom_content: str,
    tone: str,
    content_type: list,
    target_word_count: int,
    engagement_level: str,
    narrative_patterns: list,
    creativity_level: float = 0.7,
    custom_instructions: str = ""
) -> str:
    """
    Format the user prompt with all parameters for VIRAL content generation.
    Includes 'Content DNA' randomization to prevent structural fatigue.
    """
    import random
    
    content_type_str = ", ".join(content_type) if content_type else "General"
    narrative_patterns_str = ", ".join(narrative_patterns) if narrative_patterns else "None"
    
    # Map engagement level to specific viral requirements
    engagement_mapping = {
        "Low": "Focus on value delivery, minimal controversy",
        "Medium": "Include 2 engagement triggers, moderate controversy",
        "High": "Maximum viral potential - use controversial hook, 3+ engagement triggers, bold stance"
    }
    
    viral_intensity = engagement_mapping.get(engagement_level, engagement_mapping["Medium"])
    
    # Map creativity level to descriptive instruction
    creativity_desc = "Balanced"
    if creativity_level < 0.4:
        creativity_desc = "Conservative, Strict, Professional"
    elif creativity_level > 0.8:
        creativity_desc = "Highly Creative, Experimental, Unique"

    structural_dna_options = [
        "RHYTHM: Staccato. Use very short, punchy sentences. Minimize conjunctions. Rapid-fire delivery.",
        "RHYTHM: Melodic. Use varied sentence lengths. Connect ideas smoothly with transitions (e.g., 'However', 'Consequently').",
        "STRUCTURE: The Loop. Open with a micro-story/analogy, switch to hard analysis, then close by referencing the initial story.",
        "STRUCTURE: Inverted Pyramid. Start with the single most shocking fact. Explain the 'Why'. End with the 'What now'.",
        "STYLE: Socratic. Use unexpected questions to guide the reader. Make them think before giving the answer.",
        "STYLE: The Devil's Advocate. Anticipate the reader's skepticism. Phrase as 'You might think X, but actually Y'.",
        "FORMAT: Axiomatic. Use bold, definitive statements as headers (e.g., '1. Chaos is Opportunity').",
        "STYLE: The Confession. Start with a humble admit of failure. Pivot to the lesson. Use highly vulnerable 'I' language.",
        "STRUCTURE: The Contrast. Explicitly compare 'Old Way' vs 'New Way' using bullet points.",
        "RHYTHM: The Listacle. 80% of the content should be a high-density numbered list with 1-sentence explanations.",
        "FLOW: The Narrative Hook. Start with a vivid 3-line scene (sensory details), then pivot to dry analysis. Cohesion: Use the scene as a recurring metaphor.",
        "RHYTHM: The Sophisticated Hybrid. 50% short sentences, 50% long, complex but clear sentences. Use colons (:) to build tension.",
        "STYLE: The Provocateur. Take an extremely bold stance in the first sentence. Back it up with calm, logical evidence."
    ]
    
    surprise_elements = [
        "Include a counter-intuitive analogy (e.g., Comparing AI to a bicycle for the mind).",
        "Open with a shocking personal failure you've never shared.",
        "Reference a piece of obscure history that mirrors the current trend.",
        "Challenge the 'Guru' of this sector by name or type.",
        "End with a prediction for exactly 12 months from today."
    ]
    
    hook_types = ["Shock/Surprise", "Contrarian", "Pattern Interrupt", "Curiosity Gap", "Social Proof", "Vulnerability", "Data-Driven"]
    mandatory_hook = random.choice(hook_types)
    surprise = random.choice(surprise_elements)
    
    # Content DNA Shuffler (Anti-Fatigue System)
    structural_dna = random.choice(structural_dna_options) if creativity_level >= 0.4 else "Standard Professional Flow"
    
    prompt = f"""**User Input Parameters:**
*   `TOPIC`: {topic}
*   `LATEST_NEWS_AND_STATS`: {latest_news_and_stats or "No specific news data available"}
*   `CUSTOM_CONTENT`: {custom_content or "No custom content provided"}
*   `TONE`: {tone}
*   `CONTENT_TYPE`: {content_type_str}
*   `TARGET_WORD_COUNT`: {target_word_count} words (±10% acceptable)
*   `ENGAGEMENT_LEVEL`: {engagement_level} - {viral_intensity}
*   `NARRATIVE_PATTERNS`: {narrative_patterns_str}
*   `CREATIVITY_SETTING`: {creativity_desc} (Temp: {creativity_level})

**STRUCTURAL DNA (CRITICAL FOR VARIETY):**
> **{structural_dna}**

**MANDATORY HOOK TYPE FOR THIS POST:**
> **{mandatory_hook}**

**SURPRISE ELEMENT (MANDATORY):**
> **{surprise}**

**STYLE OVERRIDE (USER SPECIFIED):**
> **{custom_instructions or "None"}**
> *If instructions are provided, they take absolute priority over all other stylistic rules.*

**VIRAL CONTENT GENERATION INSTRUCTIONS:**

1. **LENGTH ENFORCEMENT**:
   - Aim for EXACTLY {target_word_count} words. 
   - I will count them. If you are off by more than 10%, the post will be rejected.
   - Do not use filler to reach the count; use meaningful, punchy insights.

2. **SELECT VIRAL HOOK** (Mandatory - First Line):
   Choose the most appropriate hook type for this topic:
   - Shock/Surprise (for unexpected results/failures)
   - Contrarian (for challenging common beliefs)
   - Curiosity Gap (for insider knowledge)
   - Social Proof (for experience-based insights)
   - Vulnerability (for personal stories)
   - Data-Driven (for statistics/research)

2. **CHOOSE PROVEN STRUCTURE**:
   - Failure → Success Arc (best for personal stories)
   - Myth Buster (best for contrarian takes)
   - Framework/System (best for tactical advice)
   - Listicle with Insights (best for multiple points)

3. **INCLUDE ENGAGEMENT TRIGGERS** (Minimum 2-3):
   - Direct question to reader
   - Controversial/polarizing statement
   - FOMO element
   - Challenge to common belief
   - Personal vulnerability

4. **INTEGRATE PSYCHOLOGICAL TRIGGERS** (Minimum 3):
   - Reciprocity (give value first)
   - Scarcity ("most people miss this")
   - Authority (cite experience/credentials)
   - Social Proof (numbers, testimonials)
   - Loss Aversion ("avoid this mistake")

5. **OPTIMIZE FOR VIRALITY**:
   - Use "you" language (direct address)
   - Include specific numbers (odd numbers preferred: 3, 5, 7)
   - Make it shareable (reader looks smart for sharing)
   - Create emotional response
   - Provide actionable insights
   - End with clear CTA

6. **LINKEDIN FORMATTING**:
   - Target {target_word_count} WORDS (not characters)
   - Use bullet points for lists/key points
   - Include 1-2 emojis maximum (strategic placement)
   - Add 3-5 relevant hashtags at END
   - Line breaks every 2-3 lines
   - Short paragraphs for scannability

**VIRALITY VALIDATION (Check before finalizing):**
□ Hook grabs attention in 3 seconds?
□ Includes question or controversial statement?
□ Uses "you" language?
□ Has specific numbers/data?
□ Clear CTA at end?
□ Creates emotional response?
□ Shareable content?
□ Actionable insights?

Generate a LinkedIn post that GUARANTEES engagement and virality. Make it impossible to scroll past."""
    
    return prompt


def call_llm_for_analysis(
    content_to_analyze: str,
    analysis_type: str = "general"
) -> Optional[str]:
    """
    Call LLM for content analysis (insights, viral elements, sentiment).
    
    Args:
        content_to_analyze: Content to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        Analysis results or None if failed
    """
    system_prompt = """You are an expert content analyst specializing in LinkedIn posts and viral content.
Your task is to analyze provided content and extract:
1. Key insights and takeaways
2. Viral elements (surprising stats, hooks, emotional triggers)
3. Sentiment and tone analysis
4. Narrative potential

Provide concise, actionable analysis that can be used to craft engaging LinkedIn content."""
    
    user_prompt = f"""Analyze the following content for LinkedIn post creation:

{content_to_analyze}

Provide:
1. **Key Insights**: Main points and takeaways
2. **Viral Elements**: Surprising facts, statistics, or hooks
3. **Sentiment**: Overall tone and emotional resonance
4. **Narrative Potential**: Story angles and perspectives

Keep your analysis concise and actionable."""
    
    return call_openrouter(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=1000,
        temperature=0.5
    )


def call_llm_for_research_brief(
    topic: str,
    news_content: str
) -> Optional[str]:
    """
    Generate a research briefing with key insights and viral hook ideas.
    """
    system_prompt = """You are an elite Research Strategist. Your goal is to analyze current news and extract 
    highly viral, human-centric insights for LinkedIn. Avoid AI slop."""
    
    user_prompt = f"""TOPIC: {topic}
    NEWS DATA:
    {news_content}
    
    Based on the news above, provide:
    1. **Factual Summary per Source**: For each article, provide a 1-sentence summary focused ONLY on facts and data (e.g., "$3B investment", "Product X launched"). DO NOT ASSUME. If data is missing, state only the core event.
    2. **The Core Trend**: What is actually happening right now?
    3. **3 Counter-Intuitive Insights**: What do most people miss?
    4. **3 Viral Hook Ideas**: Write 3 hooks (under 12 words each) in "Shock", "Contrarian", and "Pattern Interrupt" styles.
    
    STRICT: No slop words and ZERO assumptions. If the news doesn't provide a data point, don't mention one."""
    
    return call_openrouter(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=800,
        temperature=0.7
    )


def verify_factual_accuracy(
    generated_content: str,
    original_context: str
) -> Dict[str, Any]:
    """
    Verify the factual accuracy of generated content against original context.
    
    Args:
        generated_content: The AI-generated LinkedIn post
        original_context: The original news/stats/custom content provided
        
    Returns:
        Dict with 'is_accurate' (bool), 'issues' (list), and 'corrected_content' (optional)
    """
    system_prompt = """You are a strict Fact-Checking Editor. Your ONLY job is to verify that the derived content accurately reflects the source material and DOES NOT invent specific statistics, numbers, or attribution.

RULES:
1. General knowledge is allowed.
2. Specific stats (e.g., "$50K in 30 days", "73% increase") MUST exist in the Source Context.
3. If a specific number/stat appears in the Content but NOT in the Context, it is a HALLUCINATION.
4. "Data-Driven" hooks must be supported by actual data in the context.

If you find hallucinations:
- Return valid JSON with "is_accurate": false
- List the specific "issues"
- Provide a "suggestion" to fix it (e.g., replace specific stat with general qualitative statement)

If accurate:
- Return valid JSON with "is_accurate": true"""

    user_prompt = f"""SOURCE CONTEXT:
{original_context}

GENERATED CONTENT:
{generated_content}

Verify factual accuracy. Check every number and specific claim.
Return JSON format: {{ "is_accurate": boolean, "issues": [list of strings], "suggestion": "string correction strategy if needed" }}"""

    try:
        response = call_openrouter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=500,
            temperature=0.0  # Zero temperature for strict logic
        )
        
        if not response:
            return {"is_accurate": True, "issues": [], "suggestion": None}  # Fail open if LLM fails
            
        import json
        # clean response of potential markdown code blocks
        clean_response = response.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_response)
        return result
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
        return {"is_accurate": True, "issues": [], "suggestion": None}  # Fail open on error


def call_llm_for_image_prompt(post_content: str) -> Optional[str]:
    """
    Generate a professional LinkedIn-optimized image prompt based on the post content.
    Balanced for token management and high-quality visual results.
    """
    system_prompt = """You are a professional Creative Director specializing in LinkedIn aesthetics.
    Your task: Create a CONCISE (max 50 words) image generation prompt for Midjourney/DALL-E based on a LinkedIn post.
    
    Aesthetic Guidelines:
    - Corporate-modern, tech-forward, but human-centric.
    - High-quality: Glassmorphism, soft gradients, natural lighting, 8k resolution.
    - Professional settings: Modern offices, collaborative spaces, or abstract conceptual art.
    - Diverse representations.
    
    Output Format:
    Only the prompt text. No quotes, no intro."""
    
    user_prompt = f"Create a professional image prompt for this post content:\n\n{post_content}"
    
    return call_openrouter(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=150,
        temperature=0.6
    )
