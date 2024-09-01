import os
import sys
sys.path.append(os.getcwd())

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from tools.tools import get_github_profile_url, get_github_user_details
from output_parsers import github_user_parser
from output_parsers import GitHubUser

def get(name: str, debug: bool = False) -> GitHubUser:
    llm = ChatOpenAI(
        temperature=0,
        model_name="gpt-4o-mini"
    )

    template = """
        Follow the sequence of tasks, in order, take your time and do not rush.
        If you make a mistake, or dont find the information you need, you can start again.

        Task 1: Find the GitHub username.
        - Given the full name {name}, I want you to find me their GitHub username.
        - If you find a GitHub profile URL, please extract the username from the URL.
        - If you find a GitHub repository URL, please extract the username from the URL.
        - If you have found a Github profile page or repository page, the username is string in the URL directly after 'https://github.com/', and before the next '/'.
        - Before you return your answer, check that this user does work at the company you are looking for.
        - If the Github user does not work at the company, please start your search again.
        - Only return the Github username and not the full URL.

        
        \n{format_instructions}
        """

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["name"],
        partial_variables={"format_instructions": github_user_parser.get_format_instructions()},
    )

    tools_for_agent = [
        Tool(
            name="Search Google for a GitHub profile",
            func=get_github_profile_url,
            description="Useful for when you need to get a GitHub profile URL for a person.",
        ),
        Tool(
            name="Get more details about a GitHub user",
            func=get_github_user_details,
            description="Useful for when you need to know more details about a GitHub user, for example which organization they work for. Input must be a github username.",
        ),
    ]

    react_prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(
        llm=llm,
        tools=tools_for_agent,
        prompt=react_prompt,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_for_agent,
        verbose=debug,
        output_parser=github_user_parser,
    )

    result = agent_executor.invoke(
        input={
            "input": prompt_template.format_prompt(name=name),
        },
        handle_parsing_errors=True
    )
    github_user: GitHubUser = GitHubUser.parse_raw(result["output"])

    if github_user.username == "":
        print("Could not find Github username for " + name)
        exit(1)

    if debug:
        print("Github username found: " + github_user.username)

    return github_user


if __name__ == '__main__':
    pass