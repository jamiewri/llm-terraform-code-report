from langchain_community.tools.tavily_search import TavilySearchResults
import requests
import os

gh_pat = os.environ.get('GH_PAT')

def get_github_profile_url(query: str):
    client = TavilySearchResults(
        include_domains=["github.com"],
    )
    response = client.run(f"{query}")
    return response[0]["url"]

def get_github_user_details(username: str):

    url = f"https://api.github.com/users/{username}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": "Bearer "+ gh_pat,
        }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}