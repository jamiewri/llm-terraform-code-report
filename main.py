from agents.github_username import get as get_github_username
from chains.chains import get_repository_summary_chain, get_user_summary_chain
import argparse

from util.fs import write_file_to_disk, load_file_as_string
from util.util import get_hcl_repositories, find_hcl_files_in_repos, get_tf_file_contents_from_repos
from util.config import Config

def create_report(query: str, config: Config):

  # Search for Github Username from name
  github_username = get_github_username(query, debug=config.get('debug'))

  # Find Github users repositories that contain HCL code, sorted by updated_at
  repos = get_hcl_repositories(
     username=github_username.username, 
     max_repos=config.get('max_repos')
  )

  # Returns a list of files in each repo that contain Terraform files (.tf)
  repos_with_filenames = find_hcl_files_in_repos(
     repos=repos,
     max_files_per_repo=config.get('max_files_per_repo'),
     max_depth_per_repo=config.get('max_depth_per_repo')
  )

  # Returns content of each .tf file
  repos_with_contents = get_tf_file_contents_from_repos(repos_with_filenames, max=5)

  # Read Style Guide from disk
  hcl_style_guide = load_file_as_string("static/hcl_style_guide.md")
  
  # Generate Repository Summary Reports for every repository
  reports = []
  repository_summary_chain = get_repository_summary_chain()

  for r in repos_with_contents:
    print("Generating report for " + r["full_name"])
    repository_summary = repository_summary_chain.invoke(
        input={
            "owner": r["owner"],
            "name": r["name"],
            "full_name": r["full_name"],
            "terraform_style_guide": hcl_style_guide,
            "terraform_files": r["files"]
        }
    )
    write_file_to_disk(repository_summary.content, "reports/" + r["name"] + ".md")
    reports.append(repository_summary.content)

  # Generate User Summary Report
  user_summary_chain = get_user_summary_chain()
  user_summary = user_summary_chain.invoke(
      input={
          "owner": github_username.username,
          "repository_summary_reports": reports
      }
  )
  write_file_to_disk(user_summary.content, "reports/engineer-summary.md")
  

if __name__ == '__main__':

    # Parse args
    parser = argparse.ArgumentParser(description='Generate a report for a Github user')
    parser.add_argument('--search', type=str, help='Query to search for', required=True)
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--max-repos', type=int, help='Maximum number of repositories to search')
    parser.add_argument('--max-files-per-repo', type=int, help='Maximum number of files to search per repository')
    parser.add_argument('--max-depth-per-repo', type=int, help='Maximum depth to search per repository')

    args = parser.parse_args()

    # Set search query
    query = args.search

    # Set config
    config = Config()
    config.set('debug', args.debug)
    config.set('max_repos', args.max_repos)
    config.set('max_files_per_repo', args.max_files_per_repo)
    config.set('max_depth_per_repo', args.max_depth_per_repo)

    if config.get('debug'):
      print("Search: %s" % query)
      print("Debug: %s " % config.get('debug'))
      print("Max repos: %s" % config.get('max_repos'))
      print("Max files per repo: %s" % config.get('max_files_per_repo'))
      print("Max depth per repo: %s" % config.get('max_depth_per_repo'))

    create_report(query=query,
                  config=config)