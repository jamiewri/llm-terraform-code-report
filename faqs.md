# FAQs
- [Why are you comparing to the Terraform Specific Specification?](#why-are-you-comparing-to-the-terraform-specific-specification)
- [Why does this application report on repositories that do not contain any Terraform files?](#why-does-this-application-report-on-repositories-that-do-not-contain-any-terraform-files)

## Why are you comparing to the Terraform Specific Specification?

The first iteration of this application used [HashiCorp's offical Terraform style guide](https://developer.hashicorp.com/terraform/language/style), however because it mostly makes 'recommendations', the LLM would report that most examples conformed and was therefore less useful. 

In contrast, Azures [Terraform Specific Specification](https://azure.github.io/Azure-Verified-Modules/specs/terraform/) is written as ~40 hard requirements, with HCL examples. This is much easier for the LLM to make a decision if a code example conforms or not.

## Why does this application report on repositories that do not contain any Terraform files?

The function `get_hcl_repositories` filters all public repositories based on whether [GitHub's API](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user) `.language` contains `HCL`. This means that repositories containing only [Sentinel](https://developer.hashicorp.com/sentinel) code, for example, will still match and be reported on. A report in this instance will say that the repository didn't include any `.tf` files. 