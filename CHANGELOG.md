# Changelog

All notable changes to zsp are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-07-06

### Added

- Initial site: home page with project cards for all seven projects under
  the umbrella (zentools, zen80, zenzx, zenas, zenimate, plus3, bdf-fonts).
- Per-project sub-sites, each with a docs menu (compressed excerpts) linking
  to full HTML-rendered versions of every source markdown file.
- `notes/known-issues.md`, rendered as a site-wide Known Issues page,
  tracking problems found while working across the projects.
- Design system: Inter and Fira Code for UI/body/technical text, the
  ZXSpectrum font (jfsebastian/zx-spectrum-unicode-font, public domain)
  reserved for subtitles and quotations only, and a ZX Spectrum BRIGHT
  palette accent assigned per project.
- Home page hero: the three attribute-clash illustration images, shuffling
  into a random new arrangement every 5 seconds (disabled under
  `prefers-reduced-motion`).
- Introductory paragraph describing the current shape of the corpus.
- `tools/build_site.py` — the static site generator; regenerates
  `zsp_site/` from each project's source markdown.
- `scripts/release.sh` — release automation: validates `VERSION` and its
  matching changelog entry, regenerates the site, verifies the rebuild,
  and stages a versioned checkpoint under `dist/`.
- `VERSION` as the single source of truth, read live by `build_site.py` and
  stamped into every page's footer.
