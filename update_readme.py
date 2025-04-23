import os, sys
from github import Github

"""
It is advisable to keep the repos section towards the end of the document.
"""


class ReadmeUpdater(object):

    @staticmethod
    def github(gh_token):
        return Github(gh_token)

    @staticmethod
    def get_config():
        return {
            "gh_token": os.getenv("GITHUB_TOKEN", None),
            "nrecent": int(os.getenv("NUM_RECENT", 4))
        }

    def get_repo(self, github):
        repo_path = os.getenv("GITHUB_REPOSITORY")
        return {
            "repo_path": repo_path,
            "repo_name": os.path.basename(repo_path),
            }

    @staticmethod
    def get_user(github, username=None):
        # Authenticated user
        if username is not None and len(username) > 0:
            return github.get_user(login=username)
        return github.get_user()

    def __init__(self, username = None, gh_token = None, repo_path = None, nrecent = 5):
        self.config = ReadmeUpdater.get_config()

        if gh_token is not None and len(gh_token) > 0:
            self.gh_token = gh_token
        else:
            self.gh_token = self.config["gh_token"]

        if self.gh_token is None or len(self.gh_token) == 0:
            print("Could not find Github token")
            sys.exit(1)

        self.username = username

        self.github = ReadmeUpdater.github(self.gh_token)
        self.user = ReadmeUpdater.get_user(self.github, self.username)

        if repo_path is not None and len(repo_path) > 0:
            self.repo_path = repo_path
            self.repo_name = os.path.basename(repo_path)
        else:
            repo = self.get_repo(self.github)
            self.repo_path = repo["repo_path"]
            self.repo_name = repo["repo_name"]

        self.repo = self.user.get_repo(self.repo_name)

        if nrecent > 0:
            self.nrecent = nrecent
        else:
            self.nrecent = self.config["NRECENT"]

    def make_readme(self, type="public", sort="updated", direction="desc"):
        if file is None:
            return

        repo_list = self.get_repo_list(type, sort, direction)

        readme_content = file.decoded_content.decode("utf-8")

        start_marker = "<!-- Featured Repositories Start -->"
        end_marker = "<!-- Featured Repositories End -->"
        start_index = readme_content.find(start_marker)
        end_index = readme_content.find(end_marker)

        if start_index != -1 and end_index != -1:
            new_readme_content = (
                readme_content[: start_index + len(start_marker)]
                + "\n"
                + repo_list
                + "\n"
                + readme_content[end_index:]
            )
        else:
            # If "Featured Repositories" section is not found,
            # update entire README content
            new_readme_content = (
                    f"{readme_content}\n{start_marker}\n"
                    f"### Featured Repositories\n{repo_list}\n{end_marker}"
                )

        return new_readme_content

    def get_repo_list(self, type="public", sort="updated", direction="desc"):
        repos = \
            self.user.get_repos(type=type, sort=sort, direction=direction)

        repo_list = ""
        repo_count = 0
        repo_name = self.repo_name

        for repo in repos:
            name = repo.name
            if name == repo_name:
                continue
            if name == "update-readme-action":
                continue

            if repo_count >= self.nrecent:
                continue

            repo_list += (
                    f"- [{repo.name}]({repo.html_url})\n"
                    f"  - Description: "
                    f"{repo.description or 'No description provided.'}\n"
                )

            repo_count += 1

        return repo_list

    def __call__(self, type="public", sort="updated", direction="desc"):
        dirlist = [file.path for file in self.repo.get_contents("/")]

        if "README.md" not in dirlist:
            print("README.md not found. Skipping update.")
            sys.exit(0)

        readme = self.repo.get_contents("README.md")

        new_readme = self.make_readme(readme, type, sort, direction)

        commit_msg = "Update README.md with featured repositories"

        self.repo.update_file(
                readme.path,
                commit_msg,
                new_readme,
                readme.sha
            )


ReadmeUpdater()()
