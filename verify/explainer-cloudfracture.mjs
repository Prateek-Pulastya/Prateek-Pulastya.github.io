import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const i = h.indexOf('>CloudFracture<'); if (i < 0) fail('CloudFracture card not found');
const seg = h.slice(i - 400, i + 2600);
if (!/class="explainer"[\s\S]*?data-steps="4"/.test(seg)) fail('CloudFracture explainer (4 steps) missing');
for (const label of ['attack', 'detect', 'remediate', 'least-privilege'])
  if (!seg.toLowerCase().includes(label)) fail(`CloudFracture step label "${label}" missing`);
console.log('PASS');
