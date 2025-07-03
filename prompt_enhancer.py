def enhance_prompt(query):
    """Transform queries into beginner-friendly analytics requests"""
    # Simple mapping for common terms
    term_map = {
        "users": "number of visitors",
        "traffic": "website visits",
        "bounce": "visitors who left quickly",
        "device": "device type (phone, computer, tablet)",
        "country": "visitor location",
        "source": "where visitors came from",
        "page": "specific pages visited",
        "sessions": "visits to your site",
        "organic": "search engine traffic",
        "direct": "people typing your URL",
        "referral": "links from other sites"
    }
    
    # Explain technical terms
    enhanced = query
    for term, explanation in term_map.items():
        if term in enhanced.lower():
            enhanced = enhanced.replace(term, f"{term} ({explanation})")
    
    # Add date context if missing
    time_terms = ["yesterday", "week", "month", "year", "today", "ago"]
    if not any(term in enhanced.lower() for term in time_terms):
        enhanced += " for the last 30 days"
    
    # Add visualization suggestion
    if "chart" not in enhanced.lower() and "graph" not in enhanced.lower():
        if " by " in enhanced:
            enhanced += ". Show in an easy-to-understand bar chart"
        else:
            enhanced += ". Display in a simple table"
    
    # Add friendly explanation
    enhanced += " - Please explain what this means in simple terms!"
    
    return enhanced
