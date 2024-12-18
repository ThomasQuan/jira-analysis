#!/usr/bin/env python3

import argparse
import os
from dotenv import load_dotenv
from src.scraper.requester import JiraRequester
from halo import Halo
from src.scraper.printer import JiraPrinter
from src.analyzer.converter import convert_issue_to_csv


def main():
    parser = argparse.ArgumentParser(description="Fetch Jira project information")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: workflow-columns
    subparsers.add_parser("workflow-columns", help="Show workflow columns")

    # Command: project-details
    subparsers.add_parser("project-details", help="Show project details")

    # Command: issues
    issues_parser = subparsers.add_parser("issues", help="Fetch project issues")
    issues_parser.add_argument(
        "--assignee",
        type=str,
        nargs="+",
        help="Filter by assignee(s). Examples:\n" "john.doe jane.smith",
    )
    issues_parser.add_argument(
        "--created",
        type=str,
        nargs="+",
        help="Filter by created date. Examples:\n"
        "today, yesterday, week, month, year,\n"
        "2024-01-01 (specific date),\n"
        "2024-01-01 2024-01-31 (date range),\n"
        "all (all issues)",
    )
    issues_parser.add_argument("--silent", action="store_true", help="Silent mode")
    issues_parser.add_argument("--skip-cache", action="store_true", help="Skip cache")
    
    # Command: eod
    eod_parser = subparsers.add_parser(
        "eod",
        help="End of day report\n"
        "This command will fetch all issues that was updated yesterday\n"
        "provide a date to fetch issues updated on a specific date\n"
        "examples:\n"
        "eod 2024-01-01\n"
        "eod 2024-01-01 2024-01-31",
    )
    eod_parser.add_argument(
        "timeframe",
        nargs="*",
        help="Filter by date. Examples:\n"
        "yesterday (default),\n"
        "2024-01-01 (specific date),\n"
        "2024-01-01 2024-01-31 (date range)",
    )
    eod_parser.add_argument(
        "--assignee", type=str, nargs="+", help="Filter by assignee(s)"
    )

    # Command: convert issues to csv
    convert_parser = subparsers.add_parser(
        "issues-to-csv", help="Convert issues to csv"
    )
    convert_parser.add_argument("--year", type=str, help="Year to convert")

    args = parser.parse_args()

    # Load environment variables and validate
    load_dotenv()

    # Configuration from environment variables
    BASE_URL = os.getenv("BASE_URL")
    USERNAME = os.getenv("USERNAME")
    API_TOKEN = os.getenv("API_TOKEN")
    PROJECT_KEY = os.getenv("PROJECT_KEY")

    # Validate environment variables
    if not all([BASE_URL, USERNAME, API_TOKEN, PROJECT_KEY]):
        raise ValueError(
            "Please set all required environment variables:\n"
            "- BASE_URL\n"
            "- USERNAME\n"
            "- API_TOKEN\n"
            "- PROJECT_KEY"
        )

    # Initialize jiraRequester
    jiraRequester = JiraRequester(BASE_URL, USERNAME, API_TOKEN)

    # Initialize printer
    printer = JiraPrinter()

    # Handle different commands
    if args.command == "workflow-columns":
        with Halo(text="Fetching workflow columns...", spinner="dots") as spinner:
            board_config = jiraRequester.get_board_configuration(PROJECT_KEY)
            spinner.succeed("Workflow columns fetched successfully")
        printer.print_workflow_columns(board_config)

    elif args.command == "project-details":
        with Halo(text="Fetching project details...", spinner="dots") as spinner:
            project_details = jiraRequester.get_project_details(PROJECT_KEY)
            spinner.succeed("Project details fetched successfully")
        printer.print_project_details(project_details)

    elif args.command == "issues":
        timeframe = {}
        if args.created:
            timeframe["created"] = (
                args.created[0] if len(args.created) == 1 else args.created
            )

        if not timeframe:
            timeframe = {"created": "today"}  # Default behavior

        with Halo(text="Fetching issues...", spinner="dots") as spinner:
            issues, total_available = jiraRequester.get_project_issues(
                PROJECT_KEY, timeframe, args.assignee, skip_cache=args.skip_cache
            )
            spinner.succeed(f"Successfully fetched {len(issues)} issues")

        if not args.silent:
            custom_fields = jiraRequester.load_custom_field_mappings()
            printer.print_issues(
                issues,
                total_available,
                timeframe,
                custom_fields,
            )
    elif args.command == "eod":
        timeframe = args.timeframe if args.timeframe else ["yesterday"]
        timeframe = timeframe[0] if len(timeframe) == 1 else timeframe
        assignee = args.assignee if args.assignee else USERNAME
        with Halo(text="Fetching issues...", spinner="dots") as spinner:
            issues, total_available = jiraRequester.get_project_issues(
                PROJECT_KEY,
                {"updated": timeframe},
                [assignee],
                skip_cache=True
            )
            spinner.succeed(f"Successfully fetched {len(issues)} issues")

        printer.print_eod(issues)

    elif args.command == "issues-to-csv":
        custom_fields = jiraRequester.load_custom_field_mappings()
        convert_issue_to_csv(PROJECT_KEY, args.year, custom_fields)


if __name__ == "__main__":
    main()
