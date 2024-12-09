def format_development_field(value):
    """
    Format the weird development field value by forcing it to be a json object

    :param value: Raw development field value string
    :return: Formatted string with PR information
    """
    if not value:
        return "No development information"

    try:
        value_str = str(value).strip("{}")

        # Split into pullrequest data and JSON parts
        parts = value_str.split(", json=", 1)
        if len(parts) != 2:
            return str(value)

        pullrequest_str = parts[0]

        def str_to_dict(s):
            s = s.strip("{}")
            result = {}
            pairs = s.split(",")
            for pair in pairs:
                if "={" in pair:  # Handle nested structure
                    key, nested = pair.split("=", 1)
                    result[key.strip()] = str_to_dict(nested)
                else:  # Handle simple key-value
                    key, value = pair.split("=")
                    result[key.strip()] = (
                        int(value.strip()) if value.strip().isdigit() else value.strip()
                    )
            return result

        pr_data = str_to_dict(pullrequest_str)

        # Format the output
        if "pullrequest" in pr_data:
            return (
                f"Pull Requests: {pr_data.get('stateCount', 0)} "
                f"({pr_data.get('state', 'UNKNOWN')})"
            )

        return str(pr_data)

    except Exception as e:
        print(f"Error formatting development field: {e}")
        return str(value)


def format_sprint_field(value):
    """Format the sprint field value"""
    if not value:
        return "No sprint information"

    return f"{value[0].get('name')} ({value[0].get('state')})"


def format_resolution_field(value):
    if not value:
        return "No resolution information"

    # Collect all text from all content items
    text_items = []
    for paragraph in value.get("content", []):
        for content_item in paragraph.get("content", []):
            if content_item.get("type") == "text":
                text_items.append(content_item.get("text", ""))

    return "\n".join(text_items)


def format_project_output(
    project_details, board_config, issues, total_available, timeframe
):
    """Format and print all project information"""
    # Print project details
    print("Project Details:")
    print(f"Name: {project_details.get('name')}")
    print(f"Key: {project_details.get('key')}")
    print(f"Type: {project_details.get('projectTypeKey')}")
    print("\n")

    # Print board configuration
    print("Workflow Columns:")
    for column in board_config.get("columnConfig", {}).get("columns", []):
        print(f"- {column.get('name')}")
    print("\n")

    # Print issue details
    # ... (move existing issue printing logic here)

    # Print summary
    print("\n" + "=" * 50)
    print(f"Summary for timeframe: {timeframe}")
    print(f"Processed {len(issues)} out of {total_available} total available issues")
    print("=" * 50)
