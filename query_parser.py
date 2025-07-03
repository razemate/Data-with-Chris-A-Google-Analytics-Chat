import re

def extract_ga_parameters(query):
    """Extract dimensions and metrics from natural language query"""
    # Predefined GA4 parameters
    valid_dimensions = ["country", "city", "deviceCategory", "pagePath", "sourceMedium"]
    valid_metrics = ["activeUsers", "sessions", "bounceRate", "avgSessionDuration"]
    
    # Extract mentioned parameters
    found_dimensions = [dim for dim in valid_dimensions if dim in query]
    found_metrics = [met for met in valid_metrics if met in query]
    
    # Add defaults if none found
    if not found_dimensions:
        found_dimensions = ["deviceCategory"]
    if not found_metrics:
        found_metrics = ["activeUsers"]
    
    return found_dimensions, found_metrics