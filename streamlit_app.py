# streamlit_app.py

import streamlit as st
from tmc_api_client import TMCAPIClient
from tmc_config import Config
from tmc_auth import Auth
from display_functions import display_tasks_and_plans  # Import display functions


# Initialize configuration
config = Config()

# Set up page configuration
st.set_page_config(
    page_title="Talend Management Console (TMC)",
    page_icon="✨",
    layout="wide",
)


st.title("Vanakkam Thalaivaree! 🎉")
st.write("If you see this, Streamlit is working!")


# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        color: #3498db;
    }
    .card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .important {
        color: #e74c3c;
        font-weight: bold;
    }
    .success {
        color: #2ecc71;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token_set' not in st.session_state:
    st.session_state.token_set = False
if 'client' not in st.session_state:
    st.session_state.client = None
if 'workspaces' not in st.session_state:
    st.session_state.workspaces = None
if 'selected_workspace' not in st.session_state:
    st.session_state.selected_workspace = None
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None

st.write("Client:", st.session_state.client)
st.write("Token Set:", st.session_state.token_set)
st.write("Auth:", st.session_state.authenticated)


# Authentication function
def authenticate():
    auth = Auth()
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Authenticate"):
        if auth.verify_app_password(password):
            st.session_state.authenticated = True
            st.success("Authentication successful!")
            st.rerun()
        else:
            st.error("Authentication failed. Please try again.")

# Function to set token
def set_token():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        token = st.text_input("Enter TMC Authorization Token", type="password")
    
    with col2:
        if st.button("Set Token"):
            if token:
                # Store token in config
                config.add_recent_token(token)
                
                # Initialize client
                st.session_state.client = TMCAPIClient(token, config.get_base_url())
                st.session_state.token_set = True
                
                st.success("Token set successfully!")
                st.rerun()
            else:
                st.error("Please enter a token.")

# Function to fetch and display workspaces

def fetch_workspaces():
    st.markdown('<div class="section-header">Workspaces</div>', unsafe_allow_html=True)
    
    if st.button("Refresh Workspaces"):
        with st.spinner("Fetching workspaces..."):
            mappings = st.session_state.client.fetch_workspace_and_environment_mappings()
            st.session_state.workspaces = mappings
            st.success("Workspaces refreshed!")
            st.rerun()
    
    if st.session_state.workspaces is None:
        with st.spinner("Fetching workspaces..."):
            try:
                mappings = st.session_state.client.fetch_workspace_and_environment_mappings()
                st.session_state.workspaces = mappings
                st.success("Workspaces loaded!")
                print(st.session_state.workspaces)
            except Exception as e:
                st.error(f"Failed to fetch workspaces: {str(e)}")
                return
    
    # Display workspaces
    if st.session_state.workspaces:
        options = list(st.session_state.workspaces['workspaces'].keys())
        workspace_options = [f"{workspace_name} ({environment_name})" for workspace_name, environment_name in options]
        
        selected_option = st.selectbox("Select Workspace and Environment", workspace_options)
        workspace_name, environment_name = options[workspace_options.index(selected_option)]
        
        if selected_option:
            # Extract workspace name and environment name from the selected option
            workspace_name, environment_name = options[workspace_options.index(selected_option)]
            workspace_id = st.session_state.workspaces['workspaces'].get((workspace_name,environment_name))
            environment_id = st.session_state.workspaces['environments'].get(environment_name)
            print(workspace_id,environment_id)
            executable_name = st.text_input("Enter Task or Plan Name")
            print(executable_name)
            if executable_name:
            # Display tasks in a table with single selection
                display_tasks_and_plans(executable_name,workspace_id, environment_id)



# Ensure authentication first
if not st.session_state.authenticated:
    authenticate()

# If authenticated, proceed with the app
else:
    st.title("Talend Management Console (TMC) Dashboard")
    
    # Call the token-setting function
    set_token()
    
    # If the token is set, fetch and display workspaces
    if st.session_state.token_set:
        fetch_workspaces()

            