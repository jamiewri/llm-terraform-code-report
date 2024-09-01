import os
import sys
sys.path.append(os.getcwd())

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from output_parsers import repository_summary_parser



def get_repository_summary_chain():

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o"
    )

    repository_summary_prompt = """
        - You are an expert infrastructure as code programmer, specializing in Terraform.
        - Your job is to judge the quality of the terraform code and provide feedback to the author.
        - You judgement must be in the form of a report that assigns a score out of 10 for each of the 
         provided file.
        - You must go judge the code based on the official Terraform Style Guide, which is supplied below.
        - If you know how to fix an issue in the code, you should provide a suggestion on how to fix it.
        - Your suggestions should start by referencing the file name and line number where the issue was found.
        - Your suggestions should also quote the line of code that needs to be fixed in the following format.
            ```hcl
            # The line of code that needs to be fixed
            ```
        - The code submission that you are to review is provided below.

        - If the submission does not meet the style guide, reference an example of where specifically in the
          submission they didnt meet the style guide, and provide feedback on how the code can be improved. 
        - Specifically reference the file name and line number where the issue was found.
        - The submission only have to meet the requirements of the style guide if they have impelmented that
          feature in the code.

        Task 1: Generate a report.
        - Given the Terraform files in the repositories, I want you to generate a report.
        - The report should contain the following information:
            - The title of the report as described in the below format example.
            - The owner of the repository.
            - The name of the repository.
            - The full name of the repository.
            - The list of Terraform files in the repository.
            - The score out of 10 for the repository.
        - The score should be calculated for each Terraform file in the repository.
        - The total score should be calculated as the sum of the scores for each Terraform file divided by the number of Terraform files.
        - The report should be in Markdown format.
        - If you are not 90% confident in your suggestion, its okay to not provide a suggestion.
        - If you do provide a suggestion, you must provide the line number of the code that needs to be fixed.

        Owner: {owner}
        Name: {name}
        Full Name: {full_name}
        Offical Terraform Style Guide: {terraform_style_guide}
        Terraform Files: {terraform_files}

        Your report should be in the following format:

        # IaC Repository Report
        - **Owner:** {owner}
        - **Repository:** {name}
        - **Terraform Files:**
            - `{terraform_files}`

        ## Feedback
        - ### <FILE NAME>
            - **Feedback:** 
              - <FEEDBACK>
            - **Score:** <SCORE>
            - **Suggestion:**
                - Current implementation
                  ```hcl
                  <EXISTING CODE>
                  ```
                  Suggested implementation
                  ```hcl 
                  <SUGGESTED CODE>
                  ```

        Total Score
        - **Total Score:** <TOTAL SCORE>/10

        """

    repository_summary_template = PromptTemplate(
        input_variables=["owner", "name", "full_name", "terraform_style_guide", "terraform_files"],
        template=repository_summary_prompt,
        partial_variables={"format_instructions": repository_summary_parser.get_format_instructions()
        },
    )

    return repository_summary_template | llm 


def get_user_summary_chain():
    print("Generating User Summary Report")

    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o-mini"
    )

    repository_summary_prompt = """
        - You are an expert infrastructure as code programmer, specializing in Terraform.
        - Your job is to summerize the all of the provided reports.
        - In your summary include a single sentance per report, including the name of the repository and the score.
        - Your report should be in markdown format.

        Repository Summary Quality Reports:
        {repository_summary_reports}

        Your report should be in the following format:
        # Engineer Summary Report
        - **GitHub User:** {owner}
        - **Repositories Analysed** 
            - <LIST OF REPOSITORIES>

        ### Summary
        - **<REPOSITORY NAME>**
            - **Summary:** <SUMMARY>
            - **Score:** <SCORE>

        **Total Score:** <TOTAL SCORE>/10
        """

    repository_summary_template = PromptTemplate(
        input_variables=["owner", "repository_summary_reports"],
        template=repository_summary_prompt,
        partial_variables={"format_instructions": repository_summary_parser.get_format_instructions()
        },
    )

    return repository_summary_template | llm 