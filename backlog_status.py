import argparse
from openai import OpenAI
import requests
import json

def fetch_issue(repo, issue_number, github_token):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    response = requests.get(url, headers=headers)
    response = response.json()
    filtered_response = {
        "number": response["number"],
        "title": response["title"],
        "url": response["html_url"],
        "sub_issues_summary": response["sub_issues_summary"]
    }
    return json.dumps(filtered_response)

def search_issue_by_title(repo, title, github_token):
    url = f"https://api.github.com/search/issues?q=repo:{repo}+in:title+{title}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    response = requests.get(url, headers=headers)
    response = response.json()
    filtered_response = {
        "number": response["items"][0]["number"],
        "title": response["items"][0]["title"],
        "url": response["items"][0]["html_url"],
        "sub_issues_summary": response["items"][0]["sub_issues_summary"]
    }
    return json.dumps(filtered_response)

def fetch_sub_issues(repo, issue_number, github_token):
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/sub_issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"
    response = requests.get(url, headers=headers)
    formatted_issues = []
    for issue in response.json():
        formatted_issue = {
            "number": issue.get("number"),
            "title": issue.get("title"),
            "assignees": [assignee["login"] for assignee in issue.get("assignees", [])],
            "url": issue.get("html_url"),
            "state": issue.get("state")
        }
        formatted_issues.append(formatted_issue)
    return json.dumps(formatted_issues)

def query_openai(openai_token, messages):
    client = OpenAI(api_key=openai_token)
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        functions=[
            {
                "name": "fetch_issue",
                "description": "Fetch details of a GitHub issue.",
                "parameters": {"type": "object", "properties": {"issue_number": {"type": "integer"}}}
            },
            {
                "name": "fetch_sub_issues",
                "description": "Fetch all the sub-issues of a GitHub issue.",
                "parameters": {"type": "object", "properties": {"issue_number": {"type": "integer"}}}
            },
            {
                "name": "search_issue_by_title",
                "description": "Search for an issue by title",
                "parameters": {"type": "object", "properties": {"title": {"type": "string"}}}
            }
        ],
        function_call="auto"
    )
    return response.choices[0].message

def handle_function_call(function_call, repo, github_token):
    function_name = function_call.name
    arguments = json.loads(function_call.arguments)

    if function_name == "fetch_issue":
        return fetch_issue(repo, arguments["issue_number"], github_token), "fetch_issue"
    elif function_name == "search_issue_by_title":
        return search_issue_by_title(repo, arguments["title"], github_token), "search_issue_by_title"
    elif function_name == "fetch_sub_issues":
        return fetch_sub_issues(repo, arguments["issue_number"], github_token), "fetch_sub_issues"

    return None

messages = [
    {"role": "system", "content": """
You are an AI assistant that helps users retrieve information about GitHub issues from a repository.
Your job is to determine which issue the user is referring to and provide a detailed response based on the issue and its sub-issues.

#### Workflow:
1. If the user provides a ticket number, fetch the issue using `fetch_issue`.
2. If the user provides a title (or an unclear reference), search for the issue using `search_issue_by_title`.
3. Once the main issue is retrieved, extract:
- **The title** (for clarity in responses).
- **The `sub_issue_progress` field** (to summarize overall progress).
4. Fetch all **sub-issues** using `fetch_sub_issues`.
5. Collect and summarize details from sub-issues, including:
- **Assignees** (list all people working on the ticket).
- **Status** (track progress from sub-issues).
- **Links** to each sub-issue for further details.
6. Return a structured response summarizing:
- **Who is assigned to the issue** (including sub-issue assignees).
- **Overall progress** (from `sub_issue_progress`).
- **Links** to all related sub-issues.

Your response should be **concise, structured, and professional**.
If multiple people are assigned, list them clearly.
If sub-issues exist, provide their details with links. Make sure the response is easy to understand.
     """},
]

def main():
    parser = argparse.ArgumentParser(description="Get issue status from GitHub via OpenAI")
    parser.add_argument("prompt", type=str, help="The question to ask about a GitHub issue")
    parser.add_argument("--github-token", required=False, help="GitHub API token")
    parser.add_argument("--openai-token", required=True, help="OpenAI API token")
    parser.add_argument("--repo", required=True, help="The GitHub repository to look at")
    parser.add_argument("--debug", required=False, help="Prints debug output if set")
    args = parser.parse_args()

    messages.append({"role": "user", "content": args.prompt})

    while True:
        openai_response = query_openai(args.openai_token, messages)
        print_debug(args, f"Raw OpenAI response: {openai_response}")

        # Check if OpenAI is requesting a function call
        if openai_response.function_call is not None:
            function_output, function_name = handle_function_call(openai_response.function_call, args.repo, args.github_token)

            # Only append function output if it's not None
            if function_output is not None:
                print_debug(args, f"Function called: {function_name}")
                print_debug(args, f"Function output: {function_output}")

                messages.append({"role": "function", "name": function_name, "content": function_output})
            else:
                print_debug(args, f"Function '{function_name}' returned None. Skipping function response.")
                break # Not sure how to handle it (yet) :)

            # Append the function result to messages and continue the loop
            messages.append({"role": "function", "name": function_name, "content": function_output})
        else:
            # If no function call, OpenAI has provided a final answer, so we break the loop
            print_debug(args, f"Final AI Response: {openai_response.content}")
            print(openai_response.content)
            break

def print_debug(args, message):
    if args.debug:
        print(message)

if __name__ == "__main__":
    main()
