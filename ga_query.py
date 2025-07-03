from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
from google.oauth2 import service_account
from google.api_core.exceptions import PermissionDenied, InvalidArgument
import pandas as pd
import streamlit as st

def run_ga_report(dimensions, metrics, date_range="30daysAgo"):
    """Run GA4 report with beginner-friendly error handling"""
    if 'ga_credentials' not in st.session_state:
        st.error("🔌 Please connect Google Analytics first using the sidebar")
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
    
    except PermissionDenied:
        st.error("""
        ❌ Permission denied! Please verify:
        1. Service account has **Viewer** access in GA4
        2. You've added the service account email in GA4 Admin
        3. Waited 5-10 minutes after granting permissions
        """)
        return pd.DataFrame()
        
    except InvalidArgument as e:
        st.error(f"""
        ❌ Invalid request: {str(e)}
        
        **Common fixes:**
        - Check your property ID is correct
        - Verify dimensions/metrics exist in GA4
        - [GA4 Dimensions & Metrics Reference](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)
        """)
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"""
        ❌ Unexpected error: {str(e)}
        
        **Troubleshooting:**
        - Try reconnecting Google Analytics
        - Check your GA4 property has data
        - [Get Help](https://support.google.com/analytics)
        """)
        return pd.DataFrame()
