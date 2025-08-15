from repo_radar.api.github_client import GitHubClient as Client
from repo_radar.models.github_url import GitHubUrl
import asyncio

class GitHubService:
    
    def __init__(self, token: str):
        self.client = Client(token)
        
    def get_languages(self, url: GitHubUrl):
        response = asyncio.run(self.client.get_languages(url))
        
    def get_license(self, url: GitHubUrl):
        response = asyncio.run(self.client.get_license(url))
        
    def get_commits(self, url: GitHubUrl):
        Client.get_commits(url)
        
    def get_issues(self, url: GitHubUrl):
        Client.get_issues(url)
        
    def get_pulls(self, url: GitHubUrl):
        Client.get_pulls(url)
    
    def get_contributors(self, url: GitHubUrl):
        Client.get_contributors(url)
        
    def get_branches(self, url: GitHubUrl):
        Client.get_branches(url)
        
    def compare_branch(self, url: GitHubUrl):
        Client.compare_branch(url)

@dataclass
class Commit:
    str contributor
    int date_created
    

@dataclass
class GitHubCommits:
    List[commit]
    total_commits: int = 0
    
    
    def getCommitLast30Days -> int:
        commits = 0
        
        # for each commit, check date, increment if date < 30
        
        return commits