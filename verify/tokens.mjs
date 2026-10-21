import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const lum = x => { x = x.replace('#',''); const v = i => parseInt(x.slice(i,i+2),16)/255;
  const f = c => c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4);
  return 0.2126*f(v(0)) + 0.7152*f(v(2)) + 0.0722*f(v(4)); };
const ratio = (a,b) => { const L=[lum(a),lum(b)].sort((x,y)=>y-x); return (L[0]+0.05)/(L[1]+0.05); };
const bg = '#0a0b0d';
for (const [n,hex,min] of [['--attack','#ef7a63',4.5], ['--attack-fill','#e5664d',4.5], ['--defend','#5fd39a',4.5]]) {
  if (!h.includes(`${n}:`) && !h.includes(`${n} :`)) fail(`${n} token missing`);
  if (ratio(hex, bg) < min) fail(`${n} ${hex} contrast ${ratio(hex,bg).toFixed(2)} < ${min}`);
}
for (const id of ['window.MOTION_OK', 'function armOnEnter', 'function scrollProgress', 'function onScroll'])
  if (!h.includes(id)) fail(`motion util "${id}" missing`);
if (!/prefers-reduced-motion/.test(h)) fail('reduced-motion guard missing');
console.log('PASS');
