import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const seg = h.slice(h.indexOf('id="work"'), h.indexOf('id="research"'));
if (!/class="explainer"[\s\S]*?data-steps="5"/.test(seg)) fail('GuardRail explainer (5 steps) missing');
for (const label of ['Tier 1', 'Tier 2', 'de-leet', 'verdict', '0.7895'])
  if (!seg.includes(label)) fail(`GuardRail step label "${label}" missing (static completeness)`);
if (!/PASS|BLOCK|cleared/i.test(seg)) fail('verdict lacks text label');
console.log('PASS');
