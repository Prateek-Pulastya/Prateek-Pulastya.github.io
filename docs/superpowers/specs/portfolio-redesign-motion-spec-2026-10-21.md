# Portfolio Redesign + Motion Graphics — Design Spec

**Date:** 2026-10-21 · **Author:** Prateek Pulastya (with Claude) · **Status:** design approved in brainstorming; awaiting spec review → then writing-plans.
**Repo:** github.com/Prateek-Pulastya/prateek-pulastya.github.io (single-file `index.html`, GitHub Pages).
**Spec home:** `F:/Claude` (user preference overrides the default `docs/superpowers/specs/`); to be copied into the repo's `docs/` on the build branch.

---

## 1. Purpose & north star
Redesign the live portfolio into a distinctive, narrative-led site built around **attacker ↔ defender**, with three scroll-driven "explainer" animations for the flagship projects. North star (user-chosen): **more distinctive + better storytelling**, without losing the site's established brand — the *honest security engineer* (real numbers, held-out metrics, duplicates-shown vuln research).

**Chosen direction:** B + C hybrid — an **Attacker ↔ Defender** narrative spine with **Evidence/receipts** treatment for metrics.

## 2. Non-goals (out of scope)
- No new content/claims; every number stays real and matches the repos.
- No multi-page restructure — single-file `index.html` preserved.
- No external motion libraries (GSAP/Lottie) or third-party widgets.
- No change to the auto-sync pipeline (repos.json / blog.json / Actions).
- Attacker↔defender split is NOT applied site-wide — hero + flagship explainers only.

## 3. Design language & tokens
**Base (keep):** `--bg #0a0b0d`, `--panel #0f1216`, `--ink #e9ecef`, `--muted #7d8794`.
**Two accents — each one meaning (preserves "one colour = one thing"):**
- **Defender green `#5fd39a`** (10.6:1 on bg) — you, your controls, cleared/safe, verdicts.
- **Attacker red `#ef7a63`** (7.16:1 on bg) for text/accents; **`#e5664d`** (5.94:1) for fills/borders — untrusted input, payloads, the threat. Red appears ONLY on attacker-side elements.
- Light-mode variants defined to keep both roles AA (computed at build; green/red darkened for light surfaces).

**Type (keep):** Space Grotesk (display/UI) + JetBrains Mono (code/labels).

**Motion principles:**
- Purposeful only — motion explains, never decorates.
- Scroll-driven + reader-paced; no autoplay loops in content.
- `prefers-reduced-motion: reduce` → fully static, complete labelled diagrams; no motion.
- Mobile → simplified/stacked motion.
- Self-contained: inline SVG + CSS + vanilla JS (IntersectionObserver + rAF-throttled scroll-progress). No external deps.
- **Colourblind-safe:** attacker/defender distinguished by **position (left/right) + label (`BLOCK`/`PASS`) + icon**, never colour alone.

## 4. Layout & narrative structure
**Hero = the split.** Left attacker (red, untrusted input e.g. "ignore all previous instructions…") ↔ right defender (green, you), resolving to name + thesis line **"I break controls, then build the ones that hold."** Mobile: stacks attacker-above → defender-below.

**Page flow (recruiter-conversion order):**
1. Hero (split)
2. **Proof** — evidence receipts (C-style): CVSS 9.9 · #1 Intigriti · held-out **0.79** with the honesty gap shown.
3. **Selected work** — 3 flagships rendered as attack→defense scroll explainers; other projects as cards (incl. the held `<template>` AI Red-Team card until M1).
4. **Vulnerability research** — attacker craft, red-accented; duplicates/informative outcomes shown honestly (unchanged content).
5. Experience → 6. Technical scope → 7. Credentials → 8. Writing (auto feed) → 9. Open source (auto feed) → 10. Contact.
Sections 5–10 stay clean (no split) to avoid device fatigue.

## 5. The three scroll explainers
Flagships: **GuardRail**, **ATSGuard**, **cloudfracture**. Each = inline SVG schematic (terminal/schematic look) + a thin JS controller.

**Mechanic:** IntersectionObserver arms the explainer; scroll-progress through the section (bounding-rect math, rAF-throttled) maps to **discrete labelled steps**; a step caption updates as the reader scrolls. A payload enters (red) → travels the schematic → is caught/handled → honest result (green + evidence receipt).

**Step scripts (indicative):**
- **GuardRail:** ① payload enters → ② Tier-1 normalise + Aho-Corasick/regex scan → ③ de-leet + separator-strip pass → ④ Tier-2 DeBERTa monitor-only → ⑤ verdict + receipt (held-out 0.79, p50 0.14 ms).
- **ATSGuard:** ① résumé w/ hidden instruction → ② read styling (not just text) → ③ normalise (Unicode/homoglyph/leet) → ④ detect + route allow/flag/block → ⑤ receipt (0% FP / honest held-out).
- **cloudfracture:** ① IAM attack path → ② exploit w/ evidence → ③ Sigma detection fires → ④ remediate to least-privilege → ⑤ receipt (attack now fails; AppSec CI).

**Fail-safe (existing `html.anim` pattern):** every explainer is a complete static labelled diagram by default, with all steps + honest numbers visible. Motion only engages when JS + motion allowed. No-JS / reduced-motion / missed-observer → full static diagram; never blank, never scroll-gated to comprehend.

**Mobile:** schematic reflows vertical; simpler motion; still scroll-driven.

**Preserve the Tier-1 interactive demo** — the explainer shows architecture; the demo lets a visitor try it. Both stay.

## 6. Preserved vs changed
**Preserved:** all content + honesty; Tier-1 interactive demo; command palette (⌘K + mobile FAB); light/dark toggle; skip link; semantic headings + focus-visible; auto feeds + Actions; held `<template>` AI Red-Team card; single-file on GitHub Pages; shields.io/committed assets; accessibility baseline.
**Changed:** token layer (attacker-red added); hero → split; Proof → evidence receipts; 3 flagships → scroll explainers; section styling → new language; vuln research red-accented.

## 7. Build phases
- **P0** — branch `redesign`; add token layer + motion scaffolding (IO util, scroll-progress util, reduced-motion guards). No visible change.
- **P1** — hero split + Proof/evidence section.
- **P2** — restyle sections to the new language (nav, cards, vuln-research red accents, experience → contact). No explainers yet.
- **P3** — the 3 scroll explainers, **static fallback first, motion layered after**, one at a time (GuardRail → ATSGuard → cloudfracture).
- **P4** — polish, full verification, deploy to `main`.
Each phase is shippable; `main` stays live throughout; work on a branch.

## 8. Verification (acceptance criteria)
- Renders correctly in the browser pane at **375px + desktop**, **light + dark**.
- `prefers-reduced-motion` → explainers fully legible as **static** diagrams; no motion; no blank sections.
- Keyboard + focus-visible intact; skip link + command palette still work.
- **No console errors**; no external-dependency breakage.
- **AA contrast computed** (not eyeballed) for new red + green on every surface they sit on.
- No horizontal overflow at **320–1440px**.
- JS disabled → all content + numbers present and readable.
- Scroll handler rAF-throttled; transform/opacity-only animation; no visible jank.
- Honesty audit: every number still real and matches the repos.

## 9. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Scroll jank / perf | rAF throttle; animate transform/opacity only; `will-change` sparingly |
| Gimmick fatigue | split confined to hero + explainers; sections 5–10 clean |
| Colourblind legibility | position + labels + icons, never colour alone |
| Reduced-motion blankness | static complete diagram is the default state (fail-safe) |
| Scope creep | phased; explainers one at a time; each phase shippable |
| Mobile scroll-driven complexity | static fallback + simplified motion |
| Single-file size growth | inline SVG kept lean; no raster; reuse tokens |

## 10. Success criteria
A recruiter in 15 seconds grasps the attacker↔defender identity and the honest proof; the three flagships are *understood*, not just listed; the site is unmistakably Prateek's; nothing is slower, broken, or less honest than before; fully accessible (reduced-motion, keyboard, mobile, AA).

## 11. Open items to resolve during build
- Exact light-mode red/green variants (compute AA at build).
- Final step-caption wording per explainer (draft above; refine in P3).
- Whether the Proof receipts reuse the current 4-stat row or a new evidence layout (decide in P1 against the live design).
