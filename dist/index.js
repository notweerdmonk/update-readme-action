/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ 809:
/***/ ((module) => {

module.exports = eval("require")("@actions/core");


/***/ }),

/***/ 34:
/***/ ((module) => {

module.exports = eval("require")("@actions/github");


/***/ }),

/***/ 885:
/***/ ((module) => {

module.exports = eval("require")("@octokit/rest");


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __nccwpck_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		var threw = true;
/******/ 		try {
/******/ 			__webpack_modules__[moduleId](module, module.exports, __nccwpck_require__);
/******/ 			threw = false;
/******/ 		} finally {
/******/ 			if(threw) delete __webpack_module_cache__[moduleId];
/******/ 		}
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat */
/******/ 	
/******/ 	if (typeof __nccwpck_require__ !== 'undefined') __nccwpck_require__.ab = __dirname + "/";
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
const { Octokit } = __nccwpck_require__(885);
const core = __nccwpck_require__(809);
const github = __nccwpck_require__(34);

async function getRecentRepos(username, token) {
  const octokit = new Octokit({ auth: token });
  const repos = await octokit.repos.listForUser({
    username,
    sort: 'updated',
    direction: 'desc'
  });
  return repos.data.slice(0, 4);
}

async function updateReadme(owner, repo, content, token) {
  const octokit = new Octokit({ auth: token });

  try {
    const { data: readme } = await octokit.repos.getContent({
      owner: owner,
      repo: repo,
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
      owner: owner,
      repo: repo,
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

    const { owner, repo } = github.context.repo;

    const repos = await getRecentRepos(username, token);

    let featuredReposContent = '';
    for (const repo of repos) {
      featuredReposContent += `### [${repo.name}](${repo.html_url})\n\n${repo.description || 'No description'}\n\nUpdated at ${repo.updated_at}\n\n`;
    }

    await updateReadme(owner, repo, featuredReposContent, token);
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();

})();

module.exports = __webpack_exports__;
/******/ })()
;