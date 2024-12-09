import requests
import json
import os
from typing import Dict, Any


def init_custom_fields(base_url: str, username: str, api_token: str) -> Dict[str, Any]:
    """
    Get all custom fields configured in Jira and store them in config/jira_custom_fields.json
    """
    url = f"{base_url}/rest/api/3/field"
    auth = (username, api_token)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()

    # Filter for custom fields only and format the output
    custom_fields = {}
    for field in response.json():
        if field.get("custom", False):
            custom_fields[field["id"]] = {
                "name": field.get("name"),
                "description": field.get("description"),
                "type": field.get("schema", {}).get("type"),
            }

    # Create config directory if it doesn't exist
    os.makedirs("config", exist_ok=True)

    # Write custom fields to JSON file
    with open("config/jira_custom_fields.json", "w") as f:
        json.dump(custom_fields, f, indent=2)

    return custom_fields
