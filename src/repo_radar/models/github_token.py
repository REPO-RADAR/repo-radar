from dataclasses import dataclass

@dataclass
class GitHubToken:
    token: str

    def to_header(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name} token='{self.token}'>"