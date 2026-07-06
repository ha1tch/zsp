# zsp procedures manual

This is the operational reference for maintaining this site. It's written
from what actually happened building this site the first time: the real
commands, the real mistakes, and the fixes that came out of them. Where a
pitfall cost real time, it's documented here so it doesn't cost time twice.

For what the site *is*, see `README.md`. This document is about *doing
things to it*.

---

## 1. Prerequisites

- Python 3 with the `markdown` package (`pip install markdown`).
- Every source project cloned as a sibling directory of this repo:
  `zentools`, `zen80`, `zenzx`, `zenas`, `zenimate`, `plus3`, `bdf-fonts`
  all need to sit next to `zsp/`, not inside it. `tools/build_site.py`
  resolves `ROOT` as the parent of the repo for exactly this reason.
- For verification (recommended, not strictly required to build):
  Playwright with at least one browser installed (`playwright install
  chromium`), and `ffmpeg`/`ffprobe` if you're touching video assets.

---

## 2. Routine rebuild

Nothing changed except a source project's docs? This is the whole job:

```bash
cd zsp
rm -rf zsp_site dist
python3 tools/build_site.py
```

`rm -rf zsp_site` first is deliberate and safe — `zsp_site/` is pure build
output, including its `assets/` folder (see §6.1 for why that's worth
stating explicitly). If the build prints a `WARNING: <project> has
untracked doc(s)...`, see §3.

---

## 3. Adding a document to an existing project

Dropping a new `.md` file into a project's `docs/` folder does **not**
make it appear on the site. Each project's doc list in the `PROJECTS`
manifest (top of `tools/build_site.py`) is a hand-ordered array, not a
directory scan — that's what lets zenas put `MANUAL.md` first instead of
alphabetically, and it's a deliberate trade-off: curated order over
automatic discovery.

Steps:

1. Add the file to the project's real `docs/` (or `doc/`) folder, as normal.
2. Run `python3 tools/build_site.py`. If the file isn't yet in the
   manifest, you'll see:
   ```
   WARNING: <slug> has untracked doc(s) not in the manifest: <filename> —
   add to PROJECTS['docs'] in tools/build_site.py to publish.
   ```
   This warning exists because it used to fail silently — a doc could sit
   on disk indefinitely without ever reaching the site and nothing would
   say so. Now it's loud.
3. Add the filename to that project's `"docs"` list, in whatever position
   makes sense for the reading order (not necessarily the end).
4. Re-run the build. The warning should be gone, and a new page should
   exist at `zsp_site/projects/<slug>/docs/<slugified-filename>.html`.
5. Spot-check the new page's excerpt (`excerpt()` in `build_site.py` picks
   the first substantial non-badge paragraph) — for very short docs or
   docs that open with a badge/shield row, it can occasionally pick
   something less useful than intended. Read the docs-list card and adjust
   the source doc's opening paragraph if the excerpt reads badly, rather
   than special-casing the excerpt function.

If a project has no `docs/` folder at all (currently just `zen80`), its
manifest entry lists specific root-level files (`README.md`,
`CHANGELOG.md`, etc.) instead. The same untracked-file warning applies to
that fallback case too — it scans whichever directory `docs_dir` points at
(or the project root if `docs_dir` is `None`).

---

## 4. Adding a new project to the corpus

1. Clone the new project as a sibling of `zsp/` (same directory as the
   other six).
2. Read its actual `README.md` — don't invent a tagline or description.
   Every existing project's `"desc"` field is a close paraphrase of real
   text pulled from that project's own README, verified against it, not
   composed from a general sense of what the project "probably" does.
3. Add a new entry to `PROJECTS` in `tools/build_site.py`:
   ```python
   {
       "slug": "projectname",       # must match the actual repo dir name
       "name": "Display Name",
       "tagline": "...",            # short, in the ZX font on its own page
       "desc": "...",               # one paragraph, grounded in the README
       "version": "v0.0.0",         # or None if it has no releases yet
       "accent": "blue",            # see §4.1 for picking one
       "docs_dir": "docs",          # or "doc", or None for root-file fallback
       "docs": ["FILE.md", ...],    # explicit, ordered
   }
   ```
4. Run the build. Fix any warnings about untracked docs (§3) or missing
   `assets_src` files if you're also adding gallery content (§5).
5. Check the new project's card on the home page and its own project page
   render correctly before considering the addition done.

### 4.1 Picking an accent colour

Each project gets one colour from the ZX Spectrum BRIGHT palette (defined
as CSS variables in `tools/assets_src/css/style.css`: `--zx-blue`,
`--zx-red`, `--zx-magenta`, `--zx-green`, `--zx-cyan`, `--zx-yellow`,
`--zx-white`). Current assignments:

| Project | Accent |
|---|---|
| zentools | blue |
| zen80 | red |
| zenzx | magenta |
| zenas | green |
| zenimate | cyan |
| plus3 | yellow |
| bdf-fonts | white |

All seven are taken. An eighth project needs either a colour reused
(acceptable — the accent identifies a project on its own pages via
`::before` glyphs and borders; two projects sharing a colour doesn't
create ambiguity since they're never shown side by side except as
homepage cards, where the project name itself disambiguates) or a genuine
ninth accent added to `:root` in the stylesheet.

---

## 5. Adding screenshots or video to a project's gallery

The gallery is opt-in per project — a project with no `"gallery"` key in
its manifest entry simply doesn't render one. To add one:

1. Copy the actual image/video files into
   `tools/assets_src/img/<slug>/` (images) or
   `tools/assets_src/video/<slug>/` (video). This is the permanent source
   — see §6.1 for why it must be here and not directly under `zsp_site/`.
2. Add a `"gallery"` list to that project's manifest entry:
   ```python
   "gallery": [
       {
           "type": "image",              # or "video" — defaults to "image"
           "src": "slug/filename.png",   # relative to assets/img/ or assets/video/
           "caption": "...",
       },
   ],
   ```
3. Write captions that describe **only what's actually visible** in the
   shot — what feature or code path it demonstrates — not invented
   marketing language. If you're not certain what something in the
   screenshot is (an unfamiliar menu, an unlabelled UI state), say what
   you can verify and leave the rest out rather than guess.
4. Rebuild and check the gallery renders: image count matches, images
   actually decode (`naturalWidth > 0`, not just present in the DOM — an
   `<img>` tag with a 404 `src` still exists as an element), and for
   video, that the `<video>` element has the right `src` resolved.

### 5.1 Copyright judgment on third-party content

Screenshots of the emulators (zenzx, zenimate) will sometimes capture
third-party software running inside them — commercial games, in one case.
**This is not a decision to make silently.** Before adding a screenshot
that shows recognisable third-party IP:

- If it's your own tooling, test programs, or clearly public-domain/
  homebrew software: fine to include without much ceremony.
- If it's a recognisable commercial game (a title screen, box art, a
  screen carrying an explicit copyright/trademark notice): flag it
  explicitly rather than choosing for the human. State plainly what it is
  and whose IP it is, and let them decide. If they confirm they want it
  in under a fair-use rationale (a single still frame, for compatibility
  or rendering-fidelity documentation, on a non-commercial personal
  project — this is a well-established, low-risk fair-use pattern used
  throughout the emulation community), caption it with proper
  attribution: name the work and the rights holder in the caption text
  itself, and state the purpose ("shown for rendering fidelity, not
  distributed with or by this project"). Do not include such a screenshot
  without that attribution once the decision is made to use it.

### 5.2 Video specifically

- Confirm the file is genuinely valid independently of any browser:
  `ffprobe -v error -show_format -show_streams <file>` should return a
  clean stream description; `ffmpeg -v error -i <file> -frames:v 1 -f
  null -` should exit cleanly (confirms the video actually decodes).
- **Do not trust a local `file://` or `python3 -m http.server` test for
  video playback.** Browsers issue `Range` requests for `<video>`
  elements, `file://` doesn't support them meaningfully, and Python's
  built-in `http.server` ignores the `Range` header entirely and returns
  `200` with the full body instead of `206 Partial Content` — Chrome will
  abort the load (`net::ERR_ABORTED`, `video.error.code === 4`) even
  though the file is completely fine. This happened during this site's
  own build and cost real time chasing a phantom bug. If you need to
  verify actual playback, either trust the independent `ffprobe`/`ffmpeg`
  validity check, or test against a server that genuinely honours `Range`
  (real static hosts — GitHub Pages included — do this correctly as a
  matter of course; Python's dev server does not).

---

## 6. Changing the design

The stylesheet lives at `tools/assets_src/css/style.css` — **never edit
anything under `zsp_site/assets/`**, it gets deleted and regenerated on
every build (see §6.1). After any CSS change:

```bash
cd zsp
rm -rf zsp_site dist
python3 tools/build_site.py
```

then run the verification pass in §7 before considering the change done.

### 6.1 Why assets live in `tools/assets_src/`, not `zsp_site/assets/`

This is the single costliest mistake made building this site, twice, and
worth understanding so it isn't made a third time.

Early on, the font, images, and CSS were placed directly under
`zsp_site/assets/` by hand. `build_site.py` only ever generated *HTML* —
it had no code path that touched `assets/` at all. That worked, right up
until the first time `zsp_site/` was wiped with `rm -rf zsp_site` to force
a clean rebuild (a completely reasonable thing to do, and something this
manual itself recommends in §2). The wipe deleted the assets along with
the stale HTML, the rebuild regenerated the HTML but never restored the
assets, and the result was a site with correct markup and zero working
CSS, fonts, or images — while looking, to a quick glance, like it had
built successfully. This happened *twice* before the actual fix landed.

The fix: `tools/assets_src/` is the permanent, version-controlled source
for every static asset (`css/`, `fonts/`, `img/`, `video/`).
`build_site.py`'s `copy_assets()` copies this tree into `zsp_site/assets/`
as the first step of every build, unconditionally. `zsp_site/assets/` is
now genuinely disposable build output, like every other file under
`zsp_site/`. If you ever find yourself editing a file under
`zsp_site/assets/` directly, stop — that edit will silently vanish on the
next rebuild. Edit `tools/assets_src/` instead.

---

## 7. Verification, before shipping anything

This is the standard that was arrived at the hard way, after shipping a
stale zip more than once and a CSS regression that reached "done" without
actually being tested. Treat this as the minimum bar, not a suggestion.

1. **Rebuild clean.** `rm -rf zsp_site dist && python3 tools/build_site.py`.
   A change that only "works" against a stale `zsp_site/` from a previous
   build isn't verified.
2. **Sweep every page, not a sample.** There are ~34 HTML pages; checking
   three of them and assuming the rest are fine is exactly how the
   `.doc-page`/`.wrap` padding collision (see §8.2) went unnoticed across
   every single doc page while looking fine on the home page. A Playwright
   loop over `glob.glob('**/*.html', recursive=True)` is cheap — use it.
3. **Check computed values, not just presence.** `getComputedStyle(el)`
   for the specific property that matters (`backgroundColor`,
   `paddingLeft`, `transform`), not just "does the element exist." Also
   check images actually decode (`naturalWidth > 0`), not just that an
   `<img>` tag is present — a 404'd image still has a DOM node.
4. **Watch for `requestfailed` and `pageerror` events** while loading each
   page. If testing many pages in one script, **use a fresh `page` object
   per URL**, or explicitly remove listeners between iterations. A loop
   that does `pg.on('requestfailed', lambda r: failed.append(...))` once
   per iteration without cleanup leaks listeners across every subsequent
   `pg.goto()` on the same page object — and because Python closures
   capture the *variable*, not its value at definition time, every stale
   listener ends up appending into whatever list `failed` is currently
   bound to. This produced a report of "34 failed requests" for what was
   actually one real event, counted 34 times over. It's a real footgun;
   it happened during this build.
5. **Test the file you're actually about to hand over, not your working
   copy.** Package the zip, then extract *that exact file* into a clean
   temp directory and run the verification against the extracted copy.
   Checksum the zip before and after handing it over
   (`md5sum path/to/zip`) and confirm the delivered copy matches. This
   site shipped a genuinely stale zip more than once during development —
   the working files on disk were correct, but whatever was actually
   delivered wasn't the latest build. Testing the working copy and
   shipping a different file is not verification.

A minimal version of the full sweep:

```python
from playwright.sync_api import sync_playwright
import os, glob

with sync_playwright() as p:
    b = p.chromium.launch()
    failed_total, errs_total, bad_margin = [], [], []
    for rel in sorted(glob.glob('**/*.html', recursive=True)):
        pg = b.new_page(viewport={'width': 1280, 'height': 900})
        failed, errs = [], []
        pg.on('requestfailed', lambda r: failed.append(r.url))
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.abspath(rel))
        pg.wait_for_timeout(50)
        pads = pg.evaluate(
            "() => Array.from(document.querySelectorAll('.wrap'))"
            ".map(w => getComputedStyle(w).paddingLeft)")
        if failed: failed_total.append((rel, failed))
        if errs: errs_total.append((rel, errs))
        if any(p == '0px' for p in pads): bad_margin.append(rel)
        pg.close()
    b.close()
    print('failed:', failed_total)
    print('errors:', errs_total)
    print('zero-margin pages:', bad_margin)
```

(Ignore `.mp4` entries in `failed` — see §5.2 on why local video testing
gives false positives.)

---

## 8. Known pitfalls

Consolidated from the sections above, for quick scanning.

### 8.1 Heading-level analysis must skip fenced code blocks

A naive `grep -c '^# '` across a markdown file counts `# comment` lines
inside ` ```yaml`/` ```bash` code examples as if they were real headings.
This produced a false report of a document having "12 H1 headings" when
it actually had exactly one — the other eleven were shell/YAML comments
in code examples. If you need to analyse a document's real heading
structure, track fenced-code state line by line and skip anything inside
a fence. Trust rendered HTML output or a fence-aware parser over a raw
grep for anything beyond a quick sanity check.

### 8.2 CSS shorthand collisions on combined classes

`<div class="wrap doc-page">` combined two classes that each declared
`padding` as shorthand. `.wrap { padding: 0 1.5rem }` and `.doc-page {
padding: 3rem 0 5rem }` have equal specificity, so whichever is declared
later in the stylesheet wins *entirely* — and the 3-value shorthand `3rem
0 5rem` sets left/right padding to `0`, silently erasing `.wrap`'s
horizontal margin on every page that used both classes together. The
symptom was "some pages have margin, some don't," which read like a
content problem and wasn't. The fix: when two classes are combined on the
same element and both touch `padding` or `margin`, prefer longhand
(`padding-top`/`padding-bottom`) for whichever one only means to affect
one axis, so it can't clobber the other's declaration regardless of
source order.

### 8.3 Test harness bugs look exactly like real bugs

Several of the "regressions" chased during this build were bugs in the
verification code, not the site: the Python closure/loop issue (§7.4),
the video Range-request false negative (§5.2), and a hand-rolled test
HTTP server that itself had three separate bugs (missing `do_HEAD`,
wrong `Content-Type` for non-video files, a connection reset) before it
was abandoned in favour of just trusting `ffprobe`/`ffmpeg` directly.
When a test result looks alarming, check the test before concluding the
site is broken — but don't use that as a reason to skip testing, either.
The fix each time was to isolate the test properly (fresh page per
iteration, correct Content-Type, or an independent validity check outside
the browser entirely), not to stop testing.

---

## 9. Release checklist

1. Confirm `VERSION` is bumped and `CHANGELOG.md` has a matching
   `## [X.Y.Z] - YYYY-MM-DD` entry.
2. Run `scripts/release.sh` from the repo root. It will refuse to proceed
   if the version format is wrong or the changelog entry is missing.
3. It rebuilds clean, checks for stray `.md` cross-links and a sane page
   count, and stages `dist/zsp-site-vX.Y.Z.zip`.
4. Run the full verification pass (§7) against the staged output before
   tagging anything.
5. `git tag vX.Y.Z` — this is a manual, human step. Nothing in this repo
   tags or pushes on its own.
