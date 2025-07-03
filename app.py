# app.py - Updated implementation

import streamlit as st
import json

# --- Settings Panel ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # LLM Provider Selection
    providers = ["OpenAI", "Claude", "Gemini", "Mistral", "Cohere", "Custom"]
    provider = st.selectbox("LLM Provider", providers)
    api_key = st.text_input("API Key", type="password")
    
    # Dynamic API Key Links
    provider_links = {
        "OpenAI": "https://platform.openai.com/account/api-keys",
        "Claude": "https://console.anthropic.com/settings/keys",
        "Gemini": "https://makersuite.google.com/app/apikey",
        "Mistral": "https://console.mistral.ai/api-keys",
        "Cohere": "https://dashboard.cohere.com/api-keys"
    }
    
    if provider in provider_links:
        st.markdown(f"[🔑 Get {provider} API Key]({provider_links[provider]})", unsafe_allow_html=True)
    
    # Google Analytics Settings
    st.divider()
    st.subheader("🔐 Google Analytics")
    
    ga_property_id = st.text_input(
        "GA4 Property ID",
        placeholder="e.g., 396502027",
        help="Find in GA4: Admin → Property Settings → Property Details"
    )
    
    uploaded_file = st.file_uploader(
        "Service Account JSON",
        type=["json"],
        help="Create in Google Cloud Console with GA4 Viewer permissions"
    )
    
    if st.button("Save Settings"):
        # Validate inputs
        if not api_key:
            st.error("API Key is required")
        elif not ga_property_id or not uploaded_file:
            st.error("Google Analytics settings are incomplete")
        else:
            # Save all settings to session_state
            st.session_state.llm_provider = provider
            st.session_state.api_key = api_key
            st.session_state.ga_property_id = ga_property_id
            st.session_state.ga_credentials = json.load(uploaded_file)
            st.success("Settings saved successfully!")

# --- Chat Interface ---
if 'ga_credentials' in st.session_state and 'api_key' in st.session_state:
    st.subheader("💬 Analytics Chat")
    
    # Get user query
    user_query = st.text_area("Ask about your analytics data:")
    
    if st.button("Submit", type="primary") and user_query:
        # Enhance and execute query
        enhanced_query = enhance_prompt(user_query)
        dimensions, metrics = extract_ga_parameters(enhanced_query)
        
        if dimensions and metrics:
            df = run_ga_report(dimensions, metrics)
            if not df.empty:
                display_results(df, enhanced_query)
        else:
            st.warning("Couldn't extract valid GA parameters from your query")
else:
    st.warning("Please configure your settings in the sidebar to begin")

# Disconnect button
if st.sidebar.button("Disconnect GA"):
    keys = ['llm_provider', 'api_key', 'ga_property_id', 'ga_credentials']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Deployment Instructions (commented out as per user's instructions)
# Update requirements.txt:
#     google-analytics-data==0.18.0
#     google-auth==2.29.0
#
# Add to README.md:
# ## User Configuration
#
# 1. **LLM Setup**:
#    - Select your AI provider
#    - Enter your API key
#    - Click "Save Settings"
#
# 2. **Google Analytics Setup**:
#    - Enter your GA4 Property ID (numeric ID)
#    - Upload Service Account JSON file
#    - Click "Save Settings"
#
# 3. **Start Chatting**:
#    - Ask questions about your analytics data
#    - Results will appear after processing
