from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass
from repo_radar.models.github_url import GitHubUrl
from datetime import datetime

@dataclass
class Repository:
    url: GitHubUrl = None
    default_branch_commits: List[Commit] = None
    branches: List[Branch] = None
    issues: List[Issue] = None
    pulls: List[PullRequest] = None
    contributors: List[Contributor] = None
    license: Optional[dict] = None
    languages: Optional[dict] = None
    dependencies: List[Dependency] = None

    def commit_count(self) -> int:
        total = 0
        
        for branch in self.branches:
            total += len(branch.commits or [])
        total += len(self.default_branch_commits or [])
        
        return total

    def issue_stats(self) -> dict:
        open_issues = 0
        closed_issues = 0
        
        for issue in self.issues:
            if issue.state == "closed":
                closed_issues += 1
            elif issue.state == "open":
                open_issues += 1

        return {"open": open_issues, "closed": closed_issues}

    def pull_stats(self) -> dict:
        open_pulls = 0
        merged_pulls = 0
        closed_unmerged = 0
        
        for pull in self.pulls:
            if pull.merged_at:
                merged_pulls += 1
            elif pull.state == "open":
                open_pulls += 1
            elif pull.state == "closed" and not pull.merged_at:
                closed_unmerged += 1
                
        return {"open": open_pulls, "merged": merged_pulls, "closed_unmerged": closed_unmerged}

    def contributor_count(self) -> int:
        return len(self.contributors or [])

    def __repr__(self) -> str:
        branches_str = "\n      ".join(repr(b) for b in (self.branches or [])) or "None"
        contributors_str = "\n      ".join(repr(c) for c in (self.contributors or [])) or "None"
    
        return (
            f"Repository: {self.url.full_url}\n"
            f"    Commits: {self.commit_count()}\n"
            f"    Issues: {self.issue_stats()}\n"
            f"    Pulls: {self.pull_stats()}\n"
            f"    Languages: {list((self.languages or {}).keys())}\n"
            f"    License: {self.license.get('spdx_id') if self.license else 'None'}\n"
            f"    Branches:\n      {branches_str}\n"
            f"    Contributors:\n      {contributors_str}\n"
            f"    Dependencies: {list(self.dependencies)}\n"
        )

@dataclass
class Branch:
    name: str
    sha: str
    commits: List[Commit] = None
    
    def __repr__(self) -> str:
        commit_count = len(self.commits or [])
        return f"Branch '{self.name}' @ {self.sha} ({commit_count} commits)"
    
@dataclass
class Commit:
    sha: str
    author: User
    date: datetime
    message: str

    def __repr__(self) -> str:
        return f"{self.sha} by {self.author.login} on {self.date.date()}: {self.message.splitlines()[0]}"
    
@dataclass
class Contributor:
    user: User
    contributions: int

    def __repr__(self) -> str:
        return f"{self.user.login} ({self.contributions} contributions)"
    
@dataclass
class Issue:
    number: int
    title: str
    author: User
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    labels: List[Label] = None
    assignees: List[User] = None

    def lifetime_days(self) -> Optional[int]:
        if self.closed_at:
            return (self.closed_at - self.created_at).days
        return None

    def __repr__(self) -> str:
        labels = [l.name for l in (self.labels or [])]
        return f"Issue #{self.number} [{self.state}] {self.title} (labels: {labels})"

    
@dataclass
class PullRequest:
    number: int
    title: str
    author: User
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    labels: List[Label] = None
    assignees: List[User] = None

    def time_to_merge(self) -> Optional[int]:
        if self.merged_at:
            return (self.merged_at - self.created_at).days
        return None

    def __repr__(self) -> str:
        merged = f", merged in {self.time_to_merge()} days" if self.merged_at else ""
        return f"PR #{self.number} [{self.state}] {self.title}{merged}"


@dataclass
class User:
    login: str
    url: str
    
    def __repr__(self) -> str:
        return f"User(login='{self.login}', url='{self.url}')"
    
@dataclass
class Label:
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Label(name='{self.name}', color='{self.color}')"
    
@dataclass
class Dependency:
    name: str
    version: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"{self.name}{self.version or ''}"
