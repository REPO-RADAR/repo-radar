import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List
from collections import Counter, defaultdict

from repo_radar.models.github_repository import (
    Repository,
    Branch,
    Commit,
    Contributor,
    Issue,
    PullRequest,
    User,
    Label,
    Dependency,
)

class Plotter:
    
    def commits_per_day(self, commits: List[Commit]):
        """Line plot of commits per day for the last 30 days"""
        if not commits:
            return

        start_date = datetime.now() - timedelta(days=30)
        
        # Collect commit dates and authors for the last 30 days
        commit_data = [
            (c.date.date(), c.author.login) 
            for c in commits 
            if c.date.date() >= start_date.date()
        ]

        if not commit_data:
            return

        # Generate a list of all days in the 30-day period
        days = [start_date.date() + timedelta(days=i) for i in range(31)]

        # Use defaultdict to group commits by author
        author_commits = defaultdict(list)
        for date, author in commit_data:
            author_commits[author].append(date)

        plt.figure(figsize=(12, 6))
        
        # Calculate and plot commits for each individual author
        total_counts_per_day = Counter()
        for author, dates in author_commits.items():
            counts = Counter(dates)
            counts_list = [counts.get(day, 0) for day in days]
            plt.plot(days, counts_list, marker="o", label=author)
            total_counts_per_day.update(counts)

        # Calculate and plot the total commits line
        total_list = [total_counts_per_day.get(day, 0) for day in days]
        plt.plot(days, total_list, label="Total", linestyle="--", linewidth=2.5, color="black")

        plt.title("Commits per Day by Author (Last 30 Days)")
        plt.xlabel("Date")
        plt.ylabel("Commits")
        plt.xticks(rotation=45)
        plt.legend(title="Author")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def issues_bar_graph(self, issues: List[Issue]):
        """Bar graph: opened last 30 days, currently open, closed last 30 days."""
        start_date = datetime.now() - timedelta(days=30)
        
        opened_recent = 0
        currently_open = 0
        closed_recent = 0
        
        for issue in issues:
            if issue.created_at >= start_date:
                opened_recent += 1
            if issue.state == "open":
                currently_open += 1
            if issue.closed_at and issue.closed_at >= start_date:
                closed_recent += 1

        categories = ["Opened Last 30 Days", "Currently Open", "Closed Last 30 Days"]
        counts = [opened_recent, currently_open, closed_recent]

        plt.figure(figsize=(8, 5))
        plt.bar(categories, counts, color=["skyblue", "orange", "green"])
        plt.title("Issue Activity")
        plt.ylabel("Number of Issues")
        plt.tight_layout()
        plt.show()

    def pulls_bar_graph(self, pulls: List[PullRequest]):
        """Bar graph: opened last 30 days, currently open, closed, closed unmerged."""
        start_date = datetime.now() - timedelta(days=30)
        
        opened_recent = 0
        currently_open = 0
        closed_merged = 0
        closed_unmerged = 0
        
        for pull in pulls:
            if pull.created_at >= start_date:
                opened_recent += 1
            if pull.state =="open":
                currently_open += 1
            if pull.state == "closed" and pull.merged_at:
                closed_merged += 1
            if pull.state == "closed" and not pull.merged_at:
                closed_unmerged += 1

        categories = ["Opened Last 30 Days", "Currently Open", "Closed & Merged", "Closed Unmerged"]
        counts = [opened_recent, currently_open, closed_merged, closed_unmerged]

        plt.figure(figsize=(8, 5))
        plt.bar(categories, counts, color=["skyblue", "orange", "green", "red"])
        plt.title("Pull Request Activity")
        plt.ylabel("Number of Pull Requests")
        plt.tight_layout()
        plt.show()
        
    def issues_lifetime_graph(self, issues: List[Issue]):
        """
        Gantt chart: Each issue's lifetime from created to closed (or now if open).
        """
        fig, ax = plt.subplots(figsize=(10, len(issues) * 0.3))
    
        for i, issue in enumerate(issues):
            start = issue.created_at
            end = issue.closed_at or datetime.now()  # Use current time if still open
            ax.barh(
                y=i,
                width=(end - start).days,
                left=start,
                color="skyblue" if issue.state == "closed" else "orange",
                edgecolor="black"
            )
        
        ax.set_yticks(range(len(issues)))
        ax.set_yticklabels([f"{issue.title}" for issue in issues])
        ax.set_xlabel("Date")
        ax.set_title("Issue Lifetimes")
        plt.tight_layout()
        plt.show()
