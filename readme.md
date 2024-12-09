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
python3 setup.py install
```

### Get custom fields from Jira
```bash
python3 cli.py init-custom-fields
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
```


