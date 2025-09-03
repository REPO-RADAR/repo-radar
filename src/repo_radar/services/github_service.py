from __future__ import annotations
from repo_radar.config import GITUB_DEFAULT_DELTA
from repo_radar.api.github_client import GitHubClient as Client
from repo_radar.models.github_url import GitHubUrl
from requests import Response
from typing import List
import asyncio
from datetime import datetime

from repo_radar.models.github_repoistory import (
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


class GitHubService:
    
    def __init__(self, token: str):
        self.client = Client(token)

    def _run(self, coro):
        return asyncio.run(coro)
        
    def get_languages(self, url: GitHubUrl) -> dict:
        response: Response = self._run(self.client.get_languages(url))
        response.raise_for_status()
        return response.json() or {}
        
    def get_license(self, url: GitHubUrl) -> dict:
        response: Response = self._run(self.client.get_license(url))
        response.raise_for_status()
        data = response.json() or {}
    
        license_info = data.get("license")
        if license_info:
            return {
                "name": license_info.get("name"),
                "spdx_id": license_info.get("spdx_id"),
                "url": license_info.get("url"),
            }
        return {
            "name": data.get("name"),
            "path": data.get("path"),
            "download_url": data.get("download_url"),
        }
        
    def get_commits(self, url: GitHubUrl, delta: int = 0) -> List[Commit]:
        responses = self._run(self.client.get_commits(url, delta))
        commits: List[Commit] = []
        
        for response in responses:
            response.raise_for_status()
            data = response.json() or []
            for item in data:
                commit_info = item.get("commit", {})
                sha = item.get("sha")
                author_data = item.get("author")
                author_info = commit_info.get("author", {})
                
                if author_data:
                    author = User(login=author_data["login"], url=author_data["html_url"])
                else:
                    author = User(login=author_info.get("name"), url=None)

                
                date = self._parse_datetime(author_info.get("date"))
                message = commit_info.get("message")
                commits.append(Commit(sha=sha, author=author, date=date, message=message))
        return commits

        
    def get_issues(self, url: GitHubUrl, delta: int = 0) -> List[Issue]:
        responses: List[Response] = self._run(self.client.get_issues(url, delta))
        issues: List[Issue] = []
    
        for response in responses:
            response.raise_for_status()
            page_data = response.json() or []
    
            for item in page_data:
                # Author
                author_data = item.get("user", {})
                author = User(login=author_data.get("login"), url=author_data.get("html_url"))
    
                # Assignees
                assignees_data = item.get("assignees", [])
                assignees: List[User] = []
                for u in assignees_data:
                    assignees.append(User(login=u.get("login"), url=u.get("html_url")))
    
                # labels
                labels_data = item.get("labels", [])
                labels: List[Label] = []
                for l in labels_data:
                    labels.append(Label(name=l.get("name"), color=l.get("color"), description=l.get("description")))
                
                # Dates
                created_at = self._parse_datetime(item.get("created_at"))
                updated_at = self._parse_datetime(item.get("updated_at"))
                closed_at = self._parse_datetime(item.get("closed_at"))
                
                issue = Issue(
                    number=item.get("number"),
                    title=item.get("title"),
                    author=author,
                    assignees=assignees,
                    state=item.get("state"),
                    created_at=created_at,
                    updated_at=updated_at,
                    closed_at=closed_at,
                    labels=labels
                )
    
                issues.append(issue)
    
        return issues
     
    def get_pulls(self, url: GitHubUrl, delta: int = 0) -> List[PullRequest]:
        responses: List[Response] = self._run(self.client.get_pulls(url, delta))
        pulls: List[PullRequest] = []
    
        for response in responses:
            response.raise_for_status()
            data = response.json()
    
            for item in data:
                # Author
                user_data = item.get("user", {})
                author = User(login=user_data.get("login"), url=user_data.get("html_url"))
    
                # Assignees
                assignees: List[User] = []
                for u in item.get("assignees", []):
                    assignees.append(User(login=u.get("login"), url=u.get("html_url")))
    
                # Labels
                labels: List[Label] = []
                for l in item.get("labels", []):
                    labels.append(
                        Label(
                            name=l.get("name"),
                            color=l.get("color"),
                            description=l.get("description"),
                        )
                    )
    
                # Dates
                created_at = self._parse_datetime(item.get("created_at"))
                updated_at = self._parse_datetime(item.get("updated_at"))
                closed_at = self._parse_datetime(item.get("closed_at"))
                merged_at = self._parse_datetime(item.get("merged_at"))
    
                pulls.append(
                    PullRequest(
                        number=item.get("number"),
                        title=item.get("title"),
                        author=author,
                        assignees=assignees,
                        state=item.get("state"),
                        created_at=created_at,
                        updated_at=updated_at,
                        closed_at=closed_at,
                        merged_at=merged_at,
                        labels=labels,
                    )
                )
    
        return pulls

    
    def get_contributors(self, url: GitHubUrl) -> List[Contributor]:
        responses: List[Response] = self._run(self.client.get_contributors(url))
        contributors: List[Contributor] = []
    
        for response in responses:
            response.raise_for_status()
            data = response.json() or []
            for item in data:
                contributors.append(
                    Contributor(
                        user=User(login=item.get("login"), url=item.get("html_url")),
                        contributions=item.get("contributions", 0),                 
                    )
                )
        return contributors
        
    def get_branch_names(self, url: GitHubUrl) -> dict:
        responses = self._run(self.client.get_branches(url))
        metadata = self._run(self.client.get_repo_metadata(url))
        branches: dict = {}
        default_branch = metadata.json().get("default_branch")
        
        for response in responses:
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                name = item.get("name")
                sha = item.get("commit", {}).get("sha")
                if name and sha:
                    branches[name] = sha
                    
        # Drop the default branch
        branches.pop(default_branch, None)
        
        return branches
    
    def get_branches(self, url: GitHubUrl, delta: int = 0) -> List[Branch]:
        branch_names = self.get_branch_names(url)
        branches: List[Branch] = []
    
        for name, sha in branch_names.items():
            commits = self.compare_branch(url, sha, delta)
            branches.append(Branch(name=name, sha=sha, commits=commits))
    
        return branches

        
    def compare_branch(self, url: GitHubUrl, sha: str, delta: int = 0) -> List[Commit]:
        responses = self._run(self.client.compare_branch(url, sha, delta))
        commits: List[Commit] = []
        
        for response in responses:
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("commits", []):
                commit_info = item.get("commit", {})
                commit_sha = item.get("sha")
    
                user_data = item.get("author")
                author_info = commit_info.get("author", {})
    
                if user_data:
                    author = User(
                        login=user_data.get("login"),
                        url=user_data.get("html_url")
                    )
                else:
                    author = User(
                        login=author_info.get("name"),
                        url=None
                    )
    
                date_str = author_info.get("date")
                date = self._parse_datetime(date_str)
                message = commit_info.get("message")
    
                commits.append(
                    Commit(sha=commit_sha, author=author, date=date, message=message)
                )
        
        
        return commits
    
    def get_dependencies(self, url: GitHubUrl) -> List[Dependency]:
        pass
    
    def get_repo(self, url: GitHubUrl, delta: int = GITUB_DEFAULT_DELTA) -> Repository:
        repo: Repository = Repository()
        
        repo.url = url
        repo.default_branch_commits = self.get_commits(url, delta)
        repo.branches = self.get_branches(url, delta)
        repo.issues = self.get_issues(url)
        repo.pulls = self.get_pulls(url)
        repo.contributors = self.get_contributors(url)
        repo.license = self.get_license(url)
        repo.languages = self.get_languages(url)
        
        return repo
        
    def _parse_datetime(self, dt_str: str):
        return datetime.fromisoformat(dt_str.rstrip("Z")) if dt_str else None