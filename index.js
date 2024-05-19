const { Octokit } = require("@octokit/rest");
const core = require('@actions/core');
const github = require('@actions/github');

async function getRecentRepos(username, token) {
  const octokit = new Octokit({ auth: token });
  const repos = await octokit.repos.listForUser({
    username,
    sort: 'updated',
    direction: 'desc'
  });
  return repos.data.slice(0, 4);
}

async function updateReadme(repo, content, token) {
  const octokit = new Octokit({ auth: token });

  try {
    const { data: readme } = await octokit.repos.getContent({
      owner: repo.owner.login,
      repo: repo.name,
      path: 'README.md'
    });

    const readmeContent = Buffer.from(readme.content, 'base64').toString('utf-8');

    const startMarker = "<!-- Featured Repositories Start -->";
    const endMarker = "<!-- Featured Repositories End -->";
    const startIndex = readmeContent.indexOf(startMarker);
    const endIndex = readmeContent.indexOf(endMarker);

    let newContent;
    if (startIndex !== -1 && endIndex !== -1) {
      const before = readmeContent.substring(0, startIndex + startMarker.length);
      const after = readmeContent.substring(endIndex);
      newContent = `${before}\n${content}\n${after}`;
    } else {
      newContent = `${readmeContent}\n${startMarker}\n${content}\n${endMarker}`;
    }

    const sha = readme.sha;

    await octokit.repos.createOrUpdateFileContents({
      owner: repo.owner.login,
      repo: repo.name,
      path: 'README.md',
      message: 'Update README.md with featured repositories',
      content: Buffer.from(newContent).toString('base64'),
      sha
    });
  } catch (error) {
    if (error.status === 404) {
      console.log(`README.md does not exist in ${repo.name}`);
    } else {
      throw error;
    }
  }
}

async function main() {
  try {
    const username = core.getInput('username');
    const token = core.getInput('github_token');

    const repos = await getRecentRepos(username, token);

    let featuredReposContent = '';
    for (const repo of repos) {
      featuredReposContent += `### [${repo.name}](${repo.html_url})\n\n${repo.description || 'No description'}\n\nUpdated at ${repo.updated_at}\n\n`;
    }

    for (const repo of repos) {
      await updateReadme(repo, featuredReposContent, token);
    }
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
