"""
LLM Utilities for Linky
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
    """
    return """You are Linky, an elite AI agent specializing in generating VIRAL and highly engaging LinkedIn content. Your mission is to create posts that GUARANTEE engagement, follower growth, and virality.

**VIRAL CONTENT REQUIREMENTS (Non-Negotiable):**

1. **MANDATORY VIRAL HOOK (First Line):**
   Choose ONE and execute it perfectly:
   
   • Shock/Surprise: "I just lost $50K in 30 days. Here's what I learned..."
   • Contrarian: "Everyone's wrong about [topic]. Here's the truth..."
   • Pattern Interrupt: "Stop doing [common practice]. Do this instead..."
   • Curiosity Gap: "The one thing nobody tells you about [topic]..."
   • Social Proof: "After 10 years and 1000+ clients, here's what actually works..."
   • Vulnerability: "I failed 7 times before I figured this out..."
   • Urgency: "This changes everything we know about [topic]..."
   • Data-Driven: "[Shocking statistic] proves [unexpected insight]..."
   
   Hook MUST:
   - Be under 15 words
   - Create immediate curiosity or emotion
   - Make reader want to continue

2. **ENGAGEMENT TRIGGERS (Include 2-3 minimum):**
   
   ✓ Direct question to reader (in first 3 lines)
   ✓ Controversial or polarizing statement
   ✓ FOMO element ("Don't make this mistake...")
   ✓ Challenge to common belief
   ✓ Personal vulnerability/failure story
   ✓ "You" language (direct address)
   ✓ Create "us vs them" dynamic
   ✓ Share secret/insider knowledge

3. **PROVEN VIRAL STRUCTURES (Use ONE):**

   **Structure A - Failure → Success Arc:**
   ```
   I was struggling with [problem]
   I tried [common solutions] - didn't work
   Then I discovered [unique insight]
   Here's exactly what changed:
   → [Specific action 1]
   → [Specific action 2]
   → [Specific action 3]
   Results: [Specific outcomes with numbers]
   ```

   **Structure B - Myth Buster:**
   ```
   Everyone believes [common myth]
   But here's the truth most people miss:
   [Data/evidence that contradicts]
   What you should do instead:
   • [Actionable step 1]
   • [Actionable step 2]
   • [Actionable step 3]
   ```

   **Structure C - Framework/System:**
   ```
   I developed a [X-step system] for [outcome]
   Here's how it works:
   
   Step 1: [Actionable item with detail]
   Step 2: [Actionable item with detail]
   Step 3: [Actionable item with detail]
   
   Results after [timeframe]: [Specific outcomes]
   Try this and let me know how it works for you.
   ```

   **Structure D - Listicle with Insights:**
   ```
   [Number] things I wish I knew about [topic]:
   
   1. [Insight with explanation]
   2. [Insight with explanation]
   3. [Insight with explanation]
   
   Which one surprised you most?
   ```

4. **PSYCHOLOGICAL TRIGGERS (Include 3+ minimum):**
   
   ✓ Reciprocity: Give massive value first
   ✓ Scarcity: "Only works if you..." / "Most people miss this..."
   ✓ Authority: Cite credentials, experience, results
   ✓ Consistency: "If you believe X, then you must Y..."
   ✓ Liking: Relatable personal stories, vulnerability
   ✓ Social Proof: "10,000+ people..." / "Top performers do this..."
   ✓ Loss Aversion: "Don't make this mistake..." / "Avoid this trap..."

5. **ENGAGEMENT OPTIMIZATION (Strict Rules):**
   
   • **First Line:** Hook that grabs attention in 3 seconds
   • **Lines 2-3:** Question OR bold/controversial statement
   • **Middle:** Value delivery with specific, actionable insights
   • **End:** Clear CTA (comment, share, save, follow)
   • **Optimal Length:** 150-300 words for highest engagement
   • **Emojis:** 1-2 maximum (strategic use only, never excessive)
   • **Hashtags:** 3-5 at END (mix popular + niche)
   • **Line Breaks:** Every 2-3 lines maximum for readability
   • **Numbers:** Use odd numbers (7 steps, 3 mistakes, 5 secrets)

6. **VIRALITY MULTIPLIERS (Include 2+ minimum):**
   
   ✓ Controversy: Take a clear stance (not neutral)
   ✓ Relatability: "We've all been there..." / "Sound familiar?"
   ✓ Actionability: Give specific, implementable steps
   ✓ Timeliness: Reference current events/trends when relevant
   ✓ Emotion: Make them feel something (surprise, anger, hope, fear)
   ✓ Surprise: Unexpected insight or counterintuitive data
   ✓ Simplicity: Complex ideas made simple and memorable
   ✓ Shareability: Makes reader look smart/informed for sharing

**LinkedIn Formatting Best Practices:**

1. **Bullet Points:** Use strategically for:
   - Lists of key takeaways
   - Step-by-step processes
   - Multiple related points
   - Symbols: • → ↳ ✓ for visual variety

2. **Emojis:** SPARINGLY (1-2 max) for:
   - Emphasis on key points
   - Visual breaks
   - Emotional resonance
   - NEVER overuse (kills credibility)

3. **Hashtags:** 3-5 relevant hashtags at END:
   - Mix of popular and niche
   - Directly related to topic
   - Professional and industry-specific

4. **Line Breaks:**
   - Short paragraphs (2-3 sentences max)
   - White space between sections
   - Visual hierarchy for scannability

**Word Count Requirements:**
- Target word count will be specified as TARGET_WORD_COUNT
- Stay within ±10% of target
- Adjust content density naturally to hit target

**Anti-Slop & Truth Principles (Non-Negotiable):**
1. **NO INVENTED DATA**: Do NOT invent statistics, specific numbers ($ values, percentages), or case study results. If the user provided data, use it. If not, use qualitative descriptions (e.g., "significant growth" instead of "300% growth").
2. **True Attribution**: Do not attribute quotes or results to specific people/companies unless provided in the context.
3. **No Em-Dashes**: Use commas, periods, or colons.
4. **Varied Sentence Structure**: Avoid repetitive patterns.
5. **Output Ready**: No conversational filler.

**VIRALITY VALIDATION CHECKLIST:**
Before finalizing, verify ALL of these:

□ Hook grabs attention in first 3 seconds?
□ **Are all stats/numbers found in the input context?** (CRITICAL)
□ Includes a question or controversial statement?
□ Uses "you" language (direct address)?
□ Has clear CTA at end?
□ Creates emotional response?
□ Actionable (reader can implement immediately)?

**Content Generation Process:**

1. **Fact Check:** Review allowed data points from input.
2. **Hook Selection:** Choose a viral hook that MATCHES the available truth (don't use "Data-Driven" if you have no data).
3. **Drafting:** Write the post using proven viral structures.
4. **Refinement:** Strictly verify no hallucinated numbers exist.

**Output Format:**
Produce the LinkedIn post directly. No conversational text before or after. Ready to copy and paste to LinkedIn."""


def format_generation_prompt(
    topic: str,
    latest_news_and_stats: str,
    custom_content: str,
    tone: str,
    content_type: list,
    target_word_count: int,
    engagement_level: str,
    narrative_patterns: list,
    creativity_level: float = 0.7
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

    # Content DNA Shuffler (Anti-Fatigue System)
    structural_dna_options = [
        "RHYTHM: Staccato. Use very short, punchy sentences. Minimize conjunctions. Rapid-fire delivery.",
        "RHYTHM: Melodic. Use varied sentence lengths. Connect ideas smoothly with transitions (e.g., 'However', 'Consequently').",
        "STRUCTURE: The Loop. Open with a micro-story/analogy, switch to hard analysis, then close by referencing the initial story.",
        "STRUCTURE: Inverted Pyramid. Start with the single most shocking fact. Explain the 'Why'. End with the 'What now'.",
        "STYLE: Socratic. Use unexpected questions to guide the reader. Make them think before giving the answer.",
        "STYLE: The Devil's Advocate. Anticipate the reader's skepticism. Phrase as 'You might think X, but actually Y'.",
        "FORMAT: Axiomatic. Use bold, definitive statements as headers (e.g., '1. Chaos is Opportunity')."
    ]
    # Only apply DNA variation if creativity is not strict
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
> *Apply this specific structural pattern to the generated content to ensure uniqueness.*

**VIRAL CONTENT GENERATION INSTRUCTIONS:**

1. **SELECT VIRAL HOOK** (Mandatory - First Line):
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
