from setuptools import setup, find_packages

setup(
    name="jira-scraper",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "requests",
        "halo",
        "rich",
        "streamlit",
        "pandas",
        "plotly",
        "calplot",
        "numpy",
    ]
)
