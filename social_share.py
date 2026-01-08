"""
Social Media Sharing Utilities
Generates share links for various social platforms
"""

import urllib.parse
from typing import Dict


def generate_linkedin_share_url(text: str) -> str:
    """
    Generate LinkedIn share URL.
    Note: LinkedIn doesn't support pre-filled text via URL, so this opens the share dialog.
    
    Args:
        text: Post content
        
    Returns:
        LinkedIn share URL
    """
    # LinkedIn share URL (opens share dialog)
    base_url = "https://www.linkedin.com/sharing/share-offsite/"
    return base_url


def generate_twitter_share_url(text: str) -> str:
    """
    Generate Twitter/X share URL with pre-filled text.
    
    Args:
        text: Tweet content (will be truncated to 280 chars if needed)
        
    Returns:
        Twitter share URL
    """
    # Truncate to Twitter's character limit
    tweet_text = text[:280] if len(text) > 280 else text
    encoded_text = urllib.parse.quote(tweet_text)
    
    return f"https://twitter.com/intent/tweet?text={encoded_text}"


def generate_facebook_share_url(text: str) -> str:
    """
    Generate Facebook share URL.
    Note: Facebook doesn't support pre-filled text for privacy reasons.
    
    Args:
        text: Post content (not used, but kept for consistency)
        
    Returns:
        Facebook share URL
    """
    return "https://www.facebook.com/sharer/sharer.php"


def get_all_share_urls(text: str) -> Dict[str, str]:
    """
    Get share URLs for all supported platforms.
    
    Args:
        text: Post content
        
    Returns:
        Dict mapping platform name to share URL
    """
    return {
        "linkedin": generate_linkedin_share_url(text),
        "twitter": generate_twitter_share_url(text),
        "facebook": generate_facebook_share_url(text)
    }


def format_for_linkedin(text: str) -> str:
    """
    Format text optimally for LinkedIn.
    Ensures proper line breaks and formatting.
    
    Args:
        text: Raw post content
        
    Returns:
        LinkedIn-formatted text
    """
    # LinkedIn preserves line breaks
    return text.strip()


def format_for_twitter(text: str, max_length: int = 280) -> str:
    """
    Format text for Twitter with character limit.
    
    Args:
        text: Raw post content
        max_length: Maximum character length (default 280)
        
    Returns:
        Twitter-formatted text
    """
    if len(text) <= max_length:
        return text
    
    # Truncate and add ellipsis
    return text[:max_length-3] + "..."


def copy_to_clipboard_js(text: str) -> str:
    """
    Generate JavaScript code to copy text to clipboard.
    
    Args:
        text: Text to copy
        
    Returns:
        JavaScript code string
    """
    # Escape quotes in text
    escaped_text = text.replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")
    
    js_code = f"""
    <script>
    function copyToClipboard() {{
        const text = `{escaped_text}`;
        navigator.clipboard.writeText(text).then(function() {{
            alert('✅ Copied to clipboard!');
        }}, function(err) {{
            alert('❌ Failed to copy: ' + err);
        }});
    }}
    </script>
    """
    
    return js_code
