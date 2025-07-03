from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.oauth2 import service_account
import pandas as pd
import streamlit as st

def run_ga_report(dimensions, metrics, date_range="30daysAgo"):
    """Run GA4 report using session state credentials"""
    if 'ga_credentials' not in st.session_state or 'ga_property_id' not in st.session_state:
        st.error("Google Analytics settings not configured")
        return pd.DataFrame()
    
    try:
        # Get credentials from session state
        credentials = service_account.Credentials.from_service_account_info(
            st.session_state.ga_credentials,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        request = RunReportRequest(
            property=f"properties/{st.session_state.ga_property_id}",
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=date_range, end_date="today")],
        )
        
        response = client.run_report(request)
        
        # Parse response to DataFrame
        dim_headers = [header.name for header in response.dimension_headers]
        met_headers = [header.name for header in response.metric_headers]
        
        rows = []
        for row in response.rows:
            row_data = [dim.value for dim in row.dimension_values]
            row_data += [met.value for met in row.metric_values]
            rows.append(row_data)
            
        return pd.DataFrame(rows, columns=dim_headers + met_headers)
    
    except Exception as e:
        st.error(f"GA Query Error: {str(e)}")
        return pd.DataFrame()
