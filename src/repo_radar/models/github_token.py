from dataclasses import dataclass
from repo_radar.config import GITHUB_AUTH_HEADERS

@dataclass
class GitHubToken:
    """
    Represents a GitHub personal access token.

    Provides helper method to generate HTTP headers for authenticated
    or unauthenticated GitHub API requests.

    Attributes:
        - token_string (str): The raw GitHub personal access token string.
    """

    token_string: str

    def to_header(self) -> dict:
        """
        Return complete headers including auth. 
        If token is empty, assemble headers for unauthenticated API requests.
        """
        headers = dict(GITHUB_AUTH_HEADERS)
        if self.token_string:
            headers["Authorization"] = f"Bearer {self.token_string}"
        return headers

    def __repr__(self) -> str:
        """Return string representation of token class. Mask token value."""
        class_name = self.__class__.__name__
        masked = self.token_string[:4] + "…" if self.token_string else ""
        return f"<{class_name} token='{masked}'>"