const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const fs = require('fs');

async function fetchLeetcodeStats(username) {
  const url = `https://leetcode.com/${username}/`;
  const response = await axios.get(url);
  const dom = new JSDOM(response.data);
  const statsElem = dom.window.document.querySelectorAll('.total-solved-count')[0];

  if (!statsElem) {
    throw new Error('Could not find stats on LeetCode profile page');
  }

  // Scrape easy, medium, hard counts
  const statLabels = dom.window.document.querySelectorAll('.stat-value');
  if (!statLabels || statLabels.length < 3) {
    throw new Error('Could not parse problem stats');
  }

  const easy = statLabels[0].textContent.trim();
  const medium = statLabels[1].textContent.trim();
  const hard = statLabels[2].textContent.trim();

  return { easy, medium, hard };
}

async function updateReadme() {
  const username = process.env.LEETCODE_USERNAME;
  if (!username) throw new Error('LEETCODE_USERNAME env var missing');

  const stats = await fetchLeetcodeStats(username);

  const readmePath = './README.md';
  const readme = fs.readFileSync(readmePath, 'utf-8');

  const newSection = `<!--START_SECTION:leetcode_stats-->
| Difficulty | Problems Solved |
|------------|-----------------|
| Easy       | ${stats.easy}           |
| Medium     | ${stats.medium}           |
| Hard       | ${stats.hard}           |
<!--END_SECTION:leetcode_stats-->`;

  const updatedReadme = readme.replace(/<!--START_SECTION:leetcode_stats-->[\s\S]*<!--END_SECTION:leetcode_stats-->/, newSection);

  fs.writeFileSync(readmePath, updatedReadme, 'utf-8');
}

updateReadme().catch(err => {
  console.error(err);
  process.exit(1);
});
