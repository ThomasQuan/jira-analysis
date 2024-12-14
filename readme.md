# Jira Data Extraction & Analysis
A small project I whip up during the last few days of 2024 before the year ends.
I always wonder to myself how many issues did I resolve during the year?
What was the most painful issues that I had dealt with?
What was our year like in terms of performance?
All these kind of questions jump into my head and I thought why not just create a tool that can help me answer those questions.

![Jira Analyst Showcase](assets/jira_analyst_showcase.pdf)

## Note
This project is design to answer questions specifically to my company. You are free to use it and modify it to your own needs.
There might be `custom_fields` that are not present or match to your company's Jira instance.
You can modify them in to suit your needs.
Example:
- `customfield_10000` is the custom field for `Sprint` in my company.
- `customfield_10001` is the custom field for `Development` in my company.
- `customfield_10048` is the custom field for `Severity` in my company.
- ...etc

## Setup

### Enter your Jira credentials
using the .env

### Create an virtual environment
```bash
python3 -m venv venv
```

### Activate the virtual environment
```bash
source venv/bin/activate
```

### Install the dependencies
```bash
pip install -e .
```

### Fetch Jira issues
```bash
python3 cli.py issues
```
#### Fetch Jira issues options
```bash
# Fetch issues updated of today
python3 cli.py issues --updated 'today'

# Fetch issues updated of yesterday
python3 cli.py issues --updated 'yesterday'

# Fetch issues updated of the week
python3 cli.py issues --updated 'week'

# Fetch issues updated of the month
python3 cli.py issues --updated 'month'

# Fetch issues updated of the year
python3 cli.py issues --updated 'year'

# Fetch issues updated of a timeframe
python3 cli.py issues --updated '2024-12-01' '2024-12-05'

# Fetch issues without cache
python3 cli.py issues --skip-cache
```

### Fetch Project Details
```bash
python3 cli.py project-details
```

### Fetch Workflow Columns
```bash
python3 cli.py workflow-columns
```

### Fetch EOD Report
```bash
python3 cli.py eod
```

### Convert Issues JSON Cached to CSV
```bash
python3 cli.py issues-to-csv
```

### Analyze the data
```bash
streamlit run app.py
```


