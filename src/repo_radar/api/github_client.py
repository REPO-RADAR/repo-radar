from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from repo_radar.models.github_token import GitHubToken

class GitHubApiClient(ABC):

    @abstractmethod
    def validate_token(self, token: str):
        pass

    @abstractmethod
    def get_repo(self, owner: str, repo: str) -> Dict:
        pass