#!/usr/bin/env python3
"""
zsp site generator — builds the static Zen Spectrum Project site from the
markdown already living in each project's repo. Run once; regenerate any
time a project's docs change.
"""
import os
import re
import shutil
import markdown as mdlib

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TOOLS_DIR)
SITE = os.path.join(REPO_ROOT, "zsp_site")
ROOT = os.path.dirname(REPO_ROOT)
VERSION_FILE = os.path.join(REPO_ROOT, "VERSION")

MD_EXT = ["fenced_code", "tables", "sane_lists", "toc", "attr_list"]

def read_version():
    if not os.path.isfile(VERSION_FILE):
        raise SystemExit(f"build_site: VERSION file not found at {VERSION_FILE}")
    ver = open(VERSION_FILE, encoding="utf-8").read().strip()
    if not ver:
        raise SystemExit("build_site: VERSION file is empty")
    return ver

SITE_VERSION = None  # set in main(); read once, stamped into every footer

# ---------------------------------------------------------------------------
# Project manifest — hand-verified against each repo's README, not guessed.
# ---------------------------------------------------------------------------
PROJECTS = [
    {
        "slug": "zentools",
        "name": "zentools",
        "tagline": "Convert and inspect the formats a Spectrum actually used",
        "desc": "A Go library and command-line toolkit for converting and "
                "manipulating ZX Spectrum file formats: TAP, TZX, snapshots "
                "(.sna, .z80), and BASIC. No third-party dependencies.",
        "version": "v0.5.0",
        "accent": "blue",
        "docs_dir": "docs",
        "docs": ["ARCHITECTURE.md", "CLI.md", "LIBRARY.md", "MIGRATION-STATUS.md"],
    },
    {
        "slug": "zen80",
        "name": "zen80",
        "tagline": "A Z80, stepped one instruction at a time",
        "desc": "A simple instruction-stepped Z80 CPU emulator written in Go, "
                "inspired by the cycle-accurate emulation techniques described "
                "in floooh's blog posts. Implements the complete documented "
                "and undocumented instruction set.",
        "version": "v0.1.0",
        "accent": "red",
        "docs_dir": None,
        "docs": ["README.md", "ROADMAP.md", "COVERAGE.md", "CHANGELOG.md"],
    },
    {
        "slug": "zenzx",
        "name": "ZenZX",
        "tagline": "48K to +3, one emulator, one Z80 core underneath",
        "desc": "A ZX Spectrum emulator in Go, built on the zen80 Z80 CPU "
                "core. Emulates the 48K, 128K, +2, and +3 models (including "
                "the +3 floppy disc controller), with tape and snapshot "
                "support.",
        "version": "v0.4.2",
        "accent": "magenta",
        "docs_dir": "docs",
        "docs": ["zenscript.md"],
        "gallery": [
            {
                "type": "video",
                "src": "zenzx/tape-loading-demo.mp4",
                "caption": "Tape loading in progress — screen-control "
                           "keyboard shortcuts keep working while a tape "
                           "loads.",
            },
            {
                "type": "image",
                "src": "zenzx/cli-usage-and-basic.png",
                "caption": "Command-line usage and flags, alongside a "
                           "128K BASIC session actually running.",
            },
            {
                "type": "image",
                "src": "zenzx/sprite-utility-compat.png",
                "caption": "A period graphics utility running unmodified — "
                           "compatibility with real Spectrum software.",
            },
            {
                "type": "image",
                "src": "zenzx/onscreen-keyboard.png",
                "caption": "The on-screen Spectrum keyboard, with a short "
                           "BASIC colour demo running behind it.",
            },
            {
                "type": "image",
                "src": "zenzx/wonderful-dizzy-menu.png",
                "caption": "Wonderful Dizzy (Codemasters / The Oliver "
                           "Twins, 1989) rendered in ZenZX — shown for "
                           "colour and rendering fidelity, not "
                           "distributed with or by this project.",
            },
        ],
    },
    {
        "slug": "zenas",
        "name": "zenas",
        "tagline": "An assembler that runs what it assembles",
        "desc": "A Z80 and Z80N macro assembler written in Go that can also "
                "execute and test the code it assembles. Assembles source to "
                "raw machine code, packages it into runnable tapes and "
                "snapshots, or runs it in a built-in Z80 emulator and asserts "
                "on the result.",
        "version": "v0.7.5",
        "accent": "green",
        "docs_dir": "docs",
        "docs": [
            "MANUAL.md", "ZENAS_PROGRAMMING.md", "ZENAS_DESIGN.md",
            "INSTRUCTION_SET.md", "Z80N_REFERENCE.md", "RUNTIME.md",
            "DIALECT_COMPATIBILITY.md", "SEAM_COMPARISON.md",
            "PACKAGED_PROGRAM_TUTORIAL.md",
        ],
    },
    {
        "slug": "zenimate",
        "name": "zenimate",
        "tagline": "Draw the frame, paint the attributes, watch it move",
        "desc": "A ZX Spectrum animated sprite editor, in Go. Draw a "
                "multi-frame sprite on a pixel grid, paint per-character-cell "
                "Spectrum colour attributes, and preview the animation.",
        "version": "v0.7.0",
        "accent": "cyan",
        "docs_dir": "docs",
        "docs": ["GUIDE.md", "persistence-proposal.md"],
        "gallery": [
            {
                "src": "zenimate/v070-full-tool-palette.png",
                "caption": "v0.7.0 — the full 12-tool palette: brush, select, "
                           "fill, eyedropper, line, rectangle, circle, "
                           "triangle, hexagon, text, pan, and zoom.",
            },
            {
                "src": "zenimate/v060-spectrum-colour-joker.png",
                "caption": "Spectrum colour mode: a monochrome bitmap with "
                           "per-character-cell colour attributes painted on "
                           "top, live in the preview panel.",
            },
            {
                "src": "zenimate/v060-multiframe-forest-scene.png",
                "caption": "A 4-frame animation under construction, building "
                           "a platformer scene tile by tile.",
            },
            {
                "src": "zenimate/v060-image-import-batman.png",
                "caption": "Importing an external image and reducing it to "
                           "the Spectrum's bitmap-plus-attribute format.",
            },
            {
                "src": "zenimate/v061-frame-menu.png",
                "caption": "The frame menu — insert, duplicate, copy/paste, "
                           "delete — editing an 8-frame, 16\u00d716 sprite.",
            },
        ],
    },
    {
        "slug": "plus3",
        "name": "plus3",
        "tagline": "Everything the +3's disk drive ever wrote, on your host",
        "desc": "A command-line utility for creating, managing, and "
                "inspecting virtual disk images in the +3DOS format used by "
                "the ZX Spectrum +3.",
        "version": "v0.9.8",
        "accent": "yellow",
        "docs_dir": "doc",
        "docs": ["MANUAL.md", "LIBRARY-USAGE.md", "PLUS3DOS-PITFALLS.md"],
    },
    {
        "slug": "bdf-fonts",
        "name": "bdf-fonts",
        "tagline": "Bitmap fonts for screens too small for anti-aliasing",
        "desc": "A curated collection of BDF bitmap fonts, including a font "
                "extracted directly from the ZX Spectrum ROM. Useful for "
                "retro UIs and low-resolution displays.",
        "version": None,
        "accent": "white",
        "docs_dir": None,
        "docs": ["README.md", "font_catalogue.md"],
    },
]

ACCENT_VAR = {
    "blue": "var(--zx-blue)", "red": "var(--zx-red)",
    "magenta": "var(--zx-magenta)", "green": "var(--zx-green)",
    "cyan": "var(--zx-cyan)", "yellow": "var(--zx-yellow)",
    "white": "var(--zx-white)",
}

# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------
BADGE_RE = re.compile(r'^\s*(\[!\[|!\[)')

def slugify(filename):
    base = re.sub(r'\.md$', '', filename, flags=re.I)
    base = re.sub(r'[_\s]+', '-', base)
    return base.lower()

def strip_md(text):
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'[*_#>]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def excerpt(raw_md, limit=170):
    blocks = re.split(r'\n\s*\n', raw_md)
    for block in blocks:
        if BADGE_RE.match(block):
            continue
        cleaned = strip_md(block)
        if len(cleaned) > 40:
            if len(cleaned) > limit:
                cut = cleaned[:limit].rsplit(' ', 1)[0]
                return cut + '…'
            return cleaned
    return ""

def extract_title(raw_md, fallback):
    m = re.search(r'^#\s+(.+)$', raw_md, re.MULTILINE)
    if m:
        return strip_md(m.group(1))
    return fallback

def rewrite_md_links(html, doc_filenames):
    """Point in-repo .md cross-links at the sibling .html page we generate."""
    lookup = {f.lower(): slugify(f) + ".html" for f in doc_filenames}

    def repl(m):
        href = m.group(1)
        base = href.split('/')[-1].split('#')[0]
        if base.lower() in lookup:
            return f'href="{lookup[base.lower()]}"'
        return m.group(0)

    return re.sub(r'href="([^"]+\.md)"', repl, html, flags=re.I)

def render_md_file(path, doc_filenames):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    title = extract_title(raw, os.path.basename(path))
    exc = excerpt(raw)
    body_html = mdlib.markdown(raw, extensions=MD_EXT)
    body_html = rewrite_md_links(body_html, doc_filenames)
    return title, exc, body_html

# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
def nav(depth, active=""):
    p = "../" * depth
    def link(href, label, key):
        cls = ' class="active"' if key == active else ""
        return f'<a href="{href}"{cls}>{label}</a>'
    return f'''<header class="site-nav"><div class="wrap nav-inner">
<a class="nav-brand" href="{p}index.html">haitch<span class="dim">/</span>zsp</a>
<nav class="nav-links">
{link(p + "index.html#projects", "Projects", "projects")}
{link(p + "known-issues.html", "Known Issues", "issues")}
<a href="https://github.com/ha1tch/zsp">GitHub</a>
</nav></div></header>'''

def footer(depth):
    p = "../" * depth
    return f'''<footer><div class="wrap foot-row">
<span>haitch's Zen Spectrum Project v{SITE_VERSION} — Apache 2.0</span>
<span><a href="mailto:h@ual.li">h@ual.li</a> · <a href="https://oldbytes.space/@haitchfive">@haitchfive</a></span>
</div></footer>'''

def page(title, content, depth, active="", accent=None):
    p = "../" * depth
    accent_style = f' style="--accent: {ACCENT_VAR[accent]};"' if accent else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — haitch's Zen Spectrum Project</title>
<link rel="stylesheet" href="{p}assets/css/style.css">
</head>
<body{accent_style}>
{nav(depth, active)}
{content}
{footer(depth)}
</body>
</html>'''

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def project_doc_paths(proj):
    """Return [(full_source_path, filename)] for this project's doc set."""
    base = os.path.join(ROOT, proj["slug"])
    sub = proj["docs_dir"]
    out = []
    for fname in proj["docs"]:
        full = os.path.join(base, sub, fname) if sub else os.path.join(base, fname)
        out.append((full, fname))
    return out

def check_untracked_docs(proj):
    """Warn if the source directory has .md files not listed in the
    manifest — the manifest's order is curated by hand, so this is a
    check, not an auto-discovery mechanism. A new doc file should show up
    here loudly rather than silently missing from the built site."""
    base = os.path.join(ROOT, proj["slug"])
    scan_dir = os.path.join(base, proj["docs_dir"]) if proj["docs_dir"] else base
    if not os.path.isdir(scan_dir):
        return
    on_disk = {f for f in os.listdir(scan_dir) if f.lower().endswith(".md")}
    tracked = set(proj["docs"])
    untracked = sorted(on_disk - tracked)
    if untracked:
        print(f"WARNING: {proj['slug']} has untracked doc(s) not in the "
              f"manifest: {', '.join(untracked)} — add to PROJECTS['docs'] "
              f"in tools/build_site.py to publish.")

def build_project(proj):
    slug = proj["slug"]
    proj_dir = os.path.join(SITE, "projects", slug)
    docs_out = os.path.join(proj_dir, "docs")
    if os.path.isdir(docs_out):
        shutil.rmtree(docs_out)
    os.makedirs(docs_out, exist_ok=True)

    doc_paths = project_doc_paths(proj)
    doc_filenames = [fn for _, fn in doc_paths]

    rows = []
    for full_path, fname in doc_paths:
        title, exc, body_html = render_md_file(full_path, doc_filenames)
        doc_slug = slugify(fname)
        doc_content = f'''<div class="wrap doc-page">
<a class="back" href="../index.html">&larr; back to {proj["name"]}</a>
<article class="doc-body">
{body_html}
</article></div>'''
        doc_html = page(f'{title} · {proj["name"]}', doc_content, depth=3,
                         accent=proj["accent"])
        with open(os.path.join(docs_out, doc_slug + ".html"), "w", encoding="utf-8") as f:
            f.write(doc_html)
        rows.append(f'''<a class="doc-row" href="docs/{doc_slug}.html">
<div><p class="doc-title">{title}</p><p class="doc-excerpt">{exc}</p></div>
<span class="doc-link">Read &rarr;</span>
</a>''')

    version_html = f'<span class="pill">{proj["version"]}</span>' if proj["version"] else ""

    gallery_html = ""
    if proj.get("gallery"):
        def render_shot(shot):
            kind = shot.get("type", "image")
            if kind == "video":
                media = (f'<video src="../../assets/video/{shot["src"]}" '
                         f'controls preload="metadata" '
                         f'aria-label="{shot["caption"]}"></video>')
            else:
                media = (f'<img src="../../assets/img/{shot["src"]}" '
                         f'alt="{shot["caption"]}" loading="lazy">')
            return f'''<figure class="gallery-item">
{media}
<figcaption>{shot["caption"]}</figcaption>
</figure>'''
        items = "".join(render_shot(shot) for shot in proj["gallery"])
        gallery_html = f'''<section class="section"><div class="wrap">
<p class="section-label">In action</p>
<div class="gallery-grid">
{items}
</div>
</div></section>'''

    proj_content = f'''<section class="project-hero"><div class="wrap">
<a class="back" href="../../index.html#projects">&larr; all projects</a>
<h1>{proj["name"]}</h1>
<p class="zx-subtitle">{proj["tagline"]}</p>
<p class="desc">{proj["desc"]}</p>
<div class="meta-row">
{version_html}
<a href="https://github.com/ha1tch/{slug}">github.com/ha1tch/{slug} &rarr;</a>
</div>
</div></section>
{gallery_html}
<section class="section"><div class="wrap">
<p class="section-label">Documentation</p>
<div class="docs-list">
{"".join(rows)}
</div>
</div></section>'''

    html = page(proj["name"], proj_content, depth=2, accent=proj["accent"])
    with open(os.path.join(proj_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build_home():
    cards = []
    for proj in PROJECTS:
        version_html = f'<span class="pill">{proj["version"]}</span>' if proj["version"] else '<span class="pill">docs</span>'
        cards.append(f'''<a class="card" href="projects/{proj["slug"]}/index.html" style="--accent: {ACCENT_VAR[proj["accent"]]};">
<span class="card-accent"></span>
<h3>{proj["name"]}</h3>
<p class="desc">{proj["tagline"]}</p>
<div class="meta">{version_html}<span class="go">Open &rarr;</span></div>
</a>''')

    clash = '''<div class="clash-strip"><div class="clash-grid">
<img src="assets/img/pattern-green-magenta.png" alt="ZX Spectrum attribute clash pattern, green and magenta">
<img src="assets/img/pattern-yellow-cyan.png" alt="ZX Spectrum attribute clash pattern, yellow and cyan">
<img src="assets/img/pattern-cyan-red.png" alt="ZX Spectrum attribute clash pattern, cyan and red">
</div></div>'''

    content = f'''{clash}
<section class="hero"><div class="wrap">
<p class="hero-eyebrow">haitch's</p>
<h1><span class="accent">Zen</span> Spectrum Project</h1>
<p class="zx-subtitle">for the machine in rainbows</p>
</div></section>
<section class="section intro"><div class="wrap">
<p>These were built one at a time, as each was needed, and they turned out to
fit together into a working toolchain for the ZX Spectrum.
<strong>zen80</strong> is a Z80 CPU core. <strong>zenzx</strong> wraps it into
a full 48K/128K/+2/+3 machine, tape and snapshot support included.
<strong>zenas</strong> assembles Z80 and Z80N source and can run what it
assembles inside its own built-in emulator. <strong>zentools</strong>
converts between tape (TAP/TZX), snapshot (.sna/.z80), and BASIC formats.
<strong>zenimate</strong> draws and animates multi-frame sprites.
<strong>plus3</strong> reads and writes +3DOS disk images. All under active
development.</p>
</div></section>
<section class="section" id="projects"><div class="wrap">
<p class="section-label">Projects</p>
<div class="card-grid">
{"".join(cards)}
</div>
</div></section>
<script>
(function() {{
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
    return;
  }}
  var grid = document.querySelector('.clash-grid');
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.clash-grid img'));

  function shuffle(arr) {{
    arr = arr.slice();
    for (var i = arr.length - 1; i > 0; i--) {{
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }}
    return arr;
  }}

  setInterval(function() {{
    var slotWidth = grid.offsetWidth / imgs.length;
    var perm = shuffle(imgs.map(function(_, i) {{ return i; }}));
    imgs.forEach(function(img, i) {{
      img.style.transform = 'translateX(' + ((perm[i] - i) * slotWidth) + 'px)';
    }});
  }}, 5000);
}})();
</script>'''

    html = page("Home", content, depth=0)
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def build_known_issues():
    src = os.path.join(REPO_ROOT, "notes", "known-issues.md")
    with open(src, encoding="utf-8") as f:
        raw = f.read()
    body_html = mdlib.markdown(raw, extensions=MD_EXT)
    # Recolour the status glyphs used in the source notes doc.
    body_html = body_html.replace('✓', '<span class="status-fixed">✓</span>')
    body_html = body_html.replace('☐', '<span class="status-open">☐</span>')
    body_html = body_html.replace('☑', '<span class="status-decided">☑</span>')
    content = f'''<div class="wrap doc-page">
<a class="back" href="index.html">&larr; back home</a>
<article class="doc-body">
{body_html}
</article></div>'''
    html = page("Known Issues", content, depth=0, active="issues")
    with open(os.path.join(SITE, "known-issues.html"), "w", encoding="utf-8") as f:
        f.write(html)

def copy_bdf_previews():
    """bdf-fonts/font_catalogue.md references previews/*.png relatively."""
    src = os.path.join(ROOT, "bdf-fonts", "previews")
    dst = os.path.join(SITE, "projects", "bdf-fonts", "docs", "previews")
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))

def copy_assets():
    """Copy the permanent asset source into the generated site. This is what
    makes 'rm -rf zsp_site' always safe: assets are build output derived
    from tools/assets_src/, not hand-placed files that a clean rebuild can
    destroy."""
    src = os.path.join(TOOLS_DIR, "assets_src")
    dst = os.path.join(SITE, "assets")
    if not os.path.isdir(src):
        raise SystemExit(f"build_site: assets_src not found at {src}")
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def main():
    global SITE_VERSION
    SITE_VERSION = read_version()
    os.makedirs(SITE, exist_ok=True)
    copy_assets()
    for proj in PROJECTS:
        check_untracked_docs(proj)
        build_project(proj)
    copy_bdf_previews()
    build_home()
    build_known_issues()
    print("Site built.")

if __name__ == "__main__":
    main()
