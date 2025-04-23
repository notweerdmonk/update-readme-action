import os
import sys
from github import Github

"""
It is advisable to keep the repos section towards the end of the document.
"""

# Initialize GitHub API
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("Could not find Github token")
    sys.exit(1)

NRECENT = int(os.getenv("NUM_RECENT", 4))

g = Github(GITHUB_TOKEN)

# Update README function
def update_readme(nrecent: int = 4):
    this_repo_name = os.path.basename(os.getenv('GITHUB_REPOSITORY'))

    # Check if README.md exists in the repository
    if 'README.md' not in os.listdir():
        print("README.md not found. Skipping update.")
        #sys.exit(0)

    user = g.get_user()  # Get authenticated user
    repos = user.get_repos(type="public", sort="updated", direction="desc")

    # Generate repository list
    repo_list = ""
    repo_count = 0
    for repo in repos:
        if repo.name == this_repo_name:
            continue
        if repo.name == "updated-readme-action":
            continue
        if repo_count >= nrecent:
            continue
        repo_list += f"- [{repo.name}]({repo.html_url})\n  - Description: {repo.description or 'No description provided.'}\n"

    # Read existing README.md
    this_repo = user.get_repo(this_repo_name)
    file = this_repo.get_contents("README.md")

    readme_content = file.decoded_content.decode("utf-8")

    # Find index of "Featured Repositories" section
    start_marker = "<!-- Featured Repositories Start -->"
    end_marker = "<!-- Featured Repositories End -->"
    start_index = readme_content.find(start_marker)
    end_index = readme_content.find(end_marker)

    # Update repository list under "Featured Repositories" section
    if start_index != -1 and end_index != -1:
        new_readme_content = readme_content[:start_index + len(start_marker)] + "\n" + repo_list + "\n" + readme_content[end_index:]
    else:
        # If "Featured Repositories" section is not found, update entire README content
        new_readme_content = f"{readme_content}\n{start_marker}\n### Featured Repositories\n{repo_list}\n{end_marker}"

    # Update README.md
    commit_msg = "Update README.md with featured repositories"

    this_repo.update_file(file.path, commit_msg, new_readme_content, file.sha)

# Execute update README function
update_readme(NRECENT)
