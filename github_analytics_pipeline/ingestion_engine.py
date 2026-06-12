import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GitHubRepositoryPipeline():
    def __init__(self):
        token = os.environ.get("GITHUB_TOKEN")
        if not token or not token.strip():
            raise ValueError("Environment variable GITHUB_TOKEN is not set.")
        self.github_token = token.strip()

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}"
        })
        print("Ingestion Engine Initialized successfully")

    def _fetch_commits(self, repo_name, per_page: int = 100):
        url = f"https://api.github.com/repos/{repo_name}/commits"
        params = {
            "per_page": per_page,
            "page": 1
        }
        
        while url:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                self.link_header = response.headers.get("link")
                data = response.json()
                
                for commit in data:
                    yield commit
                
                url = None
                params = None
                
                if self.link_header:
                    links = self.link_header.split(',')
                    for link in links:
                        if 'rel="next"' in link:
                            next_url = link.split(';')[0].strip()
                            url = next_url.strip('<>')  
                            break
                            
            except requests.RequestException as e:
                print(f"Exception during fetching commits: {e}")
                break 


if __name__=='__main__':
    pipeline = GitHubRepositoryPipeline()
    commit_count = 0
    for commit in pipeline._fetch_commits('torvalds/linux', per_page=50):
        commit_info = commit.get("commit", {})
        author_info = commit_info.get("author", {})
        author = author_info.get("name", "Unknown Author")
        sha = commit.get("sha", "Unknown SHA")
        
        print(f"commit found by author {author} : {sha}")
        commit_count += 1
        if commit_count >= 300:
            print(f"\nSuccessfully traversed {commit_count // 50} pages!")
            break
            
    print(f"Total commits found: {commit_count}")
