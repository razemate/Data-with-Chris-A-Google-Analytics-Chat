st.title("GA Query Assistant")

import streamlit as st

# --- Settings Panel ---
st.sidebar.header("Settings")

# LLM Providers and API key URLs
llm_providers = {
    "OpenAI": "https://platform.openai.com/account/api-keys",
    "Claude": "https://console.anthropic.com/settings/keys",
    "Gemini": "https://makersuite.google.com/app/apikey",
    "Mistral": "https://console.mistral.ai/api-keys",
    "Cohere": "https://dashboard.cohere.com/api-keys"
}
llm_list = list(llm_providers.keys()) + ["Other (custom)"]
llm_choice = st.sidebar.selectbox("LLM Provider", llm_list)

if llm_choice in llm_providers:
    api_key_url = llm_providers[llm_choice]
    st.sidebar.markdown(f"[Create API Key for {llm_choice}]({api_key_url})", unsafe_allow_html=True)
    api_key_label = f"{llm_choice} API Key"
else:
    api_key_label = "LLM API Key"

llm_api_key = st.sidebar.text_input(api_key_label, type="password")
ga_property_id = st.sidebar.text_input("Google Analytics Property ID")

if st.sidebar.button("Save Settings"):
    st.session_state["llm_choice"] = llm_choice
    st.session_state["llm_api_key"] = llm_api_key
    st.session_state["ga_property_id"] = ga_property_id
    st.sidebar.success("Settings saved!")

# --- Chat Interface ---
st.title("LLM Analytics Assistant (Prototype)")

st.markdown("""
- Select your LLM provider and enter your API key in the sidebar.
- Enter your Google Analytics Property ID.
- This prototype shows hardcoded output and dynamic API key link.
""")

query = st.text_area("Describe the data you need:")
if st.button("Submit"):
    st.write("**Original Query:**", query)
    # Hardcoded enhanced prompt for prototype
    enhanced = f"[Enhanced] {query}"
    st.write("**Enhanced Prompt:**", enhanced)
    st.info("(LLM and GA4 integration coming soon)")
