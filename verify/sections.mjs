import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
if (!h.includes('finding--attack')) fail('vuln-research attacker accent class missing');
for (const s of ['id="cmdk"', 'cmdkFab', 'demoInput', 'themeBtn', 'data/repos.json', 'data/blog.json', 'card-ai-redteam-workbench'])
  if (!h.includes(s)) fail(`regression: "${s}" removed`);
console.log('PASS');
