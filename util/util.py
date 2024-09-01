import requests
import os
import dateutil.parser
import base64
from typing import List, Dict

gh_pat = os.environ.get('GH_PAT')

def get_hcl_repositories(username: str, max_repos: int = 3) -> list:
    """
    Returns list of all public repositories for a given GitHub username.
    - sorted by updated_at 

    Removing repostories that:
    - Dont contain > 50% HCL code
    - Are a fork

    Upto a maximum of `max` repositories are returned.
    """

    repos_url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer "+ gh_pat,
        }
    hcl_repos = []

    try:
        # GitHubs API paginates responses, so we need to loop through all pages
        while repos_url:

            response = requests.get(repos_url, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses
            repos = response.json()

            # sort by updated_at
            sorted_repos = sort_repositories_by_updated_at(repos)

            # Iterate through each repo in the response and check for
            # HCL code and not a fork
            for repo in sorted_repos:

                # Skip forked repos
                if repo['fork']:
                    continue

                # Add the repo to list if it contains >=50% HCL code
                if repo["language"] == "HCL":
                    hcl_repos.append(repo)

            # Check for the 'next' link in the response headers
            links = response.headers.get('Link', None)
            if links and 'rel="next"' in links:
                repos_url = links.split(';')[0].strip('<>')
            else:
                repos_url = None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching repositories: {e}")

    print("HCL repositories: ")
    [print("- " + r["full_name"]) for r in hcl_repos]

    return hcl_repos[:max_repos]



def sort_repositories_by_updated_at(repositories: List[Dict]) -> List[Dict]:

    # Convert the 'updated_at' string to a datetime object for sorting
    for repo in repositories:
        repo['updated_at'] = dateutil.parser.parse(repo['updated_at'])

    # Sort the repositories by 'updated_at' in descending order
    sorted_repositories = sorted(repositories, key=lambda x: x['updated_at'], reverse=True)

    # Convert 'updated_at' back to string if necessary for further processing
    for repo in sorted_repositories:
        repo['updated_at'] = repo['updated_at'].isoformat()

    return sorted_repositories

def find_hcl_files_in_repos(repos: List[Dict], 
                            max_files_per_repo: int, 
                            max_depth_per_repo: int,
                            ) -> List[Dict]:
    """
    Returns a list of repositories that contain Terraform files (.tf).
    Each repository object contains a list of Terraform files found in the repository.
    """
    repos_with_filenames = []
    for r in repos:
       repos_with_filenames.append({
           "owner": r["owner"]["login"],
           "name": r["name"],
           "full_name": r["full_name"],
           "hcl_files": get_hcl_filenames(
                 username=r["owner"]["login"],
                 repo=r["name"],
                 path="",
                 max_files_per_repo=max_files_per_repo,
                 max_depth_per_repo=max_depth_per_repo,
            )
    })

    return repos_with_filenames


def get_hcl_filenames(username: str, 
                      repo: str, 
                      path: str = '', 
                      max_files_per_repo: int = 5,
                      max_depth_per_repo: int = 1):
    """
    Fetches a list of .tf files from a GitHub repository, with configurable search depth.

    Args:
    - username (str): The GitHub username or organization name.
    - repo (str): The repository name.
    - path (str): The directory path to search in, default is root.
    - depth (int): The maximum depth of folders to crawl through.

    Returns:
    - list: A list of paths to .tf files within the repository.
    """
    depth = max_depth_per_repo


    if depth < 0:
        return []  # Stop recursion if maximum depth is reached
    api_url = f"https://api.github.com/repos/{username}/{repo}/contents/{path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer "+ gh_pat,
        }
    hcl_files = []

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        contents = response.json()

        for item in contents:
            if item['type'] == 'file' and item['name'].endswith('.tf'):
                hcl_files.append(item['path'])

            elif item['type'] == 'dir' and depth > 0:
                # Recursively search in directories, decrementing depth
                hcl_files.extend(get_hcl_filenames(username, 
                                                   repo=repo, 
                                                   path=item['path'], 
                                                   max_files_per_repo=99,
                                                   max_depth_per_repo=depth - 1))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository contents: {e}")

    return hcl_files[:max_files_per_repo]

def get_tf_file_contents_from_repos(repos: List[Dict], max: int = 5) -> List[Dict]:
    """
    Returns the content of each .tf file in the given list of repositories.
    """
    
    repos_with_contents = []
    for repo in repos:
        file_count = 0
        contents = []

        for file_path in repo["hcl_files"]:
            file_count += 1
            if file_count > max:
                break

            content = get_file_content(repo["full_name"], file_path)
            contents.append({
                "file_path": file_path,
                "content": content,
            })

        repos_with_contents.append({
            "owner": repo["owner"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "files": contents,
        })

    return repos_with_contents

def get_file_content(repo_full_name: str, file_path: str) -> str:
    """
    Fetches the content of a file from a public GitHub repository.

    Args:
    - repo_full_name (str): The full name of the repository (e.g., "octocat/Hello-World").
    - file_path (str): The path to the file within the repository.

    Returns:
    - str: The content of the file.
    """
    api_url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer "+ gh_pat,
        }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises an error for bad responses
        content_data = response.json()

        print("Getting content for file: " + repo_full_name + "/" + file_path)

        # Decode the base64 encoded content
        file_content = base64.b64decode(content_data['content']).decode('utf-8')
        return file_content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching file content: {e}")
        return ""