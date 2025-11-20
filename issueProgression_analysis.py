from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue
import config

class IssueProgressionAnalysis:
    """
    Analyzes the opening dates of GitHub issues and determines how many
    issues were opened per month, aggregated across all years.
    """

    def __init__(self):
        self.USER: str = config.get_parameter("user")

    def run(self):
        # Load issues
        issues: List[Issue] = DataLoader().get_issues()

        # Extract "created_date" timestamps and convert them to pandas datetime
        df = pd.DataFrame.from_records([
            {"created_date": issue.created_date}
            for issue in issues
            if issue.created_date is not None
        ])
        df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")

        # Drop any invalid dates
        df = df.dropna(subset=["created_date"])

        # Extract month names or month numbers (your choice)
        df["month"] = df["created_date"].dt.month_name()

        # Count number of issues per month
        issues_per_month = df.groupby("month").size()

        # Reorder months properly (Jan to Dec)
        months_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        issues_per_month = issues_per_month.reindex(months_order, fill_value=0)

        # Print summary
        print("\n\nIssue counts by month:\n")
        print(issues_per_month)
        print("\n")

        # Plot
        plt.figure(figsize=(12, 6))
        issues_per_month.plot(kind="bar", title="Issues Opened per Month")
        plt.xlabel("Month")
        plt.ylabel("# of Issues Opened")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    IssueProgressionAnalysis().run()
