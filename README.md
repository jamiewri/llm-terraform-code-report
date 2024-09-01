# Terraform Code Report 

###### (An autonomous agent built with OpenAI, Langchain, and Tavily)

<img src="static/terraform-code-report.webp" width="500px">

This application takes a natural language description of an engineer, for example `Jamie Wright who works are HashiCorp`, then returns a report of how well their most recent GitHub commits conform to the [Terraform Specific Specification](https://azure.github.io/Azure-Verified-Modules/specs/terraform/) from Azure. 

It will write a repository report for each HCL repository found, then write a report summarizing all repository reports into 1 engineer report. 

> :information_source: This application is a prototype to validate the technology. I'm not suggesting that an LLM can perform an equivalant to human level performance when evaluating adherence to coding standards. 

> :warning: This is a prototype. Limited error handling has been implemented.

## Workflow

1.  Search the web for the GitHub username of the described person.
    - If the query includes a reference to the users employment, then the application with validate that it has found the correct user by further searching the listed organization on their GitHub profile.
2. Search the users GitHub organization for public repositories.
    - Sorting by most recently updated.
    - Excluding forks.
    - Selecting only repositories that contain 50% HCL code.
3. Search inside each of the selected repositories for files ending in `.tf`.
    - Searching to a configurable directory depth.
    - Upto a configurable maximum number of files.
    - Downloading all matching files.
4. Generate reports
    - Write a report summarizing the files adherence to the style guide and output a markdown report per repository.
    - Write a report summarizing each the contents of all of the repository reports and output final markdown report.

An example or each of these reports can be found [here](#example-reports-generated).

## Configuration
Include the following command line flags to set configuration.
| Item | Required | Default value | Example | Description |
| - | - | - | - | - | 
| search | Required | - | `--search="Jamie Wright who works are HashiCorp"` | Sets search query string. |
| debug | Optional | `false` | `--debug` | Increase logging verbosity. |
| max-repos | Optional | `3` | `--max-repos=3` | Maximum number of repositorys to include in report, sorted by most recently updated first. |
| max-files-per-repo | Optional | `5` | `--max-files-per-repo=5` | Maximum number of `.tf` files to evaluate per repository. |
| max-depth-per-repo | Optional | `3` | `--max-depth-per-repo=3` | Maximum directory depth to search for HCL files. |


## Usage

Create Python virtual environment and install dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

> :information_source: `requirements.txt` will install  `latest`. Change to `requirements-2024-01-09.txt` for known working version.

Required API tokens.

| API | Required | Description |
| -- | -- | -- |
| [Open AI API Token](https://platform.openai.com/api-keys) | Required | Used to authenticate to Open AI's API. |
| [Tavily API Token](https://app.tavily.com/home) | Required | [Tavily](https://tavily.com) is a search engine built specifically for AI agents. This application uses this API to search for the GitHub users username.  |
| [GitHub Personal Access Token](https://github.com/settings/tokens) |  Required | Every HCL file analyzed requires 1 request to the GitHub API. [Unauthenticated](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users) requests are rate limited to 60 per hour. [Authenticated](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-authenticated-users) requests are are rated limited to 5,000 per hour. |


Export the required API tokens as environment variables.
```bash
export GH_PAT=<...>
export OPENAI_API_KEY=<...>
export TAVILY_API_KEY=<...>
```

Run the application
```bash
python3 main.py --search="Jamie Wright who works at HashiCorp"
```

## Example output

```bash
python3 main.py --search="Jamie Wright who works are HashiCorp"
> Entering new AgentExecutor chain...
I need to find the GitHub username for Jamie Wright, who works at HashiCorp. First, I will search for Jamie Wright's GitHub profile to find the username. 

Action: Search Google for a GitHub profile  
Action Input: "Jamie Wright HashiCorp GitHub"  https://gist.github.com/jamiewriThe link I found is a Gist, which may not directly indicate the GitHub username. I need to check if this Gist belongs to Jamie Wright and if they work at HashiCorp.

Action: Get more details about a GitHub user  
Action Input: "jamiewri"  {'login': 'jamiewri', 'id': 29832082, 'node_id': 'MDQ6VXNlcjI5ODMyMDgy', 'avatar_url': 'https://avatars.githubusercontent.com/u/29832082?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/jamiewri', 'html_url': 'https://github.com/jamiewri', 'followers_url': 'https://api.github.com/users/jamiewri/followers', 'following_url': 'https://api.github.com/users/jamiewri/following{/other_user}', 'gists_url': 'https://api.github.com/users/jamiewri/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/jamiewri/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/jamiewri/subscriptions', 'organizations_url': 'https://api.github.com/users/jamiewri/orgs', 'repos_url': 'https://api.github.com/users/jamiewri/repos', 'events_url': 'https://api.github.com/users/jamiewri/events{/privacy}', 'received_events_url': 'https://api.github.com/users/jamiewri/received_events', 'type': 'User', 'site_admin': False, 'name': 'Jamie Wright', 'company': '@hashicorp', 'blog': 'https://jamiewright.io', 'location': 'Melbourne, Australia', 'email': 'jamie@jamiewright.io', 'hireable': None, 'bio': None, 'twitter_username': 'jamie_wri', 'public_repos': 51, 'public_gists': 1, 'followers': 25, 'following': 52, 'created_at': '2017-07-02T07:45:27Z', 'updated_at': '2024-08-18T22:05:26Z', 'private_gists': 0, 'total_private_repos': 114, 'owned_private_repos': 112, 'disk_usage': 197252, 'collaborators': 5, 'two_factor_authentication': True, 'plan': {'name': 'pro', 'space': 976562499, 'collaborators': 0, 'private_repos': 9999}}I have confirmed that the GitHub user "jamiewri" is indeed Jamie Wright and they work at HashiCorp. Now I can return the username in the required JSON format.

Final Answer: {"username": "jamiewri"}

> Finished chain.
Github username found: jamiewri
HCL repositories: 
- jamiewri/snapshot-securing-access-to-kubernetes-with-boundary
- jamiewri/consul-service-discovery
- jamiewri/terraform-tfe-workspace
- jamiewri/tf-common-patterns
- jamiewri/tfc-management
Getting content for file: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary/deploy/boundary-config/accounts.tf
Getting content for file: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary/deploy/boundary-config/admin.tf
Getting content for file: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary/deploy/boundary-config/auth_method.tf
Getting content for file: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary/deploy/boundary-config/groups.tf
Getting content for file: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary/deploy/boundary-config/kube.tf
Getting content for file: jamiewri/consul-service-discovery/deploy/compute-bastion.tf
Getting content for file: jamiewri/consul-service-discovery/deploy/compute-consul.tf
Getting content for file: jamiewri/consul-service-discovery/deploy/compute-web.tf
Getting content for file: jamiewri/consul-service-discovery/deploy/data.tf
Getting content for file: jamiewri/consul-service-discovery/deploy/firewall.tf
Getting content for file: jamiewri/terraform-tfe-workspace/main.tf
Getting content for file: jamiewri/terraform-tfe-workspace/providers.tf
Getting content for file: jamiewri/terraform-tfe-workspace/variables.tf
Generating report for jamiewri/snapshot-securing-access-to-kubernetes-with-boundary
Generating report for jamiewri/consul-service-discovery
Generating report for jamiewri/terraform-tfe-workspace
Generating User Summary Report
```

## Example reports generated

<details> 
  <summary>reports/snapshot-securing-access-to-kubernetes-with-boundary.md</summary>

---

# IaC Code Quality Report: jamiewri/snapshot-securing-access-to-kubernetes-with-boundary

- **Owner:** jamiewri
- **Name:** snapshot-securing-access-to-kubernetes-with-boundary
- **Full Name:** jamiewri/snapshot-securing-access-to-kubernetes-with-boundary
- **Terraform Files:**
  - `deploy/boundary-config/accounts.tf`
  - `deploy/boundary-config/admin.tf`
  - `deploy/boundary-config/auth_method.tf`
  - `deploy/boundary-config/groups.tf`
  - `deploy/boundary-config/kube.tf`

## Feedback

### deploy/boundary-config/accounts.tf
- **Feedback:** The file is generally well-structured but has some issues:
  - Hardcoded passwords should be avoided for security reasons.
  - The `for_each` loop is used correctly, but the variable `var.users` should be defined and documented.
- **Score:** 7/10
- **Suggestion:**
  ```hcl
  # Line 9: Avoid hardcoding passwords
  password = "password123"
  ```
  Replace with:
  ```hcl
  password = var.user_passwords[each.key]
  ```

### deploy/boundary-config/admin.tf
- **Feedback:** The file is well-structured but has some issues:
  - Hardcoded passwords should be avoided for security reasons.
  - The `scope_id` and `grant_scope_id` should be parameterized.
- **Score:** 7/10
- **Suggestion:**
  ```hcl
  # Line 19: Avoid hardcoding passwords
  password = "password123"
  ```
  Replace with:
  ```hcl
  password = var.admin_password
  ```

### deploy/boundary-config/auth_method.tf
- **Feedback:** The file is well-structured but has some issues:
  - The `scope_id` should be parameterized.
- **Score:** 8/10
- **Suggestion:**
  ```hcl
  # Line 8: Parameterize scope_id
  scope_id = boundary_scope.org.id
  ```
  Replace with:
  ```hcl
  scope_id = var.scope_id
  ```

### deploy/boundary-config/groups.tf
- **Feedback:** The file is well-structured but has some issues:
  - The `for_each` loop is used correctly, but the variable `var.users` should be defined and documented.
  - The `scope_id` should be parameterized.
- **Score:** 8/10
- **Suggestion:**
  ```hcl
  # Line 18: Parameterize scope_id
  scope_id = boundary_scope.org.id
  ```
  Replace with:
  ```hcl
  scope_id = var.scope_id
  ```

### deploy/boundary-config/kube.tf
- **Feedback:** The file is well-structured but has some issues:
  - The `scope_id` should be parameterized.
  - The `address` should be parameterized.
- **Score:** 7/10
- **Suggestion:**
  ```hcl
  # Line 28: Parameterize scope_id
  scope_id = boundary_scope.project.id
  ```
  Replace with:
  ```hcl
  scope_id = var.scope_id
  ```

  ```hcl
  # Line 48: Parameterize address
  address = "http://vault:8200"
  ```
  Replace with:
  ```hcl
  address = var.vault_address
  ```

## Total Score
- **Total Score:** 7.4/10

The total score is calculated as the average of the individual file scores.

</details>

<details> 
  <summary>reports/consul-service-discovery.md</summary>

---
# IaC Code Quality Report: jamiewri/consul-service-discovery

- **Owner:** jamiewri
- **Name:** consul-service-discovery
- **Full Name:** jamiewri/consul-service-discovery
- **Terraform Files:**
  - `deploy/compute-bastion.tf`
  - `deploy/compute-consul.tf`
  - `deploy/compute-web.tf`
  - `deploy/data.tf`
  - `deploy/firewall.tf`

## Feedback

### deploy/compute-bastion.tf
- **Feedback:** 
  - **Issue:** The `metadata` block uses string interpolation for a single variable, which is unnecessary.
  - **Suggestion:** 
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${file(var.ssh_key)} ${var.ssh_user}"
    }
    ```
    should be:
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${file(var.ssh_key)} ${var.ssh_user}"
    }
    ```
  - **Score:** 8/10

### deploy/compute-consul.tf
- **Feedback:** 
  - **Issue:** The `metadata` block uses string interpolation for a single variable, which is unnecessary.
  - **Suggestion:** 
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${tls_private_key.bastion.public_key_openssh} ${var.ssh_user}"
    }
    ```
    should be:
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${tls_private_key.bastion.public_key_openssh} ${var.ssh_user}"
    }
    ```
  - **Score:** 8/10

### deploy/compute-web.tf
- **Feedback:** 
  - **Issue:** The `metadata` block uses string interpolation for a single variable, which is unnecessary.
  - **Suggestion:** 
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${tls_private_key.bastion.public_key_openssh} ${var.ssh_user}"
    }
    ```
    should be:
    ```hcl
    metadata = {
      sshKeys = "${var.ssh_user}:${tls_private_key.bastion.public_key_openssh} ${var.ssh_user}"
    }
    ```
  - **Score:** 8/10

### deploy/data.tf
- **Feedback:** 
  - **Issue:** The `locals` block uses string interpolation for a single variable, which is unnecessary.
  - **Suggestion:** 
    ```hcl
    myip           = "${jsondecode(data.http.myip_json.body).ip}/32"
    ```
    should be:
    ```hcl
    myip           = jsondecode(data.http.myip_json.body).ip/32
    ```
  - **Score:** 9/10

### deploy/firewall.tf
- **Feedback:** 
  - **Issue:** The `source_ranges` block uses string interpolation for a single variable, which is unnecessary.
  - **Suggestion:** 
    ```hcl
    source_ranges = [
      local.myip,
      google_compute_subnetwork.subnet.ip_cidr_range,
    ]
    ```
    should be:
    ```hcl
    source_ranges = [
      local.myip,
      google_compute_subnetwork.subnet.ip_cidr_range,
    ]
    ```
  - **Score:** 9/10

## Total Score
- **Total Score:** 8.4/10

</details>

<details> 
  <summary>reports/terraform-tfe-workspace.md</summary>

---
# IaC Repository Report: jamiewri/terraform-tfe-workspace
- **Owner:** jamiewri
- **Name:** terraform-tfe-workspace
- **Full Name:** jamiewri/terraform-tfe-workspace
- **Terraform Files:**
    - `main.tf`
    - `providers.tf`
    - `variables.tf`

## Feedback

### main.tf
- **Feedback:** 
  - The `resource` and `data` blocks are generally well-structured, but there are some areas for improvement:
    - The `vcs_repo` block should be alphabetically ordered.
    - The `for_each` usage is correct, but the `count` meta-argument is missing.
    - The `depends_on` meta-argument is missing.
- **Score:** 7/10
- **Suggestion:** 
    ```hcl
    resource "tfe_workspace" "workspace" {
      organization = var.organization
      name         = var.name
      description  = var.description
      tag_names    = var.tag_names
      auto_apply   = var.auto_apply

      vcs_repo {
        branch         = var.vcs_repo_branch
        identifier     = var.vcs_repo_identifier
        oauth_token_id = var.vcs_repo_oauth_token_id
      }
    }

    data "tfe_team" "team" {
      for_each = {
        for team in var.teams_access :
        team.name => team
      }

      name         = each.value.name
      organization = var.organization
    }

    resource "tfe_team_access" "team_access" {
      for_each = {
        for team in var.teams_access :
        team.name => team
      }

      access       = each.value.access
      team_id      = data.tfe_team.team[each.value.name].id
      workspace_id = tfe_workspace.workspace.id
    }
    ```

### providers.tf
- **Feedback:** 
  - The `required_providers` block is missing the `source` property for the `tfe` provider.
  - The `required_version` constraint should include a maximum version.
- **Score:** 6/10
- **Suggestion:** 
    ```hcl
    terraform {
      required_version = ">= 1.0, < 2.0"
      required_providers {
        tfe = {
          source  = "hashicorp/tfe"
          version = ">= 0.31, < 1.0"
        }
      }
    }
    ```

### variables.tf
- **Feedback:** 
  - The `type` for `tag_names` should be more specific than `list(any)`.
  - The `type` for `auto_apply` should be `bool` instead of `string`.
  - Descriptions for variables are missing.
  - Variables should be ordered with required fields first, followed by optional fields.
- **Score:** 5/10
- **Suggestion:** 
    ```hcl
    variable "name" {
      type        = string
      description = "The name of the workspace."
    }

    variable "organization" {
      type        = string
      description = "The organization to which the workspace belongs."
    }

    variable "description" {
      type        = string
      description = "The description of the workspace."
    }

    variable "tag_names" {
      type        = list(string)
      default     = []
      description = "A list of tag names to associate with the workspace."
    }

    variable "auto_apply" {
      type        = bool
      default     = false
      description = "Whether to automatically apply changes."
    }

    variable "vcs_repo_identifier" {
      type        = string
      description = "The identifier of the VCS repository."
    }

    variable "vcs_repo_branch" {
      type        = string
      default     = "master"
      description = "The branch of the VCS repository."
    }

    variable "vcs_repo_oauth_token_id" {
      type        = string
      description = "The OAuth token ID for the VCS repository."
    }

    variable "teams_access" {
      type = list(object({
        name   = string
        access = string
      }))
      default     = []
      description = "A list of teams and their access levels."
    }
    ```

## Total Score
- **Total Score:** 6/10

The overall score is calculated as the average of the individual file scores: (7 + 6 + 5) / 3 = 6.

</details>

<details> 
  <summary>reports/engineer-summary.md</summary>

---
# Engineer Summary Report: jamiewri
- **GitHub User:** jamiewri
- **Repositories Analysed** 
    - snapshot-securing-access-to-kubernetes-with-boundary
    - consul-service-discovery
    - terraform-tfe-workspace

### Summary
- snapshot-securing-access-to-kubernetes-with-boundary
    - The repository has a total score of 7.4/10, with individual file scores ranging from 7 to 8, highlighting issues such as hardcoded passwords and the need for parameterization.
    - **Score:** 7.4/10

- consul-service-discovery
    - The repository achieved a total score of 8.4/10, with all files scoring between 8 and 9, primarily addressing unnecessary string interpolation in metadata blocks.
    - **Score:** 8.4/10

- terraform-tfe-workspace
    - This repository received a total score of 6/10, with individual file scores indicating areas for improvement in variable types, ordering, and missing properties in the provider block.
    - **Score:** 6/10

**Total Score:** 7.26/10

</details>

## FAQs

- [Why are you comparing to the Terraform Specific Specification?](faqs.md#why-are-you-comparing-to-the-terraform-specific-specification)
- [Why does this application report on repositories that do not contain any Terraform files?](faqs.md#why-does-this-application-report-on-repositories-that-do-not-contain-any-terraform-files)


## Improvements

1. Reports are still generic and appear to be repeating the same 3-4 rule violations.
    -  Evaluate each Terraform resource against each coding standard rule individually. Similar to how CoPilot and CodeWhisperer prompt, but probably using the [Batch API](https://platform.openai.com/docs/guides/batch).
2. Repetitive `requests` definition.
    - Migrate to [GitHub Python SDK](https://github.com/PyGithub/PyGithub).
3. Serialization of inference and downloads negatively impacts overall run time.
    - Implement `asyncio` and/or `threads`.
4. CLI invocation
    - Implement web-based UI. Example [Researcher GPT](https://github.com/assafelovic/gpt-researcher) has a0n open source portal.
5. Repository logic matches all HCL code.
    - Implement logic to require at least a configurable number of `.tf` files to be present in repository.