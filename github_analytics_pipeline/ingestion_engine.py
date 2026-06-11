from _typeshed import _type_checker_internals
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class GitHubRepositoryPipeline():
    def __init__(self):
        token=os.environ.get("GITHUB_TOKEN")
        if not token or not token.strip():
            raise ValueError("Environment variable GITHUB_TOKEN is not set.")
        self.github_token=token.strip()

        self.session=requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}"
        })
        print("Ingestion Engine Intialised successfully")
    