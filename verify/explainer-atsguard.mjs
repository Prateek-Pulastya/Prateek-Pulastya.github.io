import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const i = h.indexOf('>ATSGuard<'); if (i < 0) fail('ATSGuard card not found');
const seg = h.slice(i - 400, i + 2600);
if (!/class="explainer"[\s\S]*?data-steps="5"/.test(seg)) fail('ATSGuard explainer (5 steps) missing');
for (const label of ['styling', 'normalise', 'allow', 'flag', 'block'])
  if (!seg.toLowerCase().includes(label)) fail(`ATSGuard step label "${label}" missing`);
console.log('PASS');
