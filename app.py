
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.io as pio
from ga_query import run_ga_report
from prompt_enhancer import enhance_prompt
import export_utils
import re

# Initialize session state
if "ga_property_id" not in st.session_state:
    st.session_state.ga_property_id = ""
if "ga_credentials" not in st.session_state:
    st.session_state.ga_credentials = None
if "history" not in st.session_state:
    st.session_state.history = []
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "OpenAI"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Page configuration
st.set_page_config(
    page_title="GA4 Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("📊 GA4 Analytics Assistant")
st.caption("Chat with your Google Analytics data - No technical skills needed!")

# ===== SIDEBAR SETTINGS =====
with st.sidebar:
    st.header("⚙️ Settings")
    
    # New User Onboarding
    if 'ga_credentials' not in st.session_state:
        with st.expander("✨ Getting Started Guide", expanded=True):
            st.markdown("""
            **Welcome! Follow these simple steps:**
            1. **Connect Google Analytics** below
            2. **Choose an AI assistant** (like ChatGPT)
            3. **Ask questions** about your data
            4. **Get instant reports** with charts
            
            👉 Need help? [Watch setup tutorial](https://youtu.be/GA4SetupTutorial)
            """)
    
    # Google Analytics Setup
    with st.expander("🔐 Google Analytics Setup", expanded=True):
        # Help section
        with st.expander("❓ How to Set Up Access", expanded=True):
            st.markdown("""
            **Follow these simple steps:**  
            
            1. **Get Property ID**  
               [Open Google Analytics](https://analytics.google.com/) → Admin → Property Settings → Property Details → Copy the numeric ID  
               ![Property ID](https://i.imgur.com/XYdZ4cU.png =200x)  
            
            2. **Create a Google Service Account (for Analytics Access)**  
               - [Open Google Cloud Console](https://console.cloud.google.com/)
               - Click the project drop-down (top left) and select **New Project** (or choose your existing project)
               - In the left menu, go to **IAM & Admin → Service Accounts**
               - Click **Create Service Account**
               - Enter a name (e.g., "GA4 Assistant") and click **Create and Continue**
               - Under "Grant this service account access", select **Viewer** role (or **Basic > Viewer**)
               - Click **Done**
               - Click your new service account in the list
               - Go to the **Keys** tab, click **Add Key → Create new key**
               - Choose **JSON** and click **Create** (this downloads the file you'll upload here)

            3. **Grant Service Account Access in Google Analytics**  
               - Go to [Google Analytics](https://analytics.google.com/) → Admin
               - Under **Property**, click **Property Access Management**
               - Click the blue **+** button → **Add users**
               - Paste the service account email (from the JSON file)
               - Assign the **Viewer** role
               - Click **Add**
            """)
        
        # Input fields
        property_id = st.text_input(
            "GA4 Property ID", 
            placeholder="e.g., 396502027",
            help="Numeric ID from Google Analytics property details",
            key="ga_property_input"
        )
        
        uploaded_file = st.file_uploader(
            "Service Account JSON File", 
            type=["json"],
            help="Downloaded from Google Cloud Console",
            key="ga_json_upload"
        )
        
        # Auto-connect: load credentials from local file if available
        import os
        cred_path = os.path.join(os.path.expanduser("~"), ".ga4_assistant_credentials.json")
        propid_path = os.path.join(os.path.expanduser("~"), ".ga4_assistant_propertyid.txt")
        auto_connected = False
        if os.path.exists(cred_path) and os.path.exists(propid_path):
            try:
                with open(cred_path, "r") as f:
                    credentials = json.load(f)
                with open(propid_path, "r") as f:
                    property_id = f.read().strip()
                st.session_state.ga_credentials = credentials
                st.session_state.ga_property_id = property_id
                st.info(f"✅ Auto-connected to GA4 Property: **{property_id}** (from previous session)")
                auto_connected = True
            except Exception:
                pass

        # Save button
        if st.button("🔗 Connect Google Analytics", type="primary", use_container_width=True):
            if not property_id or not uploaded_file:
                st.error("Please complete both fields")
            elif not re.match(r'^\d{5,12}$', property_id):
                st.error("Property ID must be 5-12 digit number")
            else:
                try:
                    credentials = json.load(uploaded_file)
                    required_keys = ["type", "project_id", "private_key_id", "private_key"]
                    if not all(key in credentials for key in required_keys):
                        st.error("Invalid service account file - please re-download from Google Cloud")
                    else:
                        st.session_state.ga_property_id = property_id
                        st.session_state.ga_credentials = credentials
                        # Save credentials and property id for auto-connect next time
                        with open(cred_path, "w") as f:
                            json.dump(credentials, f)
                        with open(propid_path, "w") as f:
                            f.write(property_id)
                        st.success(f"✅ Connected to GA4 Property: {property_id} (will auto-connect next time)")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format - please upload the exact file from Google Cloud")

        # Connection status
        if 'ga_credentials' in st.session_state:
            st.info(f"Connected to GA4 Property: **{st.session_state.ga_property_id}**")
            if st.button("Disconnect Google Analytics", use_container_width=True):
                keys = ['ga_credentials', 'ga_property_id']
                for key in keys:
                    if key in st.session_state:
                        del st.session_state[key]
                # Remove saved credentials
                if os.path.exists(cred_path):
                    os.remove(cred_path)
                if os.path.exists(propid_path):
                    os.remove(propid_path)
                st.rerun()
    
    # LLM Provider Selection
    st.divider()
    st.subheader("🤖 AI Assistant Setup")
    
    providers = ["OpenAI (ChatGPT)", "Claude", "Gemini (Google)", "Mistral", "Cohere", "Custom"]
    provider = st.selectbox("Choose AI Provider", providers, index=0)
    
    api_key = st.text_input(
        "API Key", 
        type="password",
        help="Get this from your AI provider's website",
        placeholder="sk-... or similar"
    )
    
    # Dynamic API Key Links
    provider_links = {
        "OpenAI (ChatGPT)": "https://platform.openai.com/account/api-keys",
        "Claude": "https://console.anthropic.com/settings/keys",
        "Gemini (Google)": "https://makersuite.google.com/app/apikey",
        "Mistral": "https://console.mistral.ai/api-keys",
        "Cohere": "https://dashboard.cohere.com/api-keys"
    }
    
    if provider in provider_links:
        st.markdown(f"🔑 [Get {provider.split(' ')[0]} API Key]({provider_links[provider]})", unsafe_allow_html=True)
    
    import os
    llm_path = os.path.join(os.path.expanduser("~"), ".ga4_assistant_llm.json")
    # Auto-load LLM settings if available
    if os.path.exists(llm_path):
        try:
            with open(llm_path, "r") as f:
                llm_data = json.load(f)
            st.session_state.llm_provider = llm_data.get("provider", provider)
            st.session_state.api_key = llm_data.get("api_key", api_key)
            st.info(f"✅ Auto-loaded AI provider: {st.session_state.llm_provider}")
        except Exception:
            pass

    if st.button("💾 Save AI Settings", use_container_width=True):
        st.session_state.llm_provider = provider
        st.session_state.api_key = api_key
        # Save to file for auto-connect next time
        with open(llm_path, "w") as f:
            json.dump({"provider": provider, "api_key": api_key}, f)
        st.success("AI settings saved! (will auto-load next time)")

    # Option to clear saved LLM settings
    if os.path.exists(llm_path):
        if st.button("Clear Saved AI Settings", use_container_width=True):
            os.remove(llm_path)
            st.session_state.llm_provider = "OpenAI"
            st.session_state.api_key = ""
            st.success("Saved AI settings cleared.")
    
    # Sample Queries
    st.divider()
    st.subheader("💡 Sample Questions")
    
    samples = {
        "Users by device": "Compare visitors using phones vs computers",
        "Top countries": "See where your visitors are located",
        "Popular pages": "Find your most visited content",
        "Traffic sources": "Discover how people find your site",
        "New vs returning": "See how many visitors come back"
    }
    
    for query, explanation in samples.items():
        if st.button(f"{query}: {explanation}", use_container_width=True):
            st.session_state.user_query = query

# ===== MAIN CONTENT =====
# New user onboarding
if 'ga_credentials' not in st.session_state:
    st.info("""
    👋 **Welcome to the GA4 Analytics Assistant!**  
    To get started:
    1. Open the sidebar (←)
    2. Connect your Google Analytics account
    3. Choose and configure your AI assistant
    4. Ask questions about your analytics data!
    """)
    st.image("https://i.imgur.com/5X6JZ9l.png", caption="Analytics Made Simple")
    st.stop()

# Chat interface
st.subheader("💬 Ask About Your Data")
enable_enhancement = st.checkbox("Enable Smart Query Enhancement", value=True, 
                                help="We'll improve your questions for better results")

# Query input
user_query = st.text_area(
    "Ask anything about your analytics:",
    value=st.session_state.get("user_query", ""),
    placeholder="e.g., 'Show me users by device for last month'",
    height=100,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 3])
with col1:
    submit = st.button("🚀 Get Report", type="primary", use_container_width=True)
with col2:
    st.caption("Examples: 'Users by country', 'Top pages', 'Mobile vs desktop traffic'")


# Chart generation function
def generate_chart(df, query):
    if df is None or df.empty or len(df.columns) < 2:
        return None
    q = query.lower()
    if " by " in q:
        return px.bar(df, x=df.columns[0], y=df.columns[1], title=f"{query}", color=df.columns[0])
    elif " over time" in q or "trend" in q or "date" in q:
        return px.line(df, x=df.columns[0], y=df.columns[1], title=f"{query} Trend")
    elif "proportion" in q or "percentage" in q or "share" in q:
        return px.pie(df, names=df.columns[0], values=df.columns[1], title=f"{query} Distribution")
    elif "scatter" in q or "correlation" in q:
        if len(df.columns) >= 3:
            return px.scatter(df, x=df.columns[1], y=df.columns[2], color=df.columns[0], title=f"{query} Correlation")
        else:
            return px.scatter(df, x=df.columns[0], y=df.columns[1], title=f"{query} Correlation")
    else:
        return None

# Process query
if submit and user_query.strip():
    # Enhance prompt
    if enable_enhancement:
        enhanced_query = enhance_prompt(user_query)
        st.session_state.enhanced_query = enhanced_query
    else:
        st.session_state.enhanced_query = user_query

    # Store in history
    st.session_state.history.append({
        "original": user_query,
        "enhanced": st.session_state.enhanced_query
    })

    # Show enhanced prompt
    st.divider()
    st.subheader("🔍 Your Enhanced Question")
    st.info(st.session_state.enhanced_query)

    # Get data from GA (simulated for now)
    st.subheader("📊 Your Report")

    # Sample data - in real app this would come from GA
    sample_data = pd.DataFrame({
        "Device": ["Desktop", "Mobile", "Tablet"],
        "Users": [1200, 850, 150],
        "Sessions": [1800, 920, 180],
        "Bounce Rate": [25, 42, 35]
    })

    # Display table
    st.dataframe(sample_data, use_container_width=True)

    # Generate and display chart
    fig = generate_chart(sample_data, user_query)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # Export options
    st.divider()
    st.subheader("📤 Export Report")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button("💾 CSV", sample_data.to_csv(), "analytics.csv")
    with col2:
        st.download_button("📊 Excel", export_utils.to_excel(sample_data, fig=fig), "analytics.xlsx")
    with col3:
        st.download_button("📄 PDF", export_utils.to_pdf(sample_data, fig=fig), "analytics.pdf")
    with col4:
        st.download_button("📝 Word", export_utils.to_word(sample_data, fig=fig), "analytics.docx")

# Query History
st.divider()
st.subheader("🕒 Your Question History")

if not st.session_state.history:
    st.info("Your questions will appear here after you ask them")
else:
    for i, item in enumerate(st.session_state.history[::-1]):
        with st.expander(f"{i+1}. {item['original'][:50]}...", expanded=False):
            st.caption(f"**Enhanced version:** {item['enhanced']}")
            if st.button("Re-run this question", key=f"rerun_{i}"):
                st.session_state.user_query = item['original']
                st.rerun()
