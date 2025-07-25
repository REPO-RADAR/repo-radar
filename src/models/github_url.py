from dataclasses import dataclass

@dataclass
class GithubUrl:
    full_url: str
    org_user: str
    repo: str
