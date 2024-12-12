# Jira Data Extraction & Analysis
A minisize projects I created to extract data from Jira and basically analyze it to generate a yearly report.



## Development setup

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


