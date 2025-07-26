from dataclasses import dataclass

@dataclass
class GithubUrl:
    full_url: str
    org_user: str
    repo: str
    
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name} org_user='{self.org_user}' repo='{self.repo}'>"
