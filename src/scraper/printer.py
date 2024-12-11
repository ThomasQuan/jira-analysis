from rich import print as rprint
from rich.text import Text
from .formatters import (
    format_sprint_field,
    format_development_field,
    format_resolution_field,
)


class JiraPrinter:
    # Public methods (used by cli.py)
    def print_workflow_columns(self, board_config):
        print("\nWorkflow Columns:")
        for column in board_config.get("columnConfig", {}).get("columns", []):
            print(f"- {column.get('name')}")

    def print_project_details(self, project_details):
        print("\nProject Details:")
        print(f"Name: {project_details.get('name')}")
        print(f"Key: {project_details.get('key')}")
        print(f"Type: {project_details.get('projectTypeKey')}")

    def print_custom_fields_init(self, custom_fields):
        print("\nCustom Fields Added:")
        for field_key, field_value in custom_fields.items():
            print(f"  {field_key}: {field_value}")

    def print_issues(self, issues, total_available, timeframe, custom_fields):
        for issue in issues:
            self._print_single_issue(issue, custom_fields)

        # Print summary
        summary_text = Text()
        summary_text.append("\n" + "=" * 50 + "\n", style="bold green")
        summary_text.append(f"Summary for timeframe: {timeframe}\n", style="bold white")
        summary_text.append(
            f"Processed {len(issues)} out of {total_available} total available issues\n",
            style="bold white",
        )
        summary_text.append("=" * 50, style="bold green")
        rprint(summary_text)

    def print_eod(self, issues):
        for issue in issues:
            fields = issue["fields"]

            # Get status changes count
            changelog = issue.get("changelog", {}).get("histories", [])
            todo_count = sum(
                1
                for history in changelog
                for item in history.get("items", [])
                if item.get("field") == "status" and item.get("toString") == "To Do"
            )

            # Get current status
            current_status = fields.get("status", {}).get("name", "Unknown")

            # Get latest comment
            comments = fields.get("comment", {}).get("comments", [])
            latest_comment = "No comments"
            if comments:
                latest = comments[-1]
                author = latest.get("author", {}).get("displayName")
                comment_body = self._format_comment_body(latest.get("body"))
                latest_comment = (
                    f"{author}: {comment_body[:100]}..."  # Truncate long comments
                )

            # Get custom fields
            

            # Get fix versions
            fix_versions = [v.get("name", "") for v in fields.get("fixVersions", [])]

            # Print concise report
            print("\n" + "=" * 80)
            print(f"Issue: {issue.get('key')} - {fields.get('summary')}")
            print(f"Current Status: {current_status}")
            print(f"Times in To Do: {todo_count}")
            print(
                f"Fix Versions: {', '.join(fix_versions) if fix_versions else 'None'}"
            )
            print(f"Latest Comment: {latest_comment}")
            print("=" * 80)

    # Private helper methods
    def _print_single_issue(self, issue, custom_fields):
        fields = issue["fields"]
        # Basic info
        print(f"\nIssue Key: {issue.get('key')}")
        print(f"Summary: {fields.get('summary')}")
        print(f"Status: {fields.get('status', {}).get('name', 'Unknown')}")
        print(f"Created: {fields.get('created')}")
        print(f"Updated: {fields.get('updated')}")

        # Priority, Reporter, Assignee
        priority = fields.get("priority")
        priority_name = priority.get("name") if priority else "No Priority"
        print(f"Priority: {priority_name}")

        reporter = fields.get("reporter", {})
        assignee = fields.get("assignee", {})
        reporter_name = reporter.get("displayName") if reporter else "Unassigned"
        assignee_name = assignee.get("displayName") if assignee else "Unassigned"
        print(f"Reporter: {reporter_name}")
        print(f"Assignee: {assignee_name}")

        # Fix Versions
        fix_versions = [v.get("name", "") for v in fields.get("fixVersions", [])]
        print(f"Fix Versions: {', '.join(fix_versions) if fix_versions else 'None'}")

        # Parent Ticket
        parent = fields.get("parent", {})
        parent_key = parent.get("key") if parent else None
        if parent_key:
            print(f"Parent Ticket: {parent_key}")

        self._print_custom_fields(fields, custom_fields)
        self._print_linked_issues(fields)
        self._print_comments(fields)

        # Add changelog printing
        self._print_status_history(issue)

        print("---")

    def _print_status_history(self, issue):
        changelog = issue.get("changelog", {}).get("histories", [])
        if changelog:
            print("\nStatus Changes:")
            for history in changelog:
                for item in history.get("items", []):
                    if item.get("field") == "status":
                        print(
                            f"  {history.get('created')} - "
                            f"{history.get('author', {}).get('displayName')}: "
                            f"{item.get('fromString')} → {item.get('toString')}"
                        )

    def _print_custom_fields(self, fields, custom_fields):
        for field_key, field_value in fields.items():
            if (
                field_key.startswith("customfield_")
                and field_key in custom_fields
            ):
                if field_value is not None and field_value != []:
                    field_info = custom_fields[field_key]
                    field_name = field_info.get("name", field_key)
                    field_type = field_info.get("type", "unknown")

                    formatted_value = self._format_custom_field(
                        field_value, field_name, field_type
                    )
                    print(f"{field_name}: {formatted_value}")

    def _format_custom_field(self, field_value, field_name, field_type):
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

    def _print_linked_issues(self, fields):
        linked_issues = fields.get("issuelinks", [])
        if linked_issues:
            print("Linked Issues:")
            for link in linked_issues:
                link_type = link.get("type", {}).get("name", "Unknown")
                outward_issue = link.get("outwardIssue", {}).get("key")
                inward_issue = link.get("inwardIssue", {}).get("key")
                if outward_issue:
                    print(f"  - {link_type}: {outward_issue}")
                if inward_issue:
                    print(f"  - {link_type}: {inward_issue}")

    def _print_comments(self, fields):
        comments = fields.get("comment", {}).get("comments", [])
        if comments:
            print("\nComments:")
            for comment in comments:
                author = comment.get("author", {}).get("displayName")
                created = comment.get("created")
                body = self._format_comment_body(comment.get("body"))
                print(f"  {created} - {author}:")
                print(f"  {body}\n")

    def _format_comment_body(self, body):
        if isinstance(body, dict):
            text = ""
            for content in body.get("content", []):
                if content.get("type") == "paragraph":
                    for text_node in content.get("content", []):
                        if text_node.get("type") == "text":
                            text += text_node.get("text", "")
            return text
        return body
