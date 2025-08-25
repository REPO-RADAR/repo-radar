from __future__ import annotations
from repo_radar.api.github_client import GitHubClient as Client
from repo_radar.models.github_url import GitHubUrl
from requests import Response
from typing import Any, Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from datetime import datetime

class GitHubService:
    
    def __init__(self, token: str):
        self.client = Client(token)

    def _run(self, coro):
        return asyncio.run(coro)
        
    def get_languages(self, url: GitHubUrl) -> dict:
        resp: Response = self._run(self.client.get_languages(url))
        resp.raise_for_status()
        return resp.json() or {}
        
    def get_license(self, url: GitHubUrl) -> dict:
        resp: Response = self._run(self.client.get_license(url))
        resp.raise_for_status()
        data = resp.json() or {}
    
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
        
    def get_commits(self, url: GitHubUrl):
        pass
        
    def get_issues(self, url: GitHubUrl) -> List[Issue]:
        responses: List[Response] = self._run(self.client.get_issues(url))
        issues: List[Issue] = []
    
        for resp in responses:
            resp.raise_for_status()
            page_data = resp.json() or []
    
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
                    
                def parse_datetime(dt_str):
                    return datetime.fromisoformat(dt_str.rstrip("Z")) if dt_str else None
                
                # Dates
                created_at = parse_datetime(item.get("created_at"))
                updated_at = parse_datetime(item.get("updated_at"))
                closed_at = parse_datetime(item.get("closed_at"))
                
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

        
    def get_pulls(self, url: GitHubUrl):
        pass
    
    def get_contributors(self, url: GitHubUrl) -> List[Contributor]:
        responses: List[Response] = self._run(self.client.get_contributors(url))
        contributors: List[Contributor] = []
    
        for resp in responses:
            resp.raise_for_status()
            data = resp.json() or []
            for item in data:
                contributors.append(
                    Contributor(
                        user=User(login=item.get("login"), url=item.get("html_url")),
                        contributions=item.get("contributions", 0),                 
                    )
                )
        return contributors

        
    def get_branches(self, url: GitHubUrl):
        responses = self._run(self.client.get_branches(url))
        return responses
        
    def compare_branch(self, url: GitHubUrl):
        pass
    
    def get_repo(self, url: GitHubUrl):
        repo: Repository = Repository()
        repo.url = url
        
        repo.issues = self.get_issues(url)
        
        repo.contributors = self.get_contributors(url)
        repo.licenses = self.get_licenses(url)
        repo.languages = self.get_languages(url)

@dataclass
class Repository:
    url: GitHubUrl
    branches: List[Branch] = None
    issues: List[Issue] = None
    pulls: Optional[dict] = None
    contributors: List[Contributor] = None
    license: Optional[dict] = None
    languages: Optional[dict] = None
    
@dataclass
class Branch:
    name: str
    sha: str
    commits: List[Commit] = None
    
@dataclass
class Commit:
    sha: str
    author: User
    date: datetime
    message: str
    
@dataclass
class Contributor:
    user: User
    contributions: int
    
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

@dataclass
class User:
    login: str
    url: str
    
@dataclass
class Label:
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
