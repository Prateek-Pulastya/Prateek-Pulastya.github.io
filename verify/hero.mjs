import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
for (const s of ['hero-split', 'side-attack', 'side-defend', 'break controls', 'id="proof"', 'receipt'])
  if (!h.includes(s)) fail(`"${s}" not found in hero/proof`);
if (!/side-attack[\s\S]{0,500}(ATTACKER|untrusted|payload)/i.test(h)) fail('attacker side lacks text label');
if (!/side-defend[\s\S]{0,500}(DEFENDER|you|control)/i.test(h)) fail('defender side lacks text label');
console.log('PASS');
