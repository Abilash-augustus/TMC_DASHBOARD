# display_functions.py

import streamlit as st
import pandas as pd
import json
from tmc_api_client import TMCAPIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import time


def display_task_details(task_details):
   # Task Details Header
    st.markdown(f"## 🛠️ Task: **{task_details.get('name', 'N/A')}**")
    st.markdown(f"**ID:** `{task_details.get('id', 'N/A')}`")
    
    # General Info Section
    with st.expander("📋 General Info"):
        workspace = task_details.get('workspace', {})
        environment = workspace.get('environment', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Workspace:**")
            st.write(f"- Name: `{workspace.get('name', 'N/A')}`") #, expanded=True
            st.write(f"- ID: `{workspace.get('id', 'N/A')}`")
            st.write(f"- Owner: `{workspace.get('owner', 'N/A')}`")
        with col2:
            st.markdown("**Environment:**")
            st.write(f"- Name: `{environment.get('name', 'N/A')}`")
            st.write(f"- ID: `{environment.get('id', 'N/A')}`")
            st.write(f"- Default: `{environment.get('default', 'N/A')}`")
    
    # Artifact Details Section
    with st.expander("📦 Artifact Details"):
        artifact = task_details.get('artifact', {})
        st.markdown("**Artifact:**")
        st.write(f"- Name: `{artifact.get('name', 'N/A')}`")
        st.write(f"- ID: `{artifact.get('id', 'N/A')}`")
        st.write(f"- Version: `{artifact.get('version', 'N/A')}`")
    
    # Connections Section
    with st.expander("🔗 Connections"):
        connections = task_details.get('connections', {})
        st.markdown("**Connections:**")
        if connections:
            for connection_name, connection_id in connections.items():
                connection_details = st.session_state.client.get_connection_details(connection_id)
                connection_name = connection_details.get('name', 'N/A')
                st.write(f"- **{connection_name}** (ID: `{connection_id}`)")
        else:
            st.write("No connections found.")
    
    # Parameters Section
    with st.expander("⚙️ Parameters"):
        parameters = task_details.get('parameters', {})
        st.markdown("**Parameters:**")
        if parameters:
            for param_name, param_value in parameters.items():
                st.write(f"- **{param_name}:** `{param_value}`")
        else:
            st.write("No parameters found.")
    
    # Pause Details Section (Optional)
    with st.expander("⏸️ Pause Details"):
        pause_details = task_details.get('taskPauseDetails', {})
        if pause_details:
            st.markdown("**Pause Status:**")
            st.write(f"- Paused: `{pause_details.get('pause', 'N/A')}`")
            st.write(f"- Pause Date: `{pause_details.get('pauseDate', 'N/A')}`")
            st.write(f"- User: `{pause_details.get('user', 'N/A')}`")
            st.write(f"- User Type: `{pause_details.get('userType', 'N/A')}`")
        else:
            st.write("No pause details available.")
    
    # Auto Upgrade Info Section (Optional)
    with st.expander("🔄 Auto Upgrade Info"):
        auto_upgrade_info = task_details.get('autoUpgradeInfo', {})
        if auto_upgrade_info:
            st.markdown("**Auto Upgrade:**")
            st.write(f"- Auto Upgradable: `{auto_upgrade_info.get('autoUpgradable', 'N/A')}`")
            st.write(f"- Override With Default Parameters: `{auto_upgrade_info.get('overrideWithDefaultParameters', 'N/A')}`")
        else:
            st.write("No auto upgrade info available.")


def display_plan_details(plan_details):
    # Plan Details Header
    st.markdown(f"## 📋 Plan: **{plan_details.get('name', 'N/A')}**")
    st.markdown(f"**ID:** `{plan_details.get('executable', 'N/A')}`")
    
    # General Info Section
    with st.expander("📋 General Info", expanded=True):
        workspace = plan_details.get('workspace', {})
        environment = workspace.get('environment', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Workspace:**")
            st.write(f"- Name: `{workspace.get('name', 'N/A')}`")
            st.write(f"- ID: `{workspace.get('id', 'N/A')}`")
        with col2:
            st.markdown("**Environment:**")
            st.write(f"- Name: `{environment.get('name', 'N/A')}`")
            st.write(f"- ID: `{environment.get('id', 'N/A')}`")
    
    # Recursive function to display steps and tasks
    def display_step(step, step_number):
        st.markdown(f"##### Tasks in Step {step_number}")
        # st.write(f"- **Step ID:** `{step.get('stepId', 'N/A')}`")
        # st.write(f"- **Step Name:** `{step.get('stepName', 'N/A')}`")
        #st.write(f"- **Previous Status:** `{step.get('status', 'N/A')}`")
        
        # Display tasks (flows) in the current step
        flows = step.get('flows', [])
        if flows:
            for flow in flows:
                st.markdown(f" Task: **{flow.get('name', 'N/A')}**")
                st.write(f"- **ID:** `{flow.get('id', 'N/A')}`")
                st.write(f"- **Engine:** `{flow.get('destination', 'N/A')}`")
                st.write(f"- **Artifact Name:** `{flow.get('artifactShortVersion', {}).get('artifactName', 'N/A')}`")
        else:
            st.write("No tasks found in this step.")
        
        # Recursively display the next step (if available)
        next_step = step.get('nextStep', {})
        if next_step:
            display_step(next_step, step_number + 1)
    
    # Chart Section (Dynamic Steps)
    with st.expander("📊 Plan Steps and Tasks", expanded=True):
        chart = plan_details.get('chart', {})
        if chart:
            display_step(chart, step_number=1)  # Start with Step 1
        else:
            st.write("No chart details available.")
    
    # Status Section
    with st.expander("📈 Status"):
        status = plan_details.get('status', 'N/A')
        st.write(f"**Status:** `{status}`")

# Function to display tasks and allow row selection
def display_tasks(tasks):
    if not tasks:
        st.warning("No tasks found.")
        return
    
    # Convert tasks to DataFrame
    df = pd.DataFrame(tasks)
    
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=True)  # Enable single row selection
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=50)  # Add pagination
    grid_options = gb.build()
    
    # Display the table
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,  # Update on selection change
        fit_columns_on_grid_load=True,
        theme="streamlit",  # Use the Streamlit theme
        height=400,
        width="100%",
    )
    
    # Handle row selection
    selected_rows = grid_response.get("selected_rows", pd.DataFrame())  # Default to an empty DataFrame if no rows are selected
        # Ensure selected_rows is always a DataFrame
    if selected_rows is None:
        selected_rows = pd.DataFrame()  # Default to an empty DataFrame if selected_rows is None
    
    st.write(selected_rows)
    
     # Check if any row is selected
    if not selected_rows.empty:  # Check if the DataFrame is not empty
        selected_task = selected_rows.iloc[0]  # Get the first selected row
        selected_task_id = selected_task["Id"]  # Replace "Id" with the actual column name for the task ID
        selected_task_name = selected_task["Name"]  # Replace "Id" with the actual column name for the task ID
        st.session_state.selected_task_id = selected_task_id
        st.session_state.selected_task_name = selected_task_name
    else:
        st.session_state.selected_task_id = None  # Clear selection if no row is selected


# Function to display plans and allow row selection
def display_plans(plans):
    if not plans:
        st.warning("No plans found.")
        return
    
    # Convert plans to DataFrame
    df = pd.DataFrame(plans)
    
    # Configure AgGrid options
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="single", use_checkbox=True)  # Enable single row selection
    gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=50)  # Add pagination
    grid_options = gb.build()
    
    # Display the table
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,  # Update on selection change
        fit_columns_on_grid_load=True,
        theme="streamlit",  # Use the Streamlit theme
        height=400,
        width="100%",
    )
    
    # Handle row selection
    selected_rows = grid_response.get("selected_rows")
    
    # Ensure selected_rows is always a DataFrame
    if selected_rows is None:
        selected_rows = pd.DataFrame()  # Default to an empty DataFrame if selected_rows is None
    
    # Check if any row is selected
    if not selected_rows.empty:  # Check if the DataFrame is not empty
        selected_plan = selected_rows.iloc[0]  # Get the first selected row
        selected_plan_id = selected_plan["Id"]  # Replace "Id" with the actual column name for the plan ID
        st.session_state.selected_plan_id = selected_plan_id
        st.write("Selected Plan ID:", st.session_state.selected_plan_id)
        st.success(f"Selected Plan ID: `{selected_plan_id}`")
    else:
        st.session_state.selected_plan_id = None  # Clear selection if no row is selected


# Function to display task operations
def display_task_operations(task_id: str, task_name: str):

    # Display task details
    task_details = st.session_state.client.get_task_details(task_id)
    if task_details:
        display_task_details(task_details)
    else:
        st.warning("Failed to fetch task details.")
    
    st.markdown('<div class="section-header">Task Operations</div>', unsafe_allow_html=True)
    
    # List of operations
    operation = st.selectbox(
        "Select an Operation",
        [
            "Execute Task",
            "Pause/Resume Task",
            "Update Task",
            "Delete Task",
            "View Executions",
            "Download Execution Logs"
        ]
    )
    
    # Handle selected operation
    if operation == "Execute Task":
            if st.button("Execute Task"):
                with st.spinner("Executing task..."):
                    execution_details = st.session_state.client.execute_task(task_id)
                    if execution_details:
                        st.success(f"Task execution started! Execution ID: `{execution_details['executionId']}`")
                    else:
                        st.error("Failed to execute task.")
            
            # Live Status and Execution Details
            st.markdown("### Execution Status")
            
            # Get the latest execution details
            executions = st.session_state.client.get_executions_for_task(task_id)
            if executions:
                latest_execution = executions[0]  # Most recent execution is the first in the list
                execution_id = latest_execution['executionId']
                
                # Poll for live status
                status_placeholder = st.empty()
                while True:
                    execution_details = st.session_state.client.get_task_execution_details(execution_id)
                    if execution_details:
                        status_placeholder.write(f"**Status:** `{execution_details['ExecutionStatus']}`")
                        status_placeholder.write(f"**Start Time:** `{execution_details['StartTime']}`")
                        status_placeholder.write(f"**Trigger Time:** `{execution_details['TriggerTime']}`")
                        
                        # Show terminate button if the task is running
                        if execution_details['ExecutionStatus'] == "RUNNING":
                            if st.button("Terminate Execution"):
                                with st.spinner("Terminating execution..."):
                                    success = st.session_state.client.terminate_execution(execution_id)
                                    if success:
                                        st.success("Execution terminated successfully!")
                                        break
                                    else:
                                        st.error("Failed to terminate execution.")
                        else:
                            break  # Exit the loop if the task is not running
                    
                    time.sleep(5)  # Poll every 5 seconds
            
            if executions:
                st.markdown("### Last 5 Executions")
                
                # Prepare data for the table
                execution_data = []
                for execution in executions[:5]:  # Limit to the last 5 executions
                    execution_details = st.session_state.client.get_task_execution_details(execution['executionId'])
                    if execution_details:
                        execution_data.append({
                            "Task Name": task_name,
                            "Start Time": execution_details.get('StartTime', 'N/A'),
                            "End Time": execution_details.get('finishTimestamp', 'N/A'),
                            "Execution Status": execution_details.get('ExecutionStatus', 'N/A'),
                            "Execution ID": execution['executionId']
                        })
                
                # Convert to DataFrame
                df = pd.DataFrame(execution_data)
                
                # Configure AgGrid options
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection(selection_mode="single", use_checkbox=True)  # Enable single row selection
                gb.configure_column("Execution ID", hide=True)  # Hide the Execution ID column
                grid_options = gb.build()
                
                # Display the table
                grid_response = AgGrid(
                    df,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,  # Update on selection change
                    fit_columns_on_grid_load=True,
                    theme="streamlit",  # Use the Streamlit theme
                    height=250,
                    width="100%",
                )
                
                # Handle row selection
                selected_rows = grid_response["selected_rows"]
                
                if selected_rows is None:
                    selected_rows = pd.DataFrame()  # Default to an empty DataFrame if selected_rows is None

                st.write(selected_rows)
                if not selected_rows.empty:
                    selected_execution = selected_rows.iloc[0]  # Get the first selected row
                    selected_execution_id = selected_execution["Execution ID"]

                    with st.spinner("Generating log file for download... Please wait"):     
                        token = st.session_state.client.get_execution_log_token(selected_execution_id)
                        if token:
                            presigned_url = st.session_state.client.get_presigned_url(selected_execution_id, token)
                            if presigned_url:
                                log_content = st.session_state.client.download_logs(presigned_url)
                                if log_content:
                                    log_text = log_content.decode("utf-8") if isinstance(log_content, bytes) else log_content
                                    
                                    # Create a meaningful file name
                                    file_name = f"{task_name}_{selected_execution_id}_logs.txt"
                                    
                                    # Wait briefly to ensure a smooth transition
                                    time.sleep(1)

                                    # Download the logs without an additional button click
                                    st.download_button(
                                        label="Download logs",
                                        data=log_text,
                                        file_name=file_name,
                                        mime="text/plain",
                                    )
                                else:
                                    st.error("Failed to fetch logs.")
                            else:
                                st.error("Failed to generate presigned URL.")
                        else:
                            st.error("Failed to generate download token.")
                else:
                    st.warning("Please select an execution to download logs.")
            else:
                st.warning("No executions found for this task.")

    elif operation == "Pause/Resume Task":
        pause = st.checkbox("Pause Task")
        pause_context = st.text_input("Pause/Resume Context", "User requested pause/resume")
        if st.button("Submit"):
            success = st.session_state.client.pause_or_resume_task(task_id, pause, pause_context)
            if success:
                st.success(f"Task {'paused' if pause else 'resumed'} successfully!")
            else:
                st.error("Failed to update task state.")
    
    elif operation == "Update Task":
        success, message = st.session_state.client.update_task_ui(task_id)
        if message:
            if success:
                st.success(message)
            else:
                st.error(message)
                
    elif operation == "Delete Task":
        terminate_executions = st.checkbox("Terminate Running Executions", value=True)
        if st.button("Delete Task"):
            success = st.session_state.client.delete_task(task_id, terminate_executions)
            if success:
                st.success("Task deleted successfully!")
            else:
                st.error("Failed to delete task.")
    
    elif operation == "View Executions":
        executions = st.session_state.client.get_executions_for_task(task_id)
        if executions:
            st.write("**Recent Executions:**")
            st.dataframe(pd.DataFrame(executions))
        else:
            st.warning("No executions found.")
    
    elif operation == "Download Execution Logs":
        execution_id = st.text_input("Enter Execution ID")
        if st.button("Download Logs"):
            if execution_id:
                token = st.session_state.client.get_execution_log_token(execution_id)
                if token:
                    presigned_url = st.session_state.client.get_presigned_url(execution_id, token)
                    if presigned_url:
                        output_file = f"execution_{execution_id}_logs.json"
                        success = st.session_state.client.download_logs(presigned_url, output_file)
                        if success:
                            st.success(f"Logs downloaded to `{output_file}`.")
                        else:
                            st.error("Failed to download logs.")
                    else:
                        st.error("Failed to generate presigned URL.")
                else:
                    st.error("Failed to generate download token.")
            else:
                st.error("Please enter an execution ID.")

# Function to display plan operations
def display_plan_operations(plan_id: str):
    
    # Display plan details
    plan_details = st.session_state.client.get_plan_details(plan_id)  # Assuming similar endpoint for plans
    if plan_details:
        display_plan_details(plan_details)
    else:
        st.warning("Failed to fetch plan details.")
    
    st.markdown('<div class="section-header">Plan Operations</div>', unsafe_allow_html=True)
    
    # List of operations
    operation = st.selectbox(
        "Select an Operation",
        [
            "Execute Plan",
            "View Plan Executions",
            "View Plan Steps"
        ]
    )
    
    # Handle selected operation
    if operation == "Execute Plan":
        if st.button("Execute"):
            execution_details = st.session_state.client.execute_plan(plan_id)
            if execution_details:
                st.success(f"Plan execution started! Execution ID: `{execution_details['executionId']}`")
            else:
                st.error("Failed to execute plan.")
    
    elif operation == "View Plan Executions":
        executions = st.session_state.client.get_executions_for_task(plan_id)  # Assuming similar endpoint for plans
        if executions:
            st.write("**Recent Executions:**")
            st.dataframe(pd.DataFrame(executions))
        else:
            st.warning("No executions found.")
    
    elif operation == "View Plan Steps":
        execution_id = st.text_input("Enter Plan Execution ID")
        if st.button("View Steps"):
            if execution_id:
                steps = st.session_state.client.get_plan_steps(execution_id)
                if steps:
                    st.write("**Plan Steps:**")
                    st.dataframe(pd.DataFrame(steps))
                else:
                    st.warning("No steps found.")
            else:
                st.error("Please enter a plan execution ID.")

def display_tasks_and_plans(task_name, workspace_id, environment_id):
    # Fetch tasks and plans
    tasks = st.session_state.client.search_tasks(task_name, workspace_id, environment_id)
    plans = st.session_state.client.search_plans(task_name, workspace_id, environment_id)
    
    # Create tabs for Tasks and Plans
    tab1, tab2 = st.tabs(["Tasks", "Plans"])
    
    # Display tasks in the first tab
    with tab1:
        if tasks:
            st.markdown('<div class="section-header">Tasks</div>', unsafe_allow_html=True)
            display_tasks(tasks)
            
            # Display task operations if a task is selected
            if st.session_state.selected_task_id:
                display_task_operations(st.session_state.selected_task_id, st.session_state.selected_task_name)
        else:
            st.warning("No tasks found.")
    
    # Display plans in the second tab
    with tab2:
        if plans:
            st.markdown('<div class="section-header">Plans</div>', unsafe_allow_html=True)
            display_plans(plans)
            
            # Display plan operations if a plan is selected
            if st.session_state.selected_plan_id:
                display_plan_operations(st.session_state.selected_plan_id)
        else:
            st.warning("No plans found.")