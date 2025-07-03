def enhance_prompt(user_query):
    """Enhance analytics queries using user-specific terminology"""
    # Get GA property name from session state if available
    property_name = st.session_state.get('ga_property_name', 'your analytics')
    
    enhancement_map = {
        "users": "activeUsers",
        "traffic": "sessions",
        "bounce": "bounceRate",
        "device": "deviceCategory",
        "country": "country",
        "source": "sourceMedium",
        "page": "pagePath",
        "city": "city"
    }
    
    # Simple enhancement rules
    enhanced = user_query.lower()
    for term, replacement in enhancement_map.items():
        enhanced = enhanced.replace(term, replacement)
    
    # Add context if missing
    if "date" not in enhanced:
        enhanced += " for the last 30 days"
    
    if "chart" not in enhanced:
        enhanced += ". Display results in a bar chart and table"
    
    return f"Generate {property_name} report: {enhanced.capitalize()}"
