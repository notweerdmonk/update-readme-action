import os
import sys
from github import Github

"""
It is advisable to keep the repos section towards the end of the document.
"""

# Initialize GitHub API
github_token = os.getenv('GITHUB_TOKEN')
g = Github(github_token)

# Update README function
def update_readme():
    # Check if README.md exists in the repository
    if 'README.md' not in os.listdir():
        print("README.md not found. Skipping update.")
        return

    user = g.get_user()  # Get authenticated user
    repos = user.get_repos(sort="updated", direction="desc")[:4]  # Get latest 4 repositories

    # Generate repository list
    repo_list = ""
    for repo in repos:
        repo_list += f"- [{repo.name}]({repo.html_url})\n  - Description: {repo.description or 'No description provided.'}\n"

    # Read existing README.md
    with open('README.md', 'r') as readme_file:
        readme_content = readme_file.read()

    # Find index of "Featured Repositories" section
    start_marker = "<!-- Featured Repositories Start -->"
    end_marker = "<!-- Featured Repositories End -->"
    start_index = readme_content.find(start_marker)
    end_index = readme_content.find(end_marker)

    # Update repository list under "Featured Repositories" section
    if start_index != -1 and end_index != -1:
        new_readme_content = readme_content[:start_index + len(start_marker)] + "\n" + repo_list + "\n" + readme_content[end_index:]
        #new_readme_content = start_marker + "\n" + repo_list + "\n" + readme_content[end_index:]
    else:
        # If "Featured Repositories" section is not found, update entire README content
        new_readme_content = f"{readme_content}\n{start_marker}\n### Featured Repositories\n{repo_list}\n{end_marker}"
        ##new_readme_content = f"{start_marker}\n### Featured Repositories\n{repo_list}\n{end_marker}"

    # Update README.md
    with open('README.md', 'w') as readme_file:
        #if start_index != -1:
        #    readme_file.seek(start_index, 0)
        #else:
        #    readme_file.seek(0, 2)
        readme_file.write(new_readme_content)

# Execute update README function
update_readme()
