import json
import csv
import os
from src.scraper.formatters import (
    format_sprint_field,
    format_development_field,
    format_resolution_field,
)


def convert_issue_to_csv(project_key, year, custom_fields):
    """
    Convert an issue of a year to a csv with the following columns:
    - Issue Key
    - Issue Type
    - Issue Summary
    - Status
    - Created
    - Updated
    - Priority
    - Reporter
    - Assignee
    - Sprint
    - Fix Version
    - Parent Ticket
    - Severity
    - Escalation Level
    - Epic Link
    - HubSpot ticket count
    - Development
    - Comments History in an array of objects
    - Status Change History in an array of objects
    """
    # Create output directory if it doesn't exist
    output_dir = "csv_data"
    os.makedirs(output_dir, exist_ok=True)

    # Prepare CSV file path
    csv_file = os.path.join(output_dir, f"issues_{year}.csv")

    # Read JSON data from all month folders
    issues_dates = {}
    year_dir = f"raw_data/{project_key}_issues/{year}"

    # Loop through all month folders
    for month in os.listdir(year_dir):
        month_path = os.path.join(year_dir, month)
        if os.path.isdir(month_path):
            json_file = os.path.join(month_path, "issues.json")
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    month_issues = json.load(f)
                    issues_dates.update(month_issues)

    # Define CSV headers based on required fields and custom fields
    default_headers = [
        "Issue Key",
        "Issue Type",
        "Issue Summary",
        "Status",
        "Created",
        "Updated",
        "Priority",
        "Reporter",
        "Assignee",
        "Fix Version",
        "Parent Ticket",
        "Comments History",
        "Status Change History",
    ]

    # Add custom field names to headers
    headers = default_headers + [
        custom_fields[field]["name"]
        for field in custom_fields
        if "name" in custom_fields[field]
    ]

    # Write to CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for _, issues in issues_dates.items():
            for issue in issues:
                fields = issue["fields"]
                # Prepare row data
                row = {
                    "Issue Key": issue.get("key"),
                    "Issue Type": fields.get("issuetype", {}).get("name"),
                    "Issue Summary": fields.get("summary"),
                    "Status": fields.get("status", {}).get("name"),
                    "Created": fields.get("created"),
                    "Updated": fields.get("updated"),
                    "Priority": fields.get("priority", {}).get("name")
                    if fields.get("priority")
                    else "",
                    "Reporter": fields.get("reporter", {}).get("displayName")
                    if (fields.get("reporter"))
                    else "",
                    "Assignee": fields.get("assignee", {}).get("displayName")
                    if fields.get("assignee")
                    else "",
                    "Fix Version": ", ".join(
                        v.get("name", "") for v in fields.get("fixVersions", [])
                    ),
                    "Parent Ticket": get_parent_ticket(fields),
                    "Comments History": json.dumps(_extract_comments(fields)),
                    "Status Change History": json.dumps(_extract_status_history(issue)),
                }

                # Add custom fields to the row
                custom_field_values = get_custom_fields(fields, custom_fields)
                row.update(custom_field_values)
                writer.writerow(row)

    return csv_file


def get_parent_ticket(fields):
    parts = [
        fields.get("parent", {}).get("key"),
        fields.get("parent", {}).get("fields", {}).get("summary")
    ]
    return " - ".join(filter(None, parts))


def get_custom_fields(fields, custom_fields):
    custom_field_values = {}
    for field_key, field_value in fields.items():
        if field_key.startswith("customfield_") and field_key in custom_fields:
            if field_value is not None and field_value != []:
                field_info = custom_fields[field_key]
                field_name = field_info.get("name", field_key)
                field_type = field_info.get("type", "unknown")

                formatted_value = format_custom_field(
                    field_value, field_name, field_type
                )
                custom_field_values[field_name] = formatted_value
    return custom_field_values


def format_custom_field(field_value, field_name, field_type):
    if field_name == "Sprint":
        return format_sprint_field(field_value)
    elif field_name == "Development":
        return format_development_field(field_value)
    elif field_name == "Ticket Resolution Details":
        return format_resolution_field(field_value)
    elif field_type == "array" and isinstance(field_value, list):
        return ", ".join(str(v) for v in field_value)
    elif field_type == "user" and isinstance(field_value, dict):
        return field_value.get("displayName", str(field_value))
    elif field_type == "option" and isinstance(field_value, dict):
        return field_value.get("value", str(field_value))
    return field_value


def _extract_comments(fields):
    """Extract comments history"""
    comments = fields.get("comment", {}).get("comments", [])
    return [
        {
            "author": comment.get("author", {}).get("displayName"),
            "created": comment.get("created"),
            "body": comment.get("body"),
        }
        for comment in comments
    ]


def _extract_status_history(issue):
    """Extract status change history"""
    changelog = issue.get("changelog", {}).get("histories", [])
    status_changes = []

    for history in changelog:
        for item in history.get("items", []):
            if item.get("field") == "status":
                status_changes.append(
                    {
                        "date": history.get("created"),
                        "author": history.get("author", {}).get("displayName"),
                        "from": item.get("fromString"),
                        "to": item.get("toString"),
                    }
                )
    return status_changes
