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
