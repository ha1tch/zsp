# zsp — haitch's Zen Spectrum Project

Live site: **https://ha1tch.github.io/zsp/**

A static site aggregating the documentation, releases, and known issues for
the ZX Spectrum tools under [github.com/ha1tch](https://github.com/ha1tch):
zentools, zen80, zenzx, zenas, zenimate, plus3, and bdf-fonts.

The site itself lives at `github.com/ha1tch/zsp`. It's generated, not
hand-written — source content is pulled directly from each project's own
repository and rendered into HTML.

## Structure

```
zsp/
├── README.md              This file
├── PROCEDURES.md          Step-by-step maintenance workflow
├── VERSION                Single source of truth for the site's version
├── CHANGELOG.md           Keep a Changelog format, one entry per release
├── .gitignore
├── tools/
│   └── build_site.py      Regenerates every page in zsp_site/ from source markdown
├── scripts/
│   └── release.sh         Release automation (see Releasing, below)
├── notes/
│   └── known-issues.md    Running log of problems found across projects
└── zsp_site/              The generated, publishable site — everything below is output
    ├── index.html         Home page — project cards
    ├── known-issues.html  Rendered from ../notes/known-issues.md
    ├── assets/
    │   ├── css/style.css  Shared stylesheet
    │   ├── fonts/         ZXSpectrum.ttf — subtitles and quotations only
    │   └── img/           Illustration assets
    └── projects/
        └── <slug>/
            ├── index.html Project sub-site home, with a docs menu
            └── docs/      One rendered page per source markdown file
```

`zsp_site/` is build output, not source — everything in it is written by
`tools/build_site.py` and safe to delete and regenerate at any time.

## Building

Requirements: Python 3 with the `markdown` package.

```bash
pip install markdown
python3 tools/build_site.py
```

`build_site.py` expects each source project to be cloned as a sibling
directory of the `zsp` repo itself — `../zentools`, `../zen80`, and so on.
For projects with a `docs/` (or `doc/`) folder, every markdown file in it
becomes a page. For projects without one, root-level markdown files (README,
CHANGELOG, etc.) are used instead — see the `PROJECTS` manifest at the top
of the script for the exact file list per project.

Regenerate `zsp_site/` any time a project's docs change:

```bash
python3 tools/build_site.py
```

## Versioning and releases

Versioning follows the same pattern used across the other projects under
the umbrella (see zenimate's `scripts/release.sh`), adapted for a static
site rather than a compiled binary.

`VERSION` at the repo root is the single source of truth. Unlike a compiled
Go project, there's no separate constant to keep in sync — `build_site.py`
reads `VERSION` directly at generation time and stamps it into every page's
footer, so it's never out of date with what's actually published.

To cut a release:

1. Bump `VERSION`.
2. Add a matching `## [X.Y.Z] - YYYY-MM-DD` entry to `CHANGELOG.md`.
3. Run `scripts/release.sh`. It validates the version format and the
   changelog entry, regenerates `zsp_site/` from a clean state, checks the
   rebuild for stray cross-links and a sane page count, and stages
   `dist/zsp-site-vX.Y.Z.zip`.
4. Review the output, then `git tag vX.Y.Z` to trigger the release. The
   script never tags or pushes on its own.

## Keeping it current

See `PROCEDURES.md` for the step-by-step maintenance workflow — adding a
doc, adding a project, updating the gallery, cutting a release, and the
pitfalls worth knowing about before you hit them yourself.

## Projects

| Project | What it does |
|---|---|
| [zentools](https://github.com/ha1tch/zentools) | TAP, TZX, snapshot, and BASIC conversion toolkit |
| [zen80](https://github.com/ha1tch/zen80) | Instruction-stepped Z80 CPU emulator |
| [zenzx](https://github.com/ha1tch/zenzx) | 48K/128K/+2/+3 ZX Spectrum emulator |
| [zenas](https://github.com/ha1tch/zenas) | Z80/Z80N macro assembler that runs what it assembles |
| [zenimate](https://github.com/ha1tch/zenimate) | Animated sprite editor |
| [plus3](https://github.com/ha1tch/plus3) | +3DOS virtual disk image manager |
| [bdf-fonts](https://github.com/ha1tch/bdf-fonts) | Bitmap font collection |

## Licence

Apache 2.0 — see https://www.apache.org/licenses/LICENSE-2.0.

Copyright (c) 2026 haitch
h@ual.li · https://oldbytes.space/@haitchfive
