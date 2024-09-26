import requests
from requests.auth import HTTPBasicAuth
import json
from loguru import logger


class ServiceNowIntegration:
    def __init__(self, instance_url, username, password):
        self.instance_url = instance_url
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}

    def create_incident(self, short_description, description, priority=3):
        """
        Create a new incident in ServiceNow.

        :param short_description: A brief description of the incident
        :param description: A detailed description of the incident
        :param priority: Priority of the incident (1-5, where 1 is highest)
        :return: The created incident's sys_id if successful, None otherwise
        """
        endpoint = f"{self.instance_url}/api/now/table/incident"

        data = {
            "short_description": short_description,
            "description": description,
            "priority": priority
        }

        try:
            response = requests.post(
                endpoint,
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()['result']['sys_id']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating incident: {str(e)}")
            return None

    def get_incident(self, sys_id):
        """
        Retrieve an incident from ServiceNow by its sys_id.

        :param sys_id: The sys_id of the incident to retrieve
        :return: The incident details if found, None otherwise
        """
        endpoint = f"{self.instance_url}/api/now/table/incident/{sys_id}"

        try:
            response = requests.get(
                endpoint,
                auth=self.auth,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()['result']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving incident: {str(e)}")
            return None

    def update_incident(self, sys_id, update_data):
        """
        Update an existing incident in ServiceNow.

        :param sys_id: The sys_id of the incident to update
        :param update_data: A dictionary containing the fields to update
        :return: True if update was successful, False otherwise
        """
        endpoint = f"{self.instance_url}/api/now/table/incident/{sys_id}"

        try:
            response = requests.patch(
                endpoint,
                auth=self.auth,
                headers=self.headers,
                data=json.dumps(update_data)
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating incident: {str(e)}")
            return False

    def _get_user_friendly_error(self, error):
        """Convert technical error messages to user-friendly messages."""
        if isinstance(error, requests.exceptions.ConnectionError):
            return "Unable to connect to ServiceNow. Please check your internet connection and try again."
        elif isinstance(error, requests.exceptions.Timeout):
            return "The request to ServiceNow timed out. Please try again later."
        elif isinstance(error, requests.exceptions.HTTPError):
            if error.response.status_code == 401:
                return "Authentication failed. Please check your ServiceNow credentials."
            elif error.response.status_code == 403:
                return "You don't have permission to perform this action in ServiceNow."
            elif error.response.status_code == 404:
                return "The requested resource was not found in ServiceNow."
            else:
                return f"An HTTP error occurred: {error}"
        else:
            return f"An unexpected error occurred: {str(error)}"