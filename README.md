# NV9P Amateur Radio
## A blog about ham radio

My interest in amateur radio began in 2013 when I was living in Colorado Springs. I had no idea this whole other world of amateur radio existed and when I started to learn about it I knew I had to get involved. I studied for the Technician exam and found the exam was being offered at a local church. I went in one Saturday and passed both the Technician and General exam sessions and was given the callsign KE0BUI.

After a year of contacts and listening and a lot of studying I upgraded my license to Amateur Extra in Fort Collins and given the callsign AD0OW. I used mainly 2m and 70cm bands during this time with a Yaesu FT60R handi-talkie. I got to know the guys at the CSU Amateur Radio Club and learned a lot about repeaters. We overhauled the W0QEY repeater on the CSU campus for the first time in 30 years!

I requested a vanity callsign from the FCC and received the callsign NV9P on the 29th of May, 2015. I work the 40m and 20m bands on phone and PSK31. Lately I have been researching antenna options to expand my band capabilities and distance.

73, Casey NV9P

## Setup

The site is built with [Zensical](https://zensical.org), which requires Python 3.11 or newer.

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Editing and Previewing

Start the local development server with live reload:

```bash
zensical serve
```

The site will be available at `http://localhost:8000`. Changes to any markdown file will reload automatically.

Blog posts live in `docs/blog/posts/`. Each post requires YAML frontmatter at the top:

```yaml
---
title: Your Post Title
date:
  created: 2024-01-15
readtime: 5
tags:
  - tag1
---
```

## Deploying

Build the static site:

```bash
zensical build
```

The output is generated in the `site/` directory and can be deployed to any static hosting provider. Site configuration lives in `zensical.toml`.

## Theme Upkeep

The site uses a custom "Front Range at Dusk" theme layered on top of Zensical's stock theme. Everything you'd normally change lives in `zensical.toml`, so no HTML or CSS is needed.

**"What I'm working on right now"** (homepage panel): edit `[project.extra.now]`. Change `updated`, and add, remove or reorder the `[[project.extra.now.items]]` blocks. Each item has an `icon`, a `title` and a short `text`. If you remove every item, the panel disappears.

```toml
[[project.extra.now.items]]
icon = "material/radio-tower"
title = "Portable satellite tower"
text = "Building a portable tower for working 2m/70cm satellites."
```

Icon names are paths under the theme's icon folder, `.venv/lib/python3.13/site-packages/zensical/templates/.icons/`, for example `material/<name>` or `fontawesome/solid/<name>`, without the `.svg` extension. A misspelled icon name stops the build with a "template not found" error.

**Banner tagline and station tags:** edit `[project.extra.station]` (`tagline` and `tags`).

**Where the theme lives:**
- `overrides/main.html`: adds the banner and the "right now" panel to every page.
- `overrides/partials/nv-banner.html`: the mountain, orbit, satellite and radiosonde artwork.
- `overrides/partials/nv-now.html`: the "right now" panel.
- `overrides/partials/header.html`: a copy of the theme's header with one change, which shows `extra.wordmark` ("NV9P") instead of the site name. After upgrading Zensical, copy the new `partials/header.html` over it and reapply that one line.
- `docs/stylesheets/nv9p.css`: colors and layout.

**Checking a build:**

```bash
zensical build
python -m unittest tests.test_build -v
```
