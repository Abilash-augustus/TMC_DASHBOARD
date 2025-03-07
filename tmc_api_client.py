# tmc_api_client.py

import requests
from typing import Dict, List, Any, Optional, Union
import streamlit as st



class TMCAPIClient:
    """Client for interacting with Talend Management Console (TMC) API."""
    
    def __init__(self, auth_token: str, base_url: str = "https://api.us-west.cloud.talend.com/tmc/v2.6"):
        """
        Initialize the TMC API client.
        
        Args:
            auth_token: Authentication token for the API
            base_url: Base URL for the TMC API (default: "https://api.us-west.cloud.talend.com/tmc/v2.6")
        """
        self.auth_token = auth_token
        self.base_url = base_url
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the headers for API requests.
        
        Returns:
            Dictionary of headers
        """
        return {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
    
    # Workspace and Environment Operations
    def fetch_workspace_and_environment_mappings(self) -> Dict[str, Dict]:
        """
        Fetch workspaces and environments from TMC.
        
        Returns:
            Dictionary with workspace and environment mappings
        """
        mappings = {
            'workspaces': {},
            'environments': {}
        }
        
        response = requests.get(f"{self.base_url}/workspaces", headers=self.get_headers())
        response.raise_for_status()
        workspaces = response.json()

        for workspace in workspaces:
            workspace_id = workspace['id']
            workspace_name = workspace['name']
            environment_id = workspace['environment']['id']
            environment_name = workspace['environment']['name']
            
            # Store workspace ID based on workspace and environment combination
            mappings['workspaces'][(workspace_name, environment_name)] = workspace_id

            # Store environment ID by name, avoiding duplicates
            if environment_name not in mappings['environments']:
                mappings['environments'][environment_name] = environment_id

        return mappings
    
    # Artifact Operations
    def list_artifacts(self, workspace_id: str, environment_id: str, artifact_name: str) -> List[Dict[str, Any]]:
        """
        List artifacts based on name, workspace, and environment.
        
        Args:
            workspace_id: ID of the workspace
            environment_id: ID of the environment
            artifact_name: Name (partial) of the artifact
            
        Returns:
            List of artifact details
        """
        params = {
            'name': artifact_name,
            'workspaceId': workspace_id,
            'environmentId': environment_id
        }

        try:
            response = requests.get(f"{self.base_url}/artifacts", params=params, headers=self.get_headers())
            response.raise_for_status()
            artifacts = response.json()

            return artifacts.get('items', [])
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
        
    #Get connection details using connection id
    def get_connection_details(self, connection_id: str) -> Dict[str, Any]:
        """
        Fetch connection details by ID.
        
        Args:
            connection_id: ID of the connection
            
        Returns:
            Dictionary containing connection details (e.g., name, type, etc.)
        """
        try:
            response = requests.get(
                f"{self.base_url}/connections/{connection_id}", 
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch connection details: {e}")
            return {}
    
    # Task Operations
    def create_task(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task in TMC.
        
        Args:
            task_payload: Task configuration details
            
        Returns:
            Created task details
        """
        try:
            response = requests.post(
                f"{self.base_url}/executables/tasks", 
                json=task_payload, 
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Task creation failed: {e}")
            return {}
            
    def update_task(self, task_id: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            request_body: Updated task configuration
            
        Returns:
            Updated task details
        """
        response = requests.put(
            f"{self.base_url}/executables/tasks/{task_id}", 
            json=request_body,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_task_runtime(self, task_id: str, engine_id: str, engine_type: str) -> Dict[str, Any]:
        """
        Update a task's runtime configuration.
        
        Args:
            task_id: ID of the task
            engine_id: ID of the engine
            engine_type: Type of the engine (REMOTE_ENGINE_CLUSTER or REMOTE_ENGINE)
            
        Returns:
            Updated runtime configuration
        """
        url = f"{self.base_url}/executables/tasks/{task_id}/run-config"
        
        payload = {
            "runtime": {"id": engine_id, "type": engine_type},
            "trigger": {"type": "MANUAL"}
        }
        
        try:
            response = requests.put(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to update engine: {e}")
            return {}
    
    def delete_task(self, task_id: str, terminate_executions: bool = True) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: ID of the task to delete
            terminate_executions: Whether to terminate any running executions
            
        Returns:
            Success status (True/False)
        """
        try:
            url = f"{self.base_url}/executables/tasks/{task_id}"
            params = {'terminateExecutions': str(terminate_executions).lower()}

            response = requests.delete(url, params=params, headers=self.get_headers())
            
            if response.status_code == 204:
                return True
            else:
                print(f"Task deletion returned status: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Task deletion failed: {e}")
            return False
    
    def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """
        Get details of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task details
        """
        try:
            response = requests.get(f"{self.base_url}/executables/tasks/{task_id}", headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve task details: {e}")
            return {}
        
    
    def get_plan_details(self, plan_id: str) -> Dict[str, Any]:
        """
        Get details of a plan.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            plan details
        """
        try:
            response = requests.get(f"{self.base_url}/executables/plans/{plan_id}", headers=self.get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve plan details: {e}")
            return {}
    
    def get_task_update_info(self, task_id: str) -> Dict[str, Any]:
        """
        Get task information needed for updates.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task update information
        """
        task_details = self.get_task_details(task_id)
        if not task_details:
            return {}
            
        return {
            'artifact': {
                'id': task_details['artifact']['id'],
                'name': task_details['artifact']['name'],
                'version': task_details['artifact']['version']
            },
            'connections': task_details.get('connections', {}),
            'name': task_details['name'],
            'parameters': task_details.get('parameters', {}),
            'workspaceId': task_details['workspace']['id'],
            'environmentId': task_details['workspace']['environment']['id']
        }
    
    def pause_or_resume_task(self, task_id: str, pause: bool, pause_context: str) -> bool:
        """
        Pause or resume a task.
        
        Args:
            task_id: ID of the task
            pause: True to pause, False to resume
            pause_context: Reason for pausing/resuming
            
        Returns:
            Success status (True/False)
        """
        try:
            request_body = {
                "pause": pause,
                "pauseContext": pause_context
            }
            
            response = requests.put(
                f"{self.base_url}/executables/tasks/{task_id}/pause",
                json=request_body,
                headers=self.get_headers()
            )
            
            if response.status_code in [202, 204]:
                return True
            else:
                print(f"Task state change returned status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return False
    
    def search_tasks(self, task_name: str, workspace_id: str, environment_id: str) -> List[Dict[str, Any]]:
        """
        Search for tasks by name, workspace, and environment.
        
        Args:
            task_name: Name (partial) of the task
            workspace_id: ID of the workspace
            environment_id: ID of the environment
            
        Returns:
            List of matching tasks
        """
        params = {
            'name': task_name,
            'workspaceId': workspace_id,
            'environmentId': environment_id
        }

        try:
            response = requests.get(
                f"{self.base_url}/executables/tasks", 
                params=params, 
                headers=self.get_headers()
            )
            response.raise_for_status()
            executables = response.json()
            
            filtered_executables = [
                {
                    'number': index + 1,
                    'Id': executable['executable'],
                    'Name': executable['name']
                } for index, executable in enumerate(executables.get('items', []))
            ]
            
            return filtered_executables
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
    
    def search_plans(self, plan_name: str, workspace_id: str, environment_id: str) -> List[Dict[str, Any]]:
        """
        Search for plans by name, workspace, and environment.
        
        Args:
            plan_name: Name (partial) of the plan
            workspace_id: ID of the workspace
            environment_id: ID of the environment
            
        Returns:
            List of matching plans
        """
        params = {
            'name': plan_name,
            'workspaceId': workspace_id,
            'environmentId': environment_id
        }

        try:
            response = requests.get(
                f"{self.base_url}/executables/plans", 
                params=params, 
                headers=self.get_headers()
            )
            response.raise_for_status()
            executables = response.json()
            
            filtered_executables = [
                {
                    'number': index + 1,
                    'Id': executable['executable'],
                    'Name': executable['name']
                } for index, executable in enumerate(executables.get('items', []))
            ]
            
            return filtered_executables
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
    
    # Execution Operations
    def execute_task(self, task_id: str, log_level: str = "INFO") -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task_id: ID of the task to execute
            log_level: Logging level for the execution
            
        Returns:
            Execution details
        """
        response = requests.post(
            f"{self.base_url}/executions", 
            json={'executable': task_id, 'logLevel': log_level},
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a plan.
        
        Args:
            plan_id: ID of the plan to execute
            
        Returns:
            Execution details
        """
        response = requests.post(
            f"{self.base_url}/executions/plans", 
            json={'executable': plan_id},
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def terminate_execution(self, execution_id: str) -> bool:
        """
        Terminate an execution.
        
        Args:
            execution_id: ID of the execution to terminate
            
        Returns:
            Success status (True/False)
        """
        try:
            url = f"{self.base_url}/executions/{execution_id}"
            response = requests.delete(url, headers=self.get_headers())
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"Failed to terminate execution. Status code: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return False
    
    def get_task_execution_details(self, execution_id: str) -> Dict[str, Any]:
        """
        Get details of a task execution.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Execution details
        """
        response = requests.get(
            f"{self.base_url}/executions/{execution_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        execution_log = response.json()
        
        execution_map = {
            'executionId': execution_log['executionId'],
            'TriggerTime': execution_log['triggerTimestamp'],
            'StartTime': execution_log['startTimestamp'],
            'UserId': execution_log['userId'],
            'ExecutionStatus': execution_log['executionStatus'],
            'LogStatus': execution_log['status']
        }
        
        return execution_map
    
    def get_plan_execution_details(self, execution_id: str) -> Dict[str, Any]:
        """
        Get details of a plan execution.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Execution details
        """
        response = requests.get(
            f"{self.base_url}/executions/plans/{execution_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        execution_log = response.json()
        
        execution_map = {
            'executionId': execution_log['executionId'],
            'StartTime': execution_log['startTimestamp'],
            'UserId': execution_log['userId'],
            'PlannedExecutableCount': execution_log['plannedExecutableCount'],
            'PlanId': execution_log['planId'],
            'executionStatus': execution_log['executionStatus']
        }
        
        return execution_map
    
    def get_executions_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get recent executions for a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            List of execution details
        """
        response = requests.get(
            f"{self.base_url}/executables/tasks/{task_id}/executions", 
            headers=self.get_headers()
        )
        response.raise_for_status()
        executions_data = response.json()

        print(executions_data)
        
        executions = [
            {
                'number': index + 1,
                'executionId': item['executionId'],
                'startTimestamp': item['startTimestamp'],
                'triggerTimestamp': item['triggerTimestamp'],
                'finishTimestamp': item['finishTimestamp'],
                'taskId': item['taskId'],
                'status': item['status'],
                'executionStatus': item['executionStatus']
            }
            for index, item in enumerate(executions_data.get('items', [])[:10])
        ]
        print(executions)
        return executions
    
    def get_plan_steps(self, plan_execution_id: str) -> List[Dict[str, Any]]:
        """
        Get steps of a plan execution.
        
        Args:
            plan_execution_id: ID of the plan execution
            
        Returns:
            List of plan step details
        """
        response = requests.get(
            f"{self.base_url}/executions/plans/{plan_execution_id}/steps"
        )
        response.raise_for_status()
        return response.json()
    
    # Log Operations
    def get_execution_log_token(self, execution_id: str, file_format: str = "TEXT") -> str:
        """
        Get token for downloading execution logs.
        
        Args:
            execution_id: ID of the execution
            file_format: Format of the log file
            
        Returns:
            Download token
        """
        response = requests.post(
            f"{self.base_url}/executions/{execution_id}/logs?fileFormat={file_format}", 
            headers=self.get_headers()
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('token', '')
    
    def get_presigned_url(self, execution_id: str, token: str) -> str:
        """
        Get presigned URL for downloading logs.
        
        Args:
            execution_id: ID of the execution
            token: Download token
            
        Returns:
            Presigned URL
        """
        headers = self.get_headers()
        headers['Content-Type'] = '*/*'

        response = requests.post(
            f"{self.base_url}/executions/{execution_id}/logs/status", 
            data=token, 
            headers=self.get_headers()
        )
        response.raise_for_status()
        presigned_data = response.json()
        return presigned_data.get('presignedURL', '')
    
    def download_logs(self, presigned_url: str) -> Optional[bytes]:
        """
        Download logs using presigned URL and return the content as bytes.
        
        Args:
            presigned_url: Presigned URL for the logs
            
        Returns:
            Log content as bytes, or None if the download fails
        """
        try:
            response = requests.get(presigned_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Failed to download logs: {e}")
            return None
    # Other methods...


    def update_task_ui(self, task_id):
        """
        Generates a dynamic UI form for updating task information and handles the update logic.
        """
        task_update_info = self.get_task_update_info(task_id)
        if not task_update_info:
            return False, "Failed to fetch task update information."

        st.write("**Current Task Configuration:**")
        st.json(task_update_info)

        # Extract connections from the task
        connections = task_update_info.get('connections', {})
        if not connections:
            st.warning("No connections found in the task.")
            return False, "No connections found in the task."

        # Fetch details for the first connection to determine filter criteria
        first_connection_id = next(iter(connections.values()), None)
        if not first_connection_id:
            st.warning("No valid connection IDs found in the task.")
            return False, "No valid connection IDs found in the task."

        # Fetch connection details for the first connection
        first_connection_details = self.get_connection_details(first_connection_id)
        if not first_connection_details:
            st.warning(f"Failed to fetch details for connection ID: {first_connection_id}")
            return False, f"Failed to fetch details for connection ID: {first_connection_id}"

        # Extract filter criteria from the first connection
        current_app = first_connection_details.get('app', '')
        current_workspace_id = first_connection_details.get('workspace', {}).get('id', '')
        current_environment_id = first_connection_details.get('workspace', {}).get('environment', {}).get('id', '')

        # Fetch all connections
        try:
            all_connections = self.get_all_connections()
        except Exception as e:
            return False, f"Failed to fetch connections: {str(e)}"

        # Filter connections based on the criteria
        filtered_connections = [
            conn for conn in all_connections
            if conn.get('app') == current_app
            and conn.get('workspace', {}).get('id') == current_workspace_id
            and conn.get('workspace', {}).get('environment', {}).get('id') == current_environment_id
        ]

        # Create a form for updating task information
        with st.form("update_task_form"):
            st.write("**Update Task Information:**")

            # Section 1: Artifact (id and version)
            st.subheader("Artifact")
            artifact_id = st.text_input("Artifact ID", value=task_update_info.get('artifact', {}).get('id', ''))
            artifact_version = st.text_input("Artifact Version", value=task_update_info.get('artifact', {}).get('version', ''))

            # Section 2: Connections (dynamic key-value pairs)
            st.subheader("Connections")
            updated_connections = {}

            # Display a dropdown for each connection in the task
            for connection_name, connection_id in connections.items():
                # Fetch details for the current connection
                connection_details = self.get_connection_details(connection_id)
                current_connection_name = connection_details.get('name', 'Unknown Connection') if connection_details else "Unknown Connection"

                # Create a dropdown for selecting a new connection
                connection_options = {conn["id"]: conn["name"] for conn in filtered_connections}
                selected_connection_id = st.selectbox(
                    f"Connection: {connection_name} (Current: {current_connection_name})",
                    options=list(connection_options.keys()),
                    format_func=lambda x: connection_options[x],
                    index=list(connection_options.keys()).index(connection_id) if connection_id in connection_options else 0
                )
                updated_connections[connection_name] = selected_connection_id

            # Section 3: Name
            st.subheader("Name")
            name = st.text_input("Task Name", value=task_update_info.get('name', ''))

            # Section 4: Parameters (dynamic key-value pairs)
            st.subheader("Parameters")
            parameters = task_update_info.get('parameters', {})
            updated_parameters = {}
            for key, value in parameters.items():
                updated_value = st.text_input(f"Parameter: {key}", value=value)
                updated_parameters[key] = updated_value

            # Section 5: Workspace ID
            st.subheader("Workspace")
            workspace_id = st.text_input("Workspace ID", value=task_update_info.get('workspaceId', ''))

            # Submit button for the form
            submitted = st.form_submit_button("Update Task")
            if submitted:
                # Construct the updated task information
                updated_task_info = {
                    "artifact": {
                        "id": artifact_id,
                        "version": artifact_version
                    },
                    "connections": updated_connections,
                    "name": name,
                    "parameters": updated_parameters,
                    "workspaceId": workspace_id
                }

                # Call the update function
                updated_task = self.update_task(task_id, updated_task_info)
                if updated_task:
                    return True, "Task updated successfully!"
                else:
                    return False, "Failed to update task."

        return False, None  # No submission yet

    
    def get_all_connections(self):
        """
        Fetches all connections from the /connections endpoint using pagination.
        """
        connections = []
        limit = 100  # Maximum number of items per request
        offset = 0
        total = None

        while True:
            # Construct the request URL
            url = f"{self.base_url}/connections?limit={limit}&offset={offset}"
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch connections: {response.status_code} - {response.text}")

            data = response.json()
            connections.extend(data.get("items", []))

            # Update the total number of connections
            if total is None:
                total = data.get("total", 0)

            # Check if all connections have been fetched
            offset += limit
            if offset >= total:
                break

        return connections
