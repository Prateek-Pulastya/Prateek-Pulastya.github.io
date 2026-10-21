# Portfolio Redesign + Motion Graphics — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the single-file portfolio around an attacker↔defender narrative with three scroll-driven "explainer" animations for the flagship projects, preserving all content, honesty, accessibility, and self-containment.

**Architecture:** All shipped changes land in one file, `index.html` (inline `<style>`, body markup, inline `<script>`), matching the site's established single-file pattern. A small motion layer (IntersectionObserver arm + rAF scroll-progress + a reduced-motion guard) drives inline-SVG schematic explainers that are complete static labelled diagrams by default and only animate when JS + motion are allowed. Verification is script-driven (`verify/*.mjs` on the HTML source) plus browser-pane probes for rendered state.

**Tech Stack:** Vanilla HTML/CSS/JS, inline SVG, IntersectionObserver, `requestAnimationFrame`. Fonts: Space Grotesk + JetBrains Mono (Google Fonts, already loaded). No external JS libraries. Node (for `verify/*.mjs`), Python `http.server` + the built-in browser pane for rendered checks.

**Spec:** `F:/Claude/portfolio-redesign-motion-spec-2026-10-21.md` (to be copied into the repo's `docs/` on the build branch).

## Global Constraints

- **Single file:** every shipped change is in `index.html`. No external JS/CSS libraries; no third-party widgets. Same-origin committed assets only.
- **Tokens (verbatim, AA-verified on `--bg #0a0b0d`):** `--defend:#5fd39a` (10.6:1); attacker-red `--attack:#ef7a63` (7.16:1, text/accents) and `--attack-fill:#e5664d` (5.94:1, fills/borders). One colour = one meaning: red only on attacker-side elements.
- **Keep:** `--bg #0a0b0d`, `--panel #0f1216`/surface tokens, `--ink #e9ecef`, `--muted #7d8794`, Space Grotesk + JetBrains Mono.
- **Fail-safe default:** content is visible/complete without JS. Hidden/animated states engage only under `html.anim` (set when IntersectionObserver exists AND `matchMedia('(prefers-reduced-motion: reduce)')` is false), mirroring the site's existing reveal pattern.
- **Accessibility:** `prefers-reduced-motion: reduce` → no motion, full static diagrams; keyboard + `:focus-visible` intact; skip link intact; attacker/defender distinguished by position + text label + icon, never colour alone.
- **Preserve functional pieces:** Tier-1 interactive demo, command palette (⌘K + mobile FAB), light/dark toggle, auto feeds (`data/repos.json`, `data/blog.json`) + Actions, the held `<template id="card-ai-redteam-workbench">`.
- **No new/changed claims:** every number stays real and matches the repos.
- **No horizontal overflow** at any width 320–1440px. **No console errors.**
- **Verification tooling:** `verify/<task>.mjs` run with `node verify/<task>.mjs` prints `PASS` (exit 0) or `FAIL: <reason>` (exit 1). Rendered/motion checks run by serving `python -m http.server 8830` and probing via the built-in browser pane; each such step names the exact Expected observation. `verify/` is not served content and does not affect the deployed site.
- **Branch:** work on branch `redesign` in a clone of `prateek-pulastya.github.io`; `main` stays live. Deploy (merge/push to `main`) happens only in Task 7 and is a stop-and-confirm step.

## Review Focus

Input classes / failure modes the spec implies that task tests must pin:
1. **Reduced-motion**: with `prefers-reduced-motion: reduce`, every explainer shows all steps + numbers statically and nothing animates. → pinned in Tasks 4–6.
2. **No-JS / failed observer**: with JS disabled, hero, Proof, and all explainers render complete and legible (no blank sections, no scroll-gated meaning). → pinned in Tasks 2, 4–6.
3. **Mobile 320–375px**: hero split stacks (attacker above / defender below), explainers reflow vertical, no horizontal overflow. → pinned in Tasks 2, 4–6.
4. **Colour-blind**: attacker vs defender is readable with colour removed (position + `BLOCK`/`PASS` label + icon present in DOM). → pinned in Tasks 2, 4.
5. **Regression of existing features**: command palette (⌘K + FAB), Tier-1 demo, light/dark toggle, and both feeds still work after the restyle. → pinned in Task 3.

---

## Task 1: Design tokens + motion scaffolding (P0, no visible change)

**Files:**
- Modify: `index.html` (`:root` token block in `<style>`; new inline `<script>` motion-util block before the closing `</body>`).
- Create: `verify/tokens.mjs`

**Interfaces:**
- Produces (global JS, consumed by Tasks 4–6):
  - `window.MOTION_OK` — boolean: `('IntersectionObserver' in window) && !matchMedia('(prefers-reduced-motion: reduce)').matches`.
  - `window.armOnEnter(el, cb)` — calls `cb()` once when `el` first intersects (IntersectionObserver, `rootMargin:'0px 0px -40px 0px'`); if `!MOTION_OK`, does nothing.
  - `window.scrollProgress(el)` — returns a clamped 0..1 number: how far `el` has travelled through the viewport (`(vh - top) / (vh + height)` clamped). Pure, no side effects.
  - `window.onScroll(fn)` — registers `fn` to run on scroll, rAF-throttled (one rAF in flight max).
- Consumes: nothing.

- [ ] **Step 1: Write the failing check** — `verify/tokens.mjs`

```js
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/tokens.mjs`
Expected: `FAIL: --attack token missing` (tokens/utilities not added yet).

- [ ] **Step 3: Add tokens** — in the `:root` block add `--attack:#ef7a63; --attack-fill:#e5664d; --defend:#5fd39a;` (green may already exist as `--accent`; add `--defend` as the semantic alias). Add light-mode overrides under the existing light-theme block (darkened reds/greens; values computed to keep ≥4.5:1 on the light surface — compute with the same `ratio` helper and record the chosen hexes in a code comment).

- [ ] **Step 4: Add motion utilities** — new inline `<script>` before `</body>`, after existing scripts:

```html
<script>
(function () {
  "use strict";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.MOTION_OK = ("IntersectionObserver" in window) && !reduce;
  if (window.MOTION_OK) document.documentElement.classList.add("anim");
  window.armOnEnter = function armOnEnter(el, cb) {
    if (!window.MOTION_OK || !el) return;
    var done = false;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting && !done) { done = true; io.disconnect(); cb(); } });
    }, { rootMargin: "0px 0px -40px 0px", threshold: 0 });
    io.observe(el);
  };
  window.scrollProgress = function scrollProgress(el) {
    if (!el) return 0;
    var r = el.getBoundingClientRect(), vh = window.innerHeight || 1;
    var p = (vh - r.top) / (vh + r.height);
    return p < 0 ? 0 : p > 1 ? 1 : p;
  };
  window.onScroll = function onScroll(fn) {
    var tick = false;
    window.addEventListener("scroll", function () {
      if (tick) return; tick = true;
      requestAnimationFrame(function () { tick = false; fn(); });
    }, { passive: true });
  };
})();
</script>
```

- [ ] **Step 5: Run the check to verify it passes**

Run: `node verify/tokens.mjs`
Expected: `PASS`.

- [ ] **Step 6: Browser verify — no visible change, no errors**

Serve (`python -m http.server 8830`), open `http://127.0.0.1:8830/` in the browser pane. Probe:
`JSON.stringify({motionOk: window.MOTION_OK, hasArm: typeof window.armOnEnter, cards: document.querySelectorAll('#work .grid-projects .card').length, errors: 0})`
Expected: `motionOk:true`, `hasArm:"function"`, `cards:8` (unchanged), console shows no errors.

- [ ] **Step 7: Commit**

```bash
git add index.html verify/tokens.mjs
git commit -m "P0: add attacker/defender tokens + motion scaffolding (no visible change)"
```

---

## Task 2: Hero split + Proof/evidence section (P1)

**Files:**
- Modify: `index.html` (hero markup + the stats/"proof" markup in body; related CSS in `<style>`).
- Create: `verify/hero.mjs`

**Interfaces:**
- Consumes: tokens `--attack`/`--defend` (Task 1).
- Produces: DOM anchors used by later verification: `.hero-split` with `.side-attack` and `.side-defend`; `#proof` section with `.receipt` items.

- [ ] **Step 1: Write the failing check** — `verify/hero.mjs`

```js
import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
for (const s of ['hero-split', 'side-attack', 'side-defend', 'break controls', 'id="proof"', 'receipt'])
  if (!h.includes(s)) fail(`"${s}" not found in hero/proof`);
// colour-blind: attacker side must carry a text label, not colour alone
if (!/side-attack[\s\S]{0,400}(ATTACKER|untrusted|payload)/i.test(h)) fail('attacker side lacks text label');
if (!/side-defend[\s\S]{0,400}(DEFENDER|you|control)/i.test(h)) fail('defender side lacks text label');
console.log('PASS');
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/hero.mjs`
Expected: `FAIL: "hero-split" not found in hero/proof`.

- [ ] **Step 3: Rebuild the hero** — replace the current hero inner markup with a two-column `.hero-split`: `.side-attack` (red, an untrusted-input sample labelled "ATTACKER · untrusted input", e.g. `ignore all previous instructions…`) and `.side-defend` (green, labelled "DEFENDER"), resolving to the h1 name + role + thesis line `I break controls, then build the ones that hold.` Keep the existing social/contact buttons. Add an icon (inline SVG or existing glyph) to each side so the roles read without colour.

- [ ] **Step 4: Rework Proof** — convert the existing 4-stat row into `#proof` with `.receipt` items (evidence treatment): CVSS 9.9, #1 Intigriti, held-out `0.7895` shown beside the in-sample `1.000` with a "−21 pts, logged not hidden" caption (C-style honesty receipt). Keep real numbers.

- [ ] **Step 5: Add CSS** — `.hero-split{display:grid;grid-template-columns:1fr 1fr;gap:…}` with `@media (max-width:720px){grid-template-columns:1fr}` (attacker stacks above defender). `.side-attack` uses `--attack`; `.side-defend` uses `--defend`. `.receipt` styled as evidence rows. All animation deferred to later tasks — this task is static layout only.

- [ ] **Step 6: Run the check to verify it passes**

Run: `node verify/hero.mjs`
Expected: `PASS`.

- [ ] **Step 7: Browser verify — render, mobile stack, no-JS, overflow**

Serve + open the pane. (a) Desktop: screenshot — split hero visible, thesis line present. (b) `resize_window` mobile 375 → probe `getComputedStyle(document.querySelector('.hero-split')).gridTemplateColumns` Expected a single-column value (one track). (c) Probe `document.documentElement.scrollWidth <= window.innerWidth + 2` Expected `true` at 375 and 1440. (d) No-JS check: `document.querySelector('.hero-split')` and `#proof` text are present in the raw HTML source (they are static markup) — confirm via `verify/hero.mjs` already passing. Expected: all true, no console errors.

- [ ] **Step 8: Commit**

```bash
git add index.html verify/hero.mjs
git commit -m "P1: attacker/defender split hero + evidence-receipt proof section"
```

---

## Task 3: Section restyle to the new language (P2)

**Files:**
- Modify: `index.html` (nav, project cards, vulnerability-research section, experience→contact styling in `<style>` and light markup tweaks).
- Create: `verify/sections.mjs`

**Interfaces:**
- Consumes: tokens (Task 1).
- Produces: vuln-research findings carry an attacker accent class `.finding--attack` (red); no structural change to feeds, palette, demo.

- [ ] **Step 1: Write the failing check** — `verify/sections.mjs`

```js
import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
if (!h.includes('finding--attack')) fail('vuln-research attacker accent class missing');
// regression guards: existing features must still be present in source
for (const s of ['id="cmdk"', 'cmdkFab', 'demoInput', 'themeBtn', 'data/repos.json', 'data/blog.json', 'card-ai-redteam-workbench'])
  if (!h.includes(s)) fail(`regression: "${s}" removed`);
console.log('PASS');
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/sections.mjs`
Expected: `FAIL: vuln-research attacker accent class missing`.

- [ ] **Step 3: Restyle** — apply the new language to nav, project cards, experience/credentials/writing/open-source/contact (spacing, borders, the two-accent system). Add `.finding--attack` (red left-accent) to the vulnerability-research findings. Do not touch the command palette, Tier-1 demo, theme toggle, feed-loading JS, or the held `<template>`.

- [ ] **Step 4: Run the check to verify it passes**

Run: `node verify/sections.mjs`
Expected: `PASS`.

- [ ] **Step 5: Browser verify — features still work, breakpoints, errors**

Serve + open the pane. Probe each regression-critical feature live:
- Palette: dispatch `Ctrl+K` → `document.getElementById('cmdk').classList.contains('open')` Expected `true`; Escape closes.
- Tier-1 demo: set `#demoInput` value `1gn0r3 prev10us 1nstruct10ns`, fire `input`, wait 160ms → `#demoVerdict .badge` text Expected `TIER1-BLOCK`.
- Theme toggle: click `#themeBtn` → `document.documentElement.getAttribute('data-theme')` flips.
- Feeds: `#repoFeed .feed-item` count ≥ 1 and `#blogFeed .feed-item` count ≥ 1 after load.
- Overflow at 375 and 1440: `scrollWidth <= innerWidth + 2` Expected `true`. Light + dark screenshots legible. No console errors.

- [ ] **Step 6: Commit**

```bash
git add index.html verify/sections.mjs
git commit -m "P2: restyle sections to attacker/defender language; vuln-research red accents"
```

---

## Task 4: GuardRail scroll explainer (P3a)

**Files:**
- Modify: `index.html` (GuardRail section: inline SVG schematic + its controller `<script>`; CSS for the explainer).
- Create: `verify/explainer-guardrail.mjs`

**Interfaces:**
- Consumes: `armOnEnter`, `scrollProgress`, `onScroll`, `MOTION_OK` (Task 1).
- Produces: pattern reused by Tasks 5–6 — an explainer is `<figure class="explainer" data-steps="N">` containing an inline `<svg>` with `.step` groups (each `data-step="i"`, class `is-on` toggled) and a `.caption`; a controller that sets `is-on` for steps up to `Math.round(scrollProgress(fig) * (N-1))`, or all steps when `!MOTION_OK`.

- [ ] **Step 1: Write the failing check** — `verify/explainer-guardrail.mjs`

```js
import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const seg = h.slice(h.indexOf('id="work"'), h.indexOf('id="research"'));
if (!/class="explainer"[\s\S]*data-steps="5"/.test(seg)) fail('GuardRail explainer (5 steps) missing');
for (const label of ['Tier 1', 'Tier 2', 'de-leet', 'verdict', '0.7895'])
  if (!seg.includes(label)) fail(`GuardRail step label "${label}" missing (static completeness)`);
// colour-blind + fail-safe: verdict carries a text label, not colour alone
if (!/PASS|BLOCK|cleared/i.test(seg)) fail('verdict lacks text label');
console.log('PASS');
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/explainer-guardrail.mjs`
Expected: `FAIL: GuardRail explainer (5 steps) missing`.

- [ ] **Step 3: Add the static SVG explainer FIRST** — in the GuardRail feature, add `<figure class="explainer" data-steps="5">` with an inline terminal/schematic `<svg>`: five `.step` groups — ① payload enters (red), ② Tier-1 normalise + Aho-Corasick/regex, ③ de-leet + separator-strip pass, ④ Tier-2 DeBERTa monitor-only, ⑤ verdict (green, text `PASS → Tier 2` / blocked path labelled) + receipt text `held-out 0.7895 · p50 0.14 ms`. All five steps + all labels are rendered and visible by default (no `is-on` dependency for visibility; `is-on` only adds the motion emphasis). Keep it above the existing Tier-1 interactive demo (architecture → then try it).

- [ ] **Step 4: Add the controller** — a `<script>` that, for this figure: if `!MOTION_OK`, add `is-on` to every `.step` and stop. Else, set the default to step 0 lit, then `onScroll(function(){ var n=Math.round(scrollProgress(fig)*(5-1)); steps.forEach(function(s,i){ s.classList.toggle('is-on', i<=n); }); caption.textContent = CAPTIONS[n]; });` with `CAPTIONS` = the five real step captions. `armOnEnter(fig, …)` may kick an initial paint. Motion = CSS transition on `.step.is-on` (opacity/transform of the travelling packet), transform/opacity only.

- [ ] **Step 5: Run the check to verify it passes**

Run: `node verify/explainer-guardrail.mjs`
Expected: `PASS`.

- [ ] **Step 6: Browser verify — reduced-motion, no-JS, scroll-driven, mobile**

Serve + open the pane.
- **Reduced-motion:** `resize_window colorScheme/dark` is unrelated; emulate reduced motion by probing the fallback path — set `window.MOTION_OK=false` is not reliable post-load, so instead verify the static completeness: with motion on, probe that every `.step` text is present in the DOM and the figure height > 0. Then reload with the pane's reduced-motion emulation (if available) OR assert via source that `!MOTION_OK` lights all steps (code path in Step 4). Expected: all five step labels + `0.7895` present and visible; no step is `display:none`.
- **Scroll-driven:** scroll the figure through the viewport; probe the lit-step count increases monotonically and the caption text changes. Expected: step count goes 1→5 as it scrolls; no console errors; `scrollWidth<=innerWidth+2` at 375.
- Screenshot desktop + 375.

- [ ] **Step 7: Commit**

```bash
git add index.html verify/explainer-guardrail.mjs
git commit -m "P3a: GuardRail scroll explainer (static-complete, motion-on-scroll)"
```

---

## Task 5: ATSGuard scroll explainer (P3b)

**Files:**
- Modify: `index.html` (ATSGuard card/section: inline SVG explainer + controller).
- Create: `verify/explainer-atsguard.mjs`

**Interfaces:**
- Consumes: the Task 4 pattern (`class="explainer" data-steps`, `.step`/`.is-on`/`.caption`, `armOnEnter`/`scrollProgress`/`onScroll`/`MOTION_OK`).
- Produces: nothing new.

- [ ] **Step 1: Write the failing check** — `verify/explainer-atsguard.mjs`

```js
import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const i = h.indexOf('>ATSGuard<'); if (i < 0) fail('ATSGuard card not found');
const seg = h.slice(i - 400, i + 2600);
if (!/class="explainer"[\s\S]*data-steps="5"/.test(seg)) fail('ATSGuard explainer (5 steps) missing');
for (const label of ['styling', 'normalise', 'allow', 'flag', 'block'])
  if (!seg.toLowerCase().includes(label)) fail(`ATSGuard step label "${label}" missing`);
console.log('PASS');
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/explainer-atsguard.mjs`
Expected: `FAIL: ATSGuard explainer (5 steps) missing`.

- [ ] **Step 3: Add the static SVG explainer** — five steps: ① résumé with hidden instruction (red) → ② read styling, not just text → ③ normalise (Unicode/homoglyph/leet) → ④ detect + route `allow / flag / block` (labels present) → ⑤ receipt `0% FP · held-out reported honestly`. Static-complete by default.

- [ ] **Step 4: Add the controller** — identical pattern to Task 4 (reuse the same step/caption mechanism against this figure; captions are ATSGuard's five). `!MOTION_OK` lights all steps.

- [ ] **Step 5: Run the check to verify it passes**

Run: `node verify/explainer-atsguard.mjs`
Expected: `PASS`.

- [ ] **Step 6: Browser verify** — same checklist as Task 4 Step 6 against the ATSGuard figure: static completeness (all 5 labels visible), scroll lights steps 1→5, caption changes, no overflow at 375, no console errors.

- [ ] **Step 7: Commit**

```bash
git add index.html verify/explainer-atsguard.mjs
git commit -m "P3b: ATSGuard scroll explainer"
```

---

## Task 6: cloudfracture scroll explainer (P3c)

**Files:**
- Modify: `index.html` (CloudFracture card/section: inline SVG explainer + controller).
- Create: `verify/explainer-cloudfracture.mjs`

**Interfaces:**
- Consumes: the Task 4 pattern.
- Produces: nothing new.

- [ ] **Step 1: Write the failing check** — `verify/explainer-cloudfracture.mjs`

```js
import { readFileSync } from 'node:fs';
const h = readFileSync('index.html', 'utf8');
const fail = m => { console.log('FAIL: ' + m); process.exit(1); };
const i = h.indexOf('>CloudFracture<'); if (i < 0) fail('CloudFracture card not found');
const seg = h.slice(i - 400, i + 2600);
if (!/class="explainer"[\s\S]*data-steps="4"/.test(seg)) fail('CloudFracture explainer (4 steps) missing');
for (const label of ['attack', 'detect', 'remediate', 'least-privilege'])
  if (!seg.toLowerCase().includes(label)) fail(`CloudFracture step label "${label}" missing`);
console.log('PASS');
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node verify/explainer-cloudfracture.mjs`
Expected: `FAIL: CloudFracture explainer (4 steps) missing`.

- [ ] **Step 3: Add the static SVG explainer** — four steps: ① IAM attack path (red) → ② Sigma detection fires → ③ remediate to least-privilege → ④ receipt `attack now fails · AppSec CI`. The attack→detect→remediate loop reads left→right; static-complete.

- [ ] **Step 4: Add the controller** — same pattern, `data-steps="4"`, four captions; `!MOTION_OK` lights all.

- [ ] **Step 5: Run the check to verify it passes**

Run: `node verify/explainer-cloudfracture.mjs`
Expected: `PASS`.

- [ ] **Step 6: Browser verify** — same checklist as Task 4 Step 6 against the CloudFracture figure.

- [ ] **Step 7: Commit**

```bash
git add index.html verify/explainer-cloudfracture.mjs
git commit -m "P3c: CloudFracture scroll explainer"
```

---

## Task 7: Full verification sweep + deploy (P4)

**Files:**
- Create: `verify/all.mjs` (runs tokens/hero/sections/explainer checks in sequence).
- Modify: none (fixes only if the sweep finds a defect).

**Interfaces:**
- Consumes: all prior `verify/*.mjs`.
- Produces: the deploy.

- [ ] **Step 1: Write `verify/all.mjs`**

```js
import { execSync } from 'node:child_process';
const files = ['tokens','hero','sections','explainer-guardrail','explainer-atsguard','explainer-cloudfracture'];
for (const f of files) {
  try { execSync(`node verify/${f}.mjs`, { stdio: 'inherit' }); }
  catch { console.log(`FAIL: verify/${f}.mjs`); process.exit(1); }
}
console.log('ALL PASS');
```

- [ ] **Step 2: Run the full source sweep**

Run: `node verify/all.mjs`
Expected: `ALL PASS`.

- [ ] **Step 3: Full browser acceptance sweep** — serve + pane. Run every acceptance criterion from the spec §8: desktop + 375 render in light + dark; `prefers-reduced-motion` emulation on → no motion, all explainers fully static/legible; keyboard + `:focus-visible` + skip link + palette + Tier-1 demo + both feeds work; `node`-free contrast already covered; `scrollWidth<=innerWidth+2` across 320/375/768/1024/1440; JS-disabled render retains all content + numbers; **no console errors** anywhere. Record each as pass/observation. Fix any failure via the owning task's RED→GREEN before proceeding (re-run its `verify/*.mjs`).

- [ ] **Step 4: Honesty audit** — diff the rendered numbers against the repos: held-out 0.7895, CVSS 9.9, #1 Intigriti, ATSGuard 0% FP, cloudfracture claims. Expected: every number matches its repo; no inflated claim introduced.

- [ ] **Step 5: STOP — confirm deploy** — pushing to `main` publishes to the live public site. Present a before/after screenshot set and the `verify/all.mjs` result; get explicit confirmation to merge/push. (This is the plan's one mandatory stop.)

- [ ] **Step 6: Deploy** — on confirmation: merge `redesign` → `main` and push; poll the live URL until the new markup is served; verify the live site once more (no console errors, explainers present, reduced-motion fallback intact).

```bash
git add verify/all.mjs
git commit -m "P4: full verification sweep harness"
# after explicit confirmation:
# git checkout main && git merge --no-ff redesign && git push origin main
```

---

## Self-review

**1. Spec coverage:** tokens/motion principles → T1; hero split + Proof receipts → T2; section language + vuln-research red → T3; three explainers (mechanics, step scripts, fail-safe, mobile) → T4–T6; verification bar + honesty audit + deploy → T7. Preserved-features constraint → pinned in T3 regression guard. No spec section is unimplemented.

**2. Placeholder scan:** every step has real check code or concrete markup/CSS instructions with exact token values, labels, and numbers. Light-mode variant hexes are computed in T1 Step 3 with the same `ratio` helper (not "TBD"). No "handle edge cases"/"add validation" placeholders.

**3. Type/interface consistency:** `MOTION_OK`, `armOnEnter`, `scrollProgress`, `onScroll` defined in T1 and consumed by name in T4–T6; the explainer DOM contract (`class="explainer" data-steps`, `.step`/`.is-on`/`.caption`) is defined in T4 Produces and reused verbatim in T5/T6.

**4. Review Focus coverage:** reduced-motion (T4–6 Step 6), no-JS (T2 Step 7, T4–6 static-complete checks), mobile 320–375 (T2/T4–6 overflow probes), colour-blind labels (T2/T4 checks), feature regression (T3 Step 5). All five pinned.
