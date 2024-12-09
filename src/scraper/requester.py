import requests
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import csv
from pathlib import Path
import time


class JiraRequester:
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize Jira Requester

        :param base_url: Base URL of your Jira instance (e.g., 'https://yourcompany.atlassian.net')
        :param username: Your Jira username (usually email)
        :param api_token: Jira API token
        """
        self.base_url = base_url
        self.auth = (username, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_project_details(self, project_key: str) -> Dict[str, Any]:
        """
        Fetch comprehensive details for a specific project

        :param project_key: Jira project key (e.g., 'PROJ')
        :return: Dictionary with project details
        """
        project_url = f"{self.base_url}/rest/api/3/project/{project_key}"
        response = requests.get(project_url, auth=self.auth, headers=self.headers)
        response.raise_for_status()

        # Save response to CSV with fields as columns
        data = response.json()
        output_dir = Path("raw_data")
        output_dir.mkdir(exist_ok=True)

        # Flatten the data and write to CSV
        with open(
            output_dir / f"{project_key}_project_details.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(data.keys())
            # Write values
            writer.writerow(str(value) for value in data.values())

        return data

    def get_date_range(self, timeframe: str | List[str]) -> tuple[str, str]:
        """
        Get JQL date range based on timeframe or date range string

        :param timeframe: Can be:
            - 'all' for all issues
            - Single date: '2024-01-01'
            - Date range as string: '2024-01-01 2024-01-31'
            - Date range as list: ['2024-01-01', '2024-01-31']
        :return: Tuple of (start_date, end_date) in JQL format
        """
        if timeframe == "all":
            return None, None
        elif timeframe == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            return today, tomorrow
        elif timeframe == "yesterday":
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            return yesterday, today
        elif timeframe == "week":
            start_of_week = (
                datetime.now() - timedelta(days=datetime.now().weekday())
            ).strftime("%Y-%m-%d")
            end_of_week = (
                datetime.now() + timedelta(days=5 - datetime.now().weekday())
            ).strftime("%Y-%m-%d")
            return start_of_week, end_of_week
        elif timeframe == "month":
            start_of_month = (
                datetime.now() - timedelta(days=datetime.now().day - 1)
            ).strftime("%Y-%m-%d")
            # Get first day of next month
            if datetime.now().month == 12:
                end_of_month = datetime(datetime.now().year + 1, 1, 1).strftime(
                    "%Y-%m-%d"
                )
            else:
                end_of_month = datetime(
                    datetime.now().year, datetime.now().month + 1, 1
                ).strftime("%Y-%m-%d")
            return start_of_month, end_of_month
        elif timeframe == "year":
            start_of_year = f"{datetime.now().year}-01-01"
            end_of_year = f"{datetime.now().year + 1}-01-01"
            return start_of_year, end_of_year

        # Handle list input
        if isinstance(timeframe, list):
            if len(timeframe) != 2:
                raise ValueError(
                    "Date range list must contain exactly 2 dates:\n"
                    "Example: ['2024-01-01', '2024-01-31']"
                )
            try:
                start_date = datetime.strptime(timeframe[0], "%Y-%m-%d")
                end_date = datetime.strptime(timeframe[1], "%Y-%m-%d") + timedelta(
                    days=1
                )
                return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Invalid date format in list. Use YYYY-MM-DD format:\n"
                    "Example: ['2024-01-01', '2024-01-31']"
                )

        # Check if it's a date range (two dates separated by space)
        if " " in timeframe:
            try:
                start_str, end_str = timeframe.split()
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_str, "%Y-%m-%d") + timedelta(days=1)
                return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    "Invalid date range format. Use YYYY-MM-DD format:\n"
                    "Example: '2024-01-01 2024-01-31'"
                )

        # Check if it's a single date
        try:
            date = datetime.strptime(timeframe, "%Y-%m-%d")
            next_date = date + timedelta(days=1)
            return date.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Invalid timeframe. Use either:\n"
                "- 'all' for all issues\n"
                "- Single date: '2024-01-01'\n"
                "- Date range: '2024-01-01 2024-01-31'"
            )

    def get_project_issues(
        self,
        project_key: str,
        timeframe: Dict[str, Any] = None,
        assignees: List[str] = None,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Fetch all issues for a project with detailed information, using cache when available
        """
        output_dir = Path("raw_data") / f"{project_key}_issues"
        cached_issues = {}
        dates_to_fetch = set()

        # Determine which dates need to be fetched
        for field, value in timeframe.items():
            start_date, end_date = self.get_date_range(value)
            if start_date and end_date:
                current_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                while current_date < end_datetime:
                    dates_to_fetch.add(current_date.strftime("%Y-%m-%d"))
                    current_date += timedelta(days=1)

        # Add timer for JSON loading
        start_time = time.time()

        # Load only the relevant cached issues from year/month structure
        if output_dir.exists():
            dates_found = set()  # Track which dates we've found in cache
            for date_str in dates_to_fetch:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                year_dir = output_dir / str(date.year)
                month_name = {
                    1: "january",
                    2: "february",
                    3: "march",
                    4: "april",
                    5: "may",
                    6: "june",
                    7: "july",
                    8: "august",
                    9: "september",
                    10: "october",
                    11: "november",
                    12: "december",
                }[date.month]

                json_path = year_dir / month_name / "issues.json"
                if json_path.exists():
                    with open(json_path, "r", encoding="utf-8") as f:
                        month_data = json.load(f)
                        if date_str in month_data:
                            cached_issues[date_str] = month_data[date_str]
                            dates_found.add(date_str)

            # Remove found dates from dates_to_fetch after iteration is complete
            dates_to_fetch -= dates_found

        json_load_time = time.time() - start_time
        print(f"Loading JSON cache took: {json_load_time:.2f} seconds")

        issues_url = f"{self.base_url}/rest/api/3/search"
        all_issues = []

        # If all dates are cached, return cached data
        if not dates_to_fetch:
            print("All requested dates found in cache")
            all_issues = []
            # Only include issues from the requested timeframe
            for field, value in timeframe.items():
                start_date, end_date = self.get_date_range(value)
                if start_date and end_date:
                    current_date = datetime.strptime(start_date, "%Y-%m-%d")
                    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

                    while current_date < end_datetime:
                        date_str = current_date.strftime("%Y-%m-%d")
                        if date_str in cached_issues:
                            all_issues.extend(cached_issues[date_str])
                        current_date += timedelta(days=1)
            return all_issues, len(all_issues)

        # Build JQL query for missing dates
        jql = f"project = {project_key}"

        for field, value in timeframe.items():
            start_date, end_date = self.get_date_range(value)
            if start_date:
                if start_date == end_date:
                    next_day = (
                        datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)
                    ).strftime("%Y-%m-%d")
                    jql += f" AND {field} >= '{start_date}' AND {field} < '{next_day}'"
                else:
                    jql += f" AND {field} >= '{start_date}' AND {field} < '{end_date}'"

        if assignees:
            quoted_assignees = [f'"{assignee}"' for assignee in assignees]
            assignee_list = ", ".join(quoted_assignees)
            jql += f" AND assignee IN ({assignee_list})"

        jql += " ORDER BY updated DESC"

        # Fetch new issues
        batch_size = 100
        start_at = 0
        new_issues_by_date = {}

        try:
            while True:
                payload = {
                    "jql": jql,
                    "maxResults": batch_size,
                    "startAt": start_at,
                    "fields": ["*all"],
                    "expand": ["changelog"],
                }

                print(f"Fetching new issues starting at: {start_at}")
                response = requests.post(
                    issues_url, json=payload, auth=self.auth, headers=self.headers
                )

                if not response.ok:
                    print(f"Error response: {response.text}")
                    response.raise_for_status()

                result = response.json()
                batch_issues = result.get("issues", [])

                if not batch_issues:
                    break

                # Organize new issues by date using updated field
                for issue in batch_issues:
                    updated_str = issue.get("fields", {}).get("updated", "")
                    if updated_str:
                        date = updated_str.split("T")[0]
                        if date not in new_issues_by_date:
                            new_issues_by_date[date] = []
                        new_issues_by_date[date].append(issue)

                start_at += len(batch_issues)
                if len(batch_issues) < batch_size:
                    break

            # Update the cache saving logic
            if new_issues_by_date:
                # Group new issues by year and month
                issues_by_year_month = {}
                for date_str, issues in new_issues_by_date.items():
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    year = str(date.year)
                    month = date.month

                    if year not in issues_by_year_month:
                        issues_by_year_month[year] = {}
                    if month not in issues_by_year_month[year]:
                        issues_by_year_month[year][month] = {}

                    issues_by_year_month[year][month][date_str] = issues

                # Month mapping for folder names
                month_names = {
                    1: "january",
                    2: "february",
                    3: "march",
                    4: "april",
                    5: "may",
                    6: "june",
                    7: "july",
                    8: "august",
                    9: "september",
                    10: "october",
                    11: "november",
                    12: "december",
                }

                # Save issues in year/month structure
                for year, year_data in issues_by_year_month.items():
                    for month_num, month_data in year_data.items():
                        month_name = month_names[month_num]
                        month_dir = output_dir / year / month_name
                        month_dir.mkdir(parents=True, exist_ok=True)

                        # Merge with existing month data if it exists
                        json_path = month_dir / "issues.json"
                        existing_month_data = {}
                        if json_path.exists():
                            with open(json_path, "r", encoding="utf-8") as f:
                                existing_month_data = json.load(f)

                        # Update with new data
                        existing_month_data.update(month_data)

                        # Save updated month data
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(existing_month_data, f, indent=2)

        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise

        return all_issues, len(all_issues)

    def get_board_configuration(self, project_key: str) -> Dict[str, Any]:
        """
        Fetch board configuration for a project to get workflow columns

        :param project_key: Jira project key
        :return: Board configuration details
        """
        # Note: This might require knowing the board ID beforehand
        boards_url = f"{self.base_url}/rest/agile/1.0/board"

        response = requests.get(
            f"{boards_url}?projectKeyOrId={project_key}",
            auth=self.auth,
            headers=self.headers,
        )
        response.raise_for_status()

        boards = response.json().get("values", [])
        if boards:
            board_id = boards[0]["id"]
            config_url = (
                f"{self.base_url}/rest/agile/1.0/board/{board_id}/configuration"
            )
            config_response = requests.get(
                config_url, auth=self.auth, headers=self.headers
            )
            result = config_response.json()

            # Save board config to CSV with fields as columns
            output_dir = Path("raw_data")
            output_dir.mkdir(exist_ok=True)
            with open(
                output_dir / f"{project_key}_board_config.csv",
                "w",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                writer.writerow(["raw_response"])
                writer.writerow([json.dumps(result)])

            return result
        return {}

    def load_custom_field_mappings(self):
        """Load custom field mappings from JSON file"""
        try:
            with open("config/jira_custom_fields.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Custom field mappings file not found")
            return {}

    def check_issues_keys(self, project_key: str):
        """Check the key column for each project in the raw_data folder which contains issues in json format"""
        output_dir = Path("raw_data")
        for file in output_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print("\nKeys in file", file.name, ":")
                # Sort keys in descending order (assuming keys are dates in YYYY-MM-DD format)
                sorted_keys = sorted(data.keys(), reverse=True)
                for key in sorted_keys:
                    print(f"- {key}")
