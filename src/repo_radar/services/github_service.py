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
        
    def get_languages(self, url: GitHubUrl):
        resp: Response = self._run(self.client.get_languages(url))
        resp.raise_for_status()
        return resp.json() or {}
        
    def get_license(self, url: GitHubUrl):
        resp: Response = self._run(self.client.get_license(url))
        resp.raise_for_status()
        return resp.json() or {}
        
    def get_commits(self, url: GitHubUrl):
        pass
        
    def get_issues(self, url: GitHubUrl):
        pass
        
    def get_pulls(self, url: GitHubUrl):
        pass
    
    def get_contributors(self, url: GitHubUrl):
        pass
        
    def get_branches(self, url: GitHubUrl):
        pass
        
    def compare_branch(self, url: GitHubUrl):
        pass

@dataclass
class Repository:
    url: GitHubUrl
    branches: List[Branch] = None
    issues: Optional[dict] = None
    pulls: Optional[dict] = None
    contributors: Optional[dict] = None
    license: Optional[str] = None
    languages: Optional[dict] = None
    
@dataclass
class Branch:
    name: str
    commits: List[Commit] = None
    
@dataclass
class Commit:
    sha: str
    author: str
    date: datetime
    message: str