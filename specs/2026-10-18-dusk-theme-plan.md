# NV9P "Front Range at Dusk" Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle nv9p.com with a Colorado dusk theme: a mountain-and-orbit banner with a radiosonde balloon, a satellite logo, and a "What I'm working on right now" homepage panel. The repo cleanup Casey asked for comes first.

**Architecture:** The theme uses Zensical's supported override mechanisms only:
- `custom_dir = "overrides"` holds a `main.html` that fills the base template's `hero` and `content` blocks. Every page template (`blog.html`, `blog-post.html`, `404.html`) extends `main.html`, so the banner reaches all pages.
- One `extra_css` stylesheet holds the dusk palette.
- One copied `partials/header.html` provides the "NV9P" wordmark.

Editable data (the station tags and the "right now" items) lives in `[project.extra]` in `zensical.toml`.

**Tech Stack:**
- Zensical 0.0.71 on Python 3.13, with Jinja2 templates, inline SVG and CSS
- Tests use stdlib `unittest` against the built `site/` output, with no new dependencies

**Spec:** `specs/2026-10-18-dusk-theme-design.md`. The reference mockup is `specs/2026-10-18-dusk-theme-mockup.html`. Its 2m/70cm tags are outdated, and the spec wins.

**Location note:** this plan lives in `specs/`, not `docs/superpowers/plans/`, because everything under `docs/` is published to the site.

## Global Constraints

- Branch: all work goes on `theme/front-range-dusk`. Never commit to or push `main`, because a push to `main` deploys to production through Cloudflare Pages.
- Commit source only. Never commit `site/` output.
- `requirements.txt` stays `zensical==0.0.71`, with no new runtime dependencies.
- The site stays dark-only (`scheme = "slate"`).
- Palette:
  - sky: `#1b1f3a` → `#6a3a5c` → `#ff7043` → `#ffb74d`
  - ridges: `#4a2f4a`, `#2a1f33`, `#17131f`
  - accent: `#ff7043`
  - secondary header text: peach `#ffd9c2`
- `site_name` stays "NV9P Amateur Radio". The header wordmark shows "NV9P".
- Tagline: "Working satellites from the Colorado Rockies".
- Station tags: `DM79`, `ITU 7`, `CQ 4`, `Rocky Mountain Div.`
- Logo icon: `fontawesome/solid/satellite`.
- No Markdown content edits. Duplicate headings are hidden with CSS.
- Must not break: search, blog pagination/tags/archive, glightbox, the `recent_posts` macro, or post URLs (`/blog/YYYY/MM/DD/<slug>/`).
- Phones: 16px side gutters, no horizontal scroll at 375px width.

## Review Focus

1. **Phone-width banner (375px):** the balloon, satellite or orbit must not sit behind "NV9P" or the tagline, and the page must not scroll sideways. Task 3 adds a screenshot check.
2. **Satellite stays on its orbit.** It must stay on the orbit when the banner is cropped at any width, which works only if both share one SVG coordinate system. Task 3 adds a geometry test.
3. **Long or blog page titles in the slim banner:** for example "High Altitude Balloon Part 1 Cameras" at 375px. The title wraps and stays inside the strip. Task 3 adds a screenshot check.
4. **Duplicate H1s hidden only where the banner shows the title.** The H1 stays in the HTML, hidden only by CSS, and the blog index's strip title reads "Blog". Task 3 adds a test.
5. **"Right now" config edge cases:** an empty `items` list renders no panel rather than an empty box, and an icon path that doesn't exist must fail the build loudly rather than silently. Task 4 adds a test.

---

### Task 1: Branch, local environment, repo cleanup, baseline guard tests

**Files:**
- Create: `tests/__init__.py` (empty)
- Create: `tests/test_build.py`
- Modify: `package.json` (empty it)
- Delete: `package-lock.json`
- Untrack: `site/` (files stay on disk)
- Add: `specs/` (the spec, mockup and this plan)

**Interfaces:**
- Produces:
  - `tests/test_build.py`, containing a helper `read(path: str) -> str` that returns the text of `site/<path>` and fails the test if the file is missing
  - a module-level `SITE = Path(__file__).resolve().parent.parent / "site"`

  Later tasks add test classes to this file.

- [ ] **Step 1: Create the branch.** Run `git -C ~/Github/nv9p switch -c theme/front-range-dusk`. Expected: `Switched to a new branch`.
- [ ] **Step 2: Rebuild the Python environment.** The existing `.venv` has Python 3.9 and the placeholder zensical 0.0.2.
  - Run `brew install python@3.13`.
  - Run `rm -rf .venv && /opt/homebrew/bin/python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
  - Expected: `.venv/bin/zensical --version` prints 0.0.71.
- [ ] **Step 3: Write the baseline guard tests** in `tests/test_build.py`, as `class BaselineTest(unittest.TestCase)`. They protect existing behavior, so they must pass both before and after the theme work.
  - `test_search_index_exists`: the file at `search/search_index.json` exists and isn't empty.
  - `test_homepage_lists_three_recent_posts`: `index.html` contains at least 3 links matching `href="[^"]*blog/20\d\d/\d\d/\d\d/[^"]+/"`. Each one resolves to an existing `site/.../index.html`.
  - `test_blog_index_and_post_urls`: `blog/index.html` exists, and `blog/2018/04/16/high-altitude-balloon-part-1-cameras/index.html` exists.
  - `test_glightbox_present`: some post page that contains an `<img` references `glightbox`.
- [ ] **Step 4: Build, then run the tests.**
  - Run `.venv/bin/zensical build && .venv/bin/python -m unittest tests.test_build -v`.
  - Expected: all 4 PASS on the stock theme. If the post slug in `test_blog_index_and_post_urls` is wrong, correct the test from the actual `site/` tree. Don't change the site to match.
- [ ] **Step 5: Clean up.**
  - Run `git rm -r --cached site -q`. `site/` is already in `.gitignore`.
  - Set `package.json` to exactly `{}` followed by a newline.
  - Delete `package-lock.json`. It locks only `mkdocs-material@0.0.1-security`, npm's empty placeholder. This is Claude's call: Casey asked for the package.json to be emptied, and an orphaned lockfile would be inconsistent.
  - Expected: `git ls-files site | wc -l` prints `0`.
- [ ] **Step 6: Commit.**

```bash
git add -A tests specs package.json package-lock.json
git add -u site
git commit -m "chore: untrack built site/, drop placeholder npm package, add build tests and theme spec"
```

---

### Task 2: Dusk palette, satellite logo and favicon, tabs in header, "NV9P" wordmark

**Files:**
- Modify: `zensical.toml`
- Create: `docs/stylesheets/nv9p.css`
- Create: `overrides/partials/header.html`, copied from `.venv/lib/python3.13/site-packages/zensical/templates/partials/header.html`
- Create: `docs/img/satellite.svg`, copied from the theme's `.icons/fontawesome/solid/satellite.svg`, with `fill="#ff7043"` added to the `<svg>`
- Test: `tests/test_build.py`

**Interfaces:**
- Produces:
  - Config keys:
    - `[project.theme] custom_dir = "overrides"`
    - `[project] extra_css = ["stylesheets/nv9p.css"]`
    - `[project.extra] wordmark = "NV9P"`
  - CSS custom properties on `:root` in `nv9p.css`, used by Tasks 3–5:
    - `--nv-sky-1: #1b1f3a`, `--nv-sky-2: #6a3a5c`, `--nv-sky-3: #ff7043`, `--nv-sky-4: #ffb74d`
    - `--nv-ridge-1: #4a2f4a`, `--nv-ridge-2: #2a1f33`, `--nv-ridge-3: #17131f`
    - `--nv-accent: #ff7043`, `--nv-peach: #ffd9c2`
    - `--nv-panel: #23252e`

- [ ] **Step 1: Write the failing tests** as `class ChromeTest(unittest.TestCase)`.
  - `test_logo_is_satellite`: `index.html`'s `md-logo` anchor contains the satellite SVG path, using a distinctive substring of `satellite.svg`'s `d=` attribute, and doesn't contain `tower-broadcast`.
  - `test_wordmark_and_title`: the header topic contains `>NV9P<` (whitespace-trimmed), and `<title>` still contains `NV9P Amateur Radio`.
  - `test_stylesheet_linked`: every page's HTML contains `stylesheets/nv9p.css`.
  - `test_tabs_in_header`: `index.html` contains `md-tabs` inside the `<header` element, and the tab labels Home, Blog, Logbook, QSL Cards and About all appear.
  - `test_favicon_is_satellite`: the `rel="icon"` href ends in `img/satellite.svg`.
- [ ] **Step 2: Run the tests to verify they fail.** Run `.venv/bin/zensical build && .venv/bin/python -m unittest tests.test_build -v`. Expected: the 5 `ChromeTest` tests FAIL and `BaselineTest` passes.
- [ ] **Step 3: Implement.**
  - In `zensical.toml`:
    - set `favicon = "img/satellite.svg"`
    - set `logo = "fontawesome/solid/satellite"`
    - set `features = ["navigation.indexes", "navigation.tabs", "navigation.tabs.sticky"]`
    - add the three config keys listed under Interfaces
  - In `overrides/partials/header.html`, change only the site-name topic to `{{ config.extra.wordmark | d(config.site_name, true) }}`.
  - In `nv9p.css`:
    - define the tokens
    - map the theme onto them, preferring Zensical's variables: `[data-md-color-scheme="slate"]` overrides of `--md-primary-fg-color`, `--md-accent-fg-color`, `--md-typeset-a-color`, and the header/tabs background set to `--nv-sky-1`
    - the body/reading area stays the slate default
- [ ] **Step 4: Run the tests to verify they pass.** Same command. Expected: all pass.
- [ ] **Step 5: Commit** with `git add zensical.toml overrides docs/stylesheets docs/img/satellite.svg tests && git commit -m "feat(theme): dusk palette, satellite logo, header tabs and NV9P wordmark"`.

---

### Task 3: Banner (large on the homepage, slim elsewhere) and duplicate-H1 hiding

**Files:**
- Create: `overrides/main.html`
- Create: `overrides/partials/nv-banner.html`
- Modify: `docs/stylesheets/nv9p.css`, `zensical.toml`
- Test: `tests/test_build.py`
- `docs/index.md` is not edited. The CSS rule below hides its `# NV9P Amateur Radio` H1, because the banner already shows it.

**Interfaces:**
- Consumes: the CSS tokens from Task 2.
- Produces:
  - Config:

```toml
[project.extra.station]
tagline = "Working satellites from the Colorado Rockies"
tags = ["DM79", "ITU 7", "CQ 4", "Rocky Mountain Div."]
```

  - Markup:
    - `<section class="nv-banner nv-banner--home">` on the homepage (`page.is_homepage`), and `<section class="nv-banner nv-banner--slim">` on every other page
    - inside it, `<svg class="nv-banner__art" viewBox="0 0 1100 300" preserveAspectRatio="xMidYMax slice">`
    - copy in `.nv-banner__copy`
    - the satellite group has `id="nv-sat"`, the orbit ellipse has `id="nv-orbit"`, and the balloon group has `id="nv-sonde"`
  - `overrides/main.html` extends `base.html`. It fills `{% block hero %}` with `{% include "partials/nv-banner.html" %}`, and Task 4 adds to its `content` block.

- [ ] **Step 1: Write the failing tests** as `class BannerTest(unittest.TestCase)`.
  - `test_home_banner`: `index.html` contains `nv-banner--home`, `>NV9P<`, the exact tagline, and each of the 4 tags as `>DM79<`, `>ITU 7<`, `>CQ 4<` and `>Rocky Mountain Div.<`. It also contains `id="nv-sat"` and `id="nv-sonde"`.
  - `test_slim_banner_on_inner_pages`: `about/index.html`, `logbook/index.html`, `blog/index.html` and the Task 1 post page each contain `nv-banner--slim` and not `nv-banner--home`. Their `.nv-banner__copy` text equals the page title, and for the blog index that title is `Blog`. The slim pages don't contain `id="nv-sat"` or `id="nv-sonde"`.
  - `test_satellite_on_orbit`: parse `cx`, `cy`, `rx` and `ry` from `#nv-orbit` and the `translate(x y)` from `#nv-sat` in `index.html`. Assert `abs(((x-cx)/rx)**2 + ((y-cy)/ry)**2 - 1) < 0.01`. Also assert that the `rotate(θ)` angle matches the tangent `atan2(ry*cos t, rx*sin t)` within 1°, where `t = acos((x-cx)/rx)`.
  - `test_duplicate_h1_hidden_by_css`: `nv9p.css` contains the rule that hides `.md-container:has(.nv-banner) .md-content__inner > h1:first-of-type`. The post page's HTML still contains its `<h1`, because only CSS hides it.
- [ ] **Step 2: Run the tests to verify they fail.** Expected: the 4 `BannerTest` tests FAIL.
- [ ] **Step 3: Implement the banner.**
  - Port the artwork from the mockup's homepage hero: the gradient `#dusk`, the three ridge paths, both dotted orbit ellipses, and the balloon group.
  - Place the satellite at the orbit point for `t = 75°` on ellipse `cx=760 cy=250 rx=560 ry=190`, which gives `translate(905 66.5) rotate(5.2)`. The test is the source of truth, so recompute if the ellipse changes.
  - The slim variant uses a 150px-tall strip, a single orbit arc, and no satellite or balloon.
  - Give each SVG its own gradient id (`nv-dusk-home` or `nv-dusk-slim`), so ids are never duplicated.
  - On the homepage, the copy is the wordmark (as a `<p>`, not an `<h1>`), the tagline and the tags. On slim pages, the copy is `page.title` as the page's visible heading.
- [ ] **Step 4: Implement the responsive CSS.**
  - Heights: about 320px on the homepage and 150px on slim pages.
  - At `max-width: 600px`, set the homepage banner to `height: 360px` and the copy `left: 16px; right: 16px`, and change the SVG's `preserveAspectRatio` to `xMaxYMax slice` through a second `<svg>` or a CSS `object-position` approach. The goal is that the balloon and satellite show on the right without overlapping the copy. The builder chooses the technique, and the screenshot check decides whether it works.
  - Long slim titles wrap.
  - Add the H1-hiding rule.
- [ ] **Step 5: Run the tests to verify they pass.** Expected: all pass.
- [ ] **Step 6: Run the visual checks.**
  - Run `.venv/bin/zensical serve`.
  - Screenshot `/`, `/about/` and `/blog/2018/04/16/high-altitude-balloon-part-1-cameras/` at 1280px and 375px.
  - Expected:
    - the satellite sits on the dotted line
    - the balloon doesn't overlap the "NV9P" or tagline text
    - the long title wraps inside the strip
    - `document.documentElement.scrollWidth <= window.innerWidth` at 375px
- [ ] **Step 7: Commit** with `git commit -m "feat(theme): Front Range banner with orbit, satellite and radiosonde; slim banner on inner pages"`, after `git add`ing the files listed for this task.

---

### Task 4: "What I'm working on right now" panel

**Files:**
- Create: `overrides/partials/nv-now.html`
- Modify: `overrides/main.html`, `zensical.toml`, `docs/stylesheets/nv9p.css`
- Test: `tests/test_build.py`

**Interfaces:**
- Consumes: `overrides/main.html` from Task 3.
- Produces: the config Casey edits.

```toml
[project.extra.now]
updated = "October 2026"

[[project.extra.now.items]]
icon = "material/radio-tower"
title = "Portable satellite tower"
text = "Building a portable tower for working 2m/70cm satellites."

[[project.extra.now.items]]
icon = "material/crosshairs-gps"
title = "Front Range sonde chasing"
text = "Tracking and recovering radiosondes after they come down along the Front Range."

[[project.extra.now.items]]
icon = "fontawesome/solid/cloud-arrow-up"
title = "Weather balloon launches"
text = "Launching my own weather balloons."
```

- [ ] **Step 1: Write the failing tests** as `class NowPanelTest(unittest.TestCase)`.
  - `test_panel_on_homepage`: `index.html` contains `class="nv-now"`, the heading `What I'm working on right now` (the apostrophe may be `&#39;`), and `updated October 2026`. The three titles appear in the order above. Each item contains an inline `<svg`.
  - `test_panel_before_intro`: the index of `nv-now` in `index.html` is lower than the index of `Welcome to the website of radio station NV9P`.
  - `test_panel_only_on_homepage`: `about/index.html` and `blog/index.html` don't contain `nv-now`.
  - `test_empty_items_renders_nothing`:
    - copy `zensical.toml` to a temp directory along with `docs/`, `overrides/`, `main.py` and `ext/`
    - set `items = []` in the copy
    - build it with `zensical build -f <tmp>/zensical.toml`, or run from `<tmp>` if `-f` isn't supported
    - assert that `nv-now` is absent from that build's `index.html`
- [ ] **Step 2: Run the tests to verify they fail.** Expected: the `NowPanelTest` tests FAIL.
- [ ] **Step 3: Implement.**
  - In `main.html`, `{% block content %}` renders `{% if page.is_homepage %}{% include "partials/nv-now.html" %}{% endif %}{{ super() }}`.
  - `nv-now.html` renders nothing unless `config.extra.now and config.extra.now.items`.
  - Icons render with `{% include ".icons/" ~ item.icon ~ ".svg" %}`. A wrong path then raises a template-not-found error and fails the build, which is the loud failure Review Focus item 5 asks for. Don't wrap it in `ignore missing`.
  - Style it as in the mockup:
    - a bordered gradient panel (`#24202b` → `#1e1f27`)
    - an orange dot with a soft ring
    - a 3-column grid that drops to 1 column at ≤700px
- [ ] **Step 4: Run the tests to verify they pass.** Expected: all pass.
- [ ] **Step 5: Run the visual check.** Screenshot `/` at 1280px and 375px. Expected: the panel matches the mockup's look, and there's no horizontal scroll.
- [ ] **Step 6: Commit** with `git commit -m "feat(theme): homepage 'What I'm working on right now' panel from config"`.

---

### Task 5: Homepage card styling, README upkeep notes, final verification

**Files:**
- Modify: `docs/stylesheets/nv9p.css`, `README.md`, `CLAUDE.md`

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Style the homepage cards.** Restyle the homepage's "Latest Blog Posts" and project sections as cards, using `--nv-panel` with a 3px `--nv-accent` top border, as in the mockup. Do it with CSS that targets the existing Markdown output under `.md-container:has(.nv-banner--home)`, and don't edit `docs/index.md`. If a section can't be targeted without markup, leave it unstyled and note it in the hand-back. Don't edit copy.
- [ ] **Step 2: Add a "Theme upkeep" section to `README.md`.**
  - Say how to edit `[project.extra.now]` (items and `updated`) and `[project.extra.station]`, with a pointer to icon names under the theme's `.icons/` directory.
  - Say that `overrides/partials/header.html` is a copy of the theme's partial, which needs re-copying after a Zensical upgrade (keeping the one-line wordmark change).
  - Say how to run `python -m unittest tests.test_build` after `zensical build`.
- [ ] **Step 3: Update `CLAUDE.md`'s Architecture section** to describe `overrides/`, `docs/stylesheets/nv9p.css`, the `[project.extra]` keys and `tests/`.
- [ ] **Step 4: Run the full verification.**
  - Run `rm -rf site && .venv/bin/zensical build && .venv/bin/python -m unittest tests.test_build -v`. Expected: every test passes, with zero failures and zero errors.
  - Search check: `zensical serve`, then search "Cloudlog", which returns the Cloudlog post.
  - Lightbox check: clicking an image in `/blog/2018/04/16/high-altitude-balloon-part-1-cameras/` opens the lightbox.
  - Blog navigation check: pagination works, and the tag and archive links from the blog index resolve.
- [ ] **Step 5: Commit** with `git add docs/stylesheets/nv9p.css README.md CLAUDE.md && git commit -m "feat(theme): homepage cards and theme upkeep docs"`.
- [ ] **Step 6: Stop before pushing.** Report to Casey. Pushing the branch, and merging to `main` (which deploys to production), each need Casey's go-ahead. Before Casey merges, they should confirm in the Cloudflare Pages dashboard:
  - the build command runs `zensical build` (or equivalent)
  - the output directory is `site`
  - `PYTHON_VERSION`/`.python-version` gives Python 3.13

  This matters because Task 1 untracked `site/`, so the deploy must not rely on committed build files.
