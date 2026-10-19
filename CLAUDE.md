# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NV9P is a personal amateur radio blog built with [Zensical](https://zensical.org) (the successor to Material for MkDocs). Content is written in Markdown with YAML frontmatter; Python macros handle dynamic content generation.

## Common Commands

```bash
# Install dependencies (Python 3.11+)
pip install -r requirements.txt

# Start local dev server (hot reload at http://localhost:8000)
zensical serve

# Build static site to site/
zensical build
```

## Architecture

### Content Pipeline

Blog posts live in `docs/blog/posts/*.md` with YAML frontmatter (`title`, `date`, `readtime`, `tags`, `pin`). Zensical processes these through a custom Python macro module:

- **`main.py`** — Loaded as a macro plugin (`module_name = "main"` in `zensical.toml`). Exposes `recent_posts(count)` as a Jinja2 template macro used in `docs/index.md` to display the latest posts. The `define_env(env)` function is the entry point — do not run this file directly.
- **`hooks/socialmedia.py`** — Legacy MkDocs hook for share buttons. It is not enabled in the config.

### Key Config

`zensical.toml` controls everything: theme, plugins (glightbox, macros, blog; search is on by default), nav structure, markdown extensions, and Google Analytics.

### Theme

The "Front Range at Dusk" theme sits on top of the stock Zensical theme (`custom_dir = "overrides"`, `extra_css = ["stylesheets/nv9p.css"]`). The design and plan are in `specs/`.

- `overrides/main.html` fills the base template's `hero` block (`partials/nv-banner.html`, the large banner on the homepage and a slim strip elsewhere) and its `content` block (`partials/nv-now.html`, homepage only). Zensical 0.0.71 doesn't set `page.is_homepage`, so the homepage is detected by `page.url == ""`.
- `overrides/partials/header.html` is a copy of the theme partial, changed to show `extra.wordmark`.
- Editable data lives in `[project.extra]`: `wordmark`, `station` (tagline, tags) and `now` (updated, items with icon/title/text).
- `docs/stylesheets/nv9p.css` defines the `--nv-*` palette tokens. Duplicate page H1s are hidden by CSS where the banner shows the title.

### Tests

`tests/test_build.py` (stdlib `unittest`) checks the built `site/` output. Run `zensical build`, then `python -m unittest tests.test_build -v`. `site/` is build output and is not tracked; Cloudflare Pages builds from source.

### Blog Post Frontmatter

```yaml
---
title: Post Title
date:
  created: 2024-01-15
readtime: 5
tags:
  - tag1
  - tag2
pin: false
---
```

The `main.py` parser handles multiple date formats for flexibility. Post URLs are `/blog/YYYY/MM/DD/<slug>/`, where the slug is the slugified `title` unless a `slug` is set in frontmatter.
