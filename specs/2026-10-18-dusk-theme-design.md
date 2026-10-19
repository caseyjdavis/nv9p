# NV9P "Front Range at Dusk" Theme — Design

Date: 2026-10-18
Status: Draft, awaiting approval
Reference mockup: `specs/2026-10-18-dusk-theme-mockup.html` (open in a browser)

## Intent

nv9p.com is Casey's (NV9P) amateur radio blog. It currently runs the stock Zensical theme (dark `slate` scheme, deep-orange accent, broadcast-tower logo), with no custom CSS or template overrides. That look says nothing about who the station is.

Casey's current focus in the hobby is:

- working satellites on 2m and 70cm
- chasing radiosondes (weather balloon sondes) along the Front Range
- launching weather balloons
- all of it from Colorado

The theme should make that obvious within a few seconds of landing on the site: the Colorado mountains on one side, the sky with satellite orbits and a weather balloon on the other.

## Goals

1. **A dusk color scheme across the whole site.** The sky gradient runs deep navy `#1b1f3a` → plum `#6a3a5c` → sunset orange `#ff7043` → amber `#ffb74d`. The Front Range ridges are dark layered plum/purple silhouettes (`#4a2f4a`, `#2a1f33`, `#17131f`). Deep orange (`#ff7043`, the site's current accent) stays the accent for links, active nav and highlights, and peach (`#ffd9c2`) is used for secondary header text. The reading area stays a calm dark gray, so long posts remain comfortable to read.
2. **Header logo:** replace the broadcast-tower icon with the theme's bundled satellite icon (`fontawesome/solid/satellite`). Casey explicitly chose the theme icon over an emoji. The favicon should match (a satellite, not the tower).
3. **Homepage banner (large).** A full-width illustrated banner, drawn as SVG rather than a photo so it stays sharp and light. Contents:
   - a layered mountain skyline along the bottom
   - a faint dotted elliptical orbit across the sky with a small satellite sitting **exactly on** the orbit line and rotated to follow its tangent (Casey specifically flagged misalignment in an earlier mockup)
   - a radiosonde weather balloon in the sky: the balloon, a small parachute, and the sonde box hanging on a line
   - "NV9P" large, the tagline "Working satellites from the Colorado Rockies", and small monospace tags: `DM79` (grid square), `ITU 7`, `CQ 4`, `Rocky Mountain Div.` (ARRL division), with exact label text left to the builder. These replace the earlier 2m/70cm band tags at Casey's request
   - the site navigation over the banner
4. **Inner pages (slim banner).** Blog posts, Logbook, QSL Cards, About and the blog index get a shorter strip of the same sky and skyline, with the page title in it. The strip has no satellite or balloon (an orbit arc is fine), so every page feels like the same site without each one opening on a giant banner.
5. **"What I'm working on right now" panel** on the homepage, placed between the banner and the existing content. It has a small orange dot, a heading, an "updated <Month Year>" note, and one short item per project (icon, bold headline, one sentence). The starting content:
   - **Portable satellite tower:** building a portable tower for working 2m/70cm satellites.
   - **Front Range sonde chasing:** tracking and recovering radiosondes after they come down along the Front Range.
   - **Weather balloon launches:** launching my own weather balloons.

   The descriptions are draft wording for Casey to adjust. Icons come from the theme's bundled icon sets, not emoji.
6. **Easy upkeep.** Casey must be able to change the "right now" items and the updated date by editing Markdown or simple config, with no Python, HTML or CSS involved.
7. **The homepage below the panel** keeps its existing content and order: intro paragraph, latest posts (via the `recent_posts` macro) and the project sections. Restyling them, for example as cards with an orange top edge like the mockup, is in scope. Rewriting the text is not.

## Non-goals

- No live satellite data in this round: no pass predictions, no live tracking, and no automatic pull of satellite contacts from Cloudlog.
- No rewriting of existing blog posts or page copy.
- No switch away from Zensical, and no new site generator or JS framework.
- No changes to Google Analytics, the blog URL structure or the nav entries.

## Anti-goals (a failure even if it "works")

- Breaking existing features: search, the blog (pagination, tags, archive), the glightbox image lightbox, the `recent_posts` macro on the homepage, or post URLs.
- Hurting readability of long posts, for example with busy backgrounds behind body text or low-contrast text on the gradient.
- A banner that looks broken on phones: elements overlapping the callsign text, or the satellite drifting off the orbit when the banner is resized or cropped.
- Stock-photo feel: the illustration should look drawn and unified, like the mockup.

## Constraints

- **Platform:** Zensical, configured in `zensical.toml`. `requirements.txt` pins `zensical==0.0.71`, and `.python-version` says 3.13.
- **The local environment is stale and must be rebuilt.** `.venv` was made with the system Python 3.9.6 and contains `zensical 0.0.2`, not 0.0.71. No `zensical` command is on the PATH, and `uv`/`pyenv` aren't installed, but Homebrew is. A fresh Python 3.13 venv is needed before anything can be built or previewed. This is setup on Casey's Mac, not a site change.
- **Customization goes through the theme's supported mechanisms:** an extra stylesheet and theme template overrides (`custom_dir`, overriding blocks of the base template), the Material-for-MkDocs-compatible approach that Zensical carries forward. The builder should confirm the exact config keys against the Zensical 0.0.71 docs. Don't fork or vendor the theme.
- **Light/dark:** the site is dark-only (`slate`) today, and it stays dark-only.
- **Nothing that is only for planning goes under `docs/`,** because everything there is published. That's why this spec lives in `specs/`.
- **Deployment:** Cloudflare Pages watches the GitHub repo (`caseyjdavis/nv9p`) and builds the site itself whenever something is pushed. A push to `main` therefore goes live, so all theme work happens on a feature branch, and it's merged only after Casey has seen it. A Cloudflare preview deployment of the branch, if enabled, or `zensical serve` locally are the ways to look at it first. Because Cloudflare builds from source, the theme work commits **source only** and never commits `site/` output. Cloudflare's build must be able to install `zensical==0.0.71` on Python 3.13, and any new build dependency must be added to `requirements.txt`.
- **Phone widths must work:** 16px side gutters, no horizontal scroll, and the banner text stays legible.
- **`site/` is listed in `.gitignore` but 129 built files are still tracked,** and the working tree has uncommitted rebuilt output from the Zensical migration. Don't fold theme work into those changes.

## Decided (by Casey)

- Front Range at Dusk colors, chosen over the "Night Pass" (navy/cyan) and "Topo & Telemetry" (green console) directions.
- A satellite icon to the left of "NV9P" in the header, using the theme's bundled icon rather than an emoji.
- Mountain skyline plus sky orbits as the core motif.
- A radiosonde weather balloon in the header image.
- A "What I'm working on right now" section on the homepage, with the three items above.
- The slim banner on inner pages: Casey agreed with the overall playback that included it.

## Calls made by Claude (Casey can override)

- The banner and skyline are inline SVG, not photos.
- The skyline is a stylized Front Range rather than a traced real profile. It's a plus, not a requirement, if Pikes Peak (or the profile of Casey's local view) is recognizable.
- The tagline wording is "Working satellites from the Colorado Rockies".
- **Navigation layout:** keep Zensical's stock sticky header bar (with search), recolored to sit seamlessly on top of the dusk sky. Turn on the `navigation.tabs` feature so the five nav entries show as a horizontal row of links, as in the mockup. The banner sits directly under the header. Sidebars stay where the theme puts them, so the blog's archive, tags and pagination keep working. On phones, use the theme's normal hamburger drawer. The mockup's "links over the banner" look is the target feel, not a literal layout.
- **Header wordmark:** show "NV9P" next to the satellite icon by overriding the header template. Don't change `site_name` ("NV9P Amateur Radio"), so page `<title>`s and SEO stay the same.
- **Page titles:** where the banner shows the title (the homepage's big "NV9P", the inner pages' slim-strip title), hide the duplicate H1 in the content area, via the template or CSS, without editing the Markdown. The blog index's strip title is "Blog".
- **The station tags (grid, ITU, CQ, ARRL division) live in `[project.extra]`**, so they can be edited like the "right now" items.

## Left to the builder

- The exact SVG artwork, as long as it matches the mockup's look and keeps the satellite on its orbit at all sizes. Putting both in one SVG coordinate system, and cropping instead of distorting, does this.
- How the "right now" content is stored, for example a block in `docs/index.md` using `attr_list`/admonition-style markup, a list in `[project.extra]` rendered by the template, or a Markdown snippet. Whatever is chosen must meet Goal 6.
- Which bundled icons to use for the three "right now" items.
- The CSS structure and the theme variables to override. Prefer Zensical/Material CSS custom properties (`--md-primary-fg-color` and similar) over brute-force overrides.
- Whether to delete the stray `package.json`/`package-lock.json`. They depend on `mkdocs-material ^0.0.1-security`, npm's empty placeholder for a removed package, which does nothing. Mention it to Casey rather than removing it silently.
