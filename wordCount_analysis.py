
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_loader import DataLoader
from model import Issue,Event
import config

class WordCountAnalysis:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--user)
        self.USER:str = config.get_parameter('user')
    
    def run(self):
        issues:List[Issue] = DataLoader().get_issues()
        
        ### WORD COUNT VS RESOLUTION TIME ANALYSIS

        print("\n\n")
        print("There is a lot of data here and the data contains some outliers that skew the chart.")
        print("So here is the option to hone in on specific parts of the data to make it more consice.")

        print("\n")
        print("Word Count Limit: Limits issues by word count, the data will not exceed the number you input.")

        print("\n")
        print("Resolve Day Limit: Limits issues by how many days they took to resolve, the data will not exceed the number you input.")
        print("\n")

        #Taking user input for limits
        while True:
            try:
                wordLimit = int(input("Enter a limit on the word count (Data goes up to 10000 words): "))
            except ValueError:
                print ("Please enter a valid number.")
                continue
            else: break

        while True:
            try:
                dayLimit = int(input("Enter a limit on the number of days  (Data goes up to 2000 days): "))
            except ValueError:
                print ("Please enter a valid number.")
                continue
            else: break


        
        analysis_data = []

        for issue in issues:
            # Only evaluate closed issues
            closed_events = [e for e in issue.events if e.event_type == "closed"]
            if not closed_events:
                continue  # skip unresolved issues

            # Word count of the text field
            word_count = len(issue.text.split()) if issue.text else 0

            # Not including any issues that are over the word limit
            if word_count > wordLimit:
                continue

            # Get created and closed timestamps
            created = pd.to_datetime(issue.created_date)
            closed = pd.to_datetime(closed_events[-1].event_date)  # use the last closed event if multiple

            resolve_time_days = (closed - created).days

            # Not including any issues that are over the day limit
            if resolve_time_days > dayLimit:
                continue

            analysis_data.append({
                "word_count": word_count,
                "resolve_time_days": resolve_time_days
            })

        # Convert to DataFrame
        df = pd.DataFrame(analysis_data)

        print("\n\n")
        print("Word Count vs Resolution Time")
        print(df.describe())

        ### SCATTER PLOT
        plt.figure(figsize=(12,6))
        plt.scatter(df["word_count"], df["resolve_time_days"], alpha=0.5)
        plt.title("Does a Longer Issue Description Lead to Faster Resolution?")
        plt.xlabel("Word Count in Issue Description")
        plt.ylabel("Resolution Time (Days)")
        plt.grid(True)

        ### Trend Line
        z = np.polyfit(df["word_count"], df["resolve_time_days"], 1)
        p = np.poly1d(z)
        plt.plot(df["word_count"], p(df["word_count"]), "r--")



        plt.show()

                        
    

if __name__ == '__main__':
    # Invoke run method when running this module directly
    WordCountAnalysis().run()