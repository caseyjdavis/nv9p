# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NV9P is a personal amateur radio blog built with MkDocs and the Material theme. Content is written in Markdown with YAML frontmatter; Python macros and hooks handle dynamic content generation.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start local dev server (hot reload at http://localhost:8000)
mkdocs serve

# Build static site to site/
mkdocs build
```

## Architecture

### Content Pipeline

Blog posts live in `docs/blog/posts/*.md` with YAML frontmatter (`title`, `date`, `readtime`, `tags`, `pin`). MkDocs processes these through two custom Python components:

- **`main.py`** — Loaded as a macro plugin (`module_name: main` in `mkdocs.yml`). Exposes `recent_posts(count)` as a Jinja2 template macro used in `docs/index.md` to display the latest posts. The `define_env(env)` function is the MkDocs entry point — do not run this file directly.
- **`hooks/socialmedia.py`** — MkDocs hook that post-processes blog pages to inject Twitter/Facebook share buttons.

### Key Config

`mkdocs.yml` controls everything: theme, plugins (search, glightbox, macros, blog), nav structure, markdown extensions, and Google Analytics.

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

The `main.py` parser handles multiple date formats for flexibility.
