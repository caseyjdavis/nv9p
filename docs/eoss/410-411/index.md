---
title: EOSS-410 and EOSS-411
full_width: true
hide:
  - toc
---

# EOSS-410 and EOSS-411

**November 14, 2026 · Eastern Colorado plains**

Two balloons went up the same morning from the same launch site, and one chase vehicle followed both. EOSS-410 peaked at about 87,450 ft and EOSS-411 at about 86,480 ft before both came down northeast of the launch site.

<div class="nv-embed">
  <iframe src="flight-day.html" title="Interactive flight replay, sounding and wind tower for EOSS-410 and EOSS-411" allowfullscreen></iframe>
</div>

[Open the flight viewer full screen :material-open-in-new:](flight-day.html){ target="_blank" rel="noopener" .md-button }

The viewer has three tabs:

- **Flight replay**: both flight paths and the chase route in 3D over USGS aerial imagery, with a playback clock.
- **Sounding**: temperature, pressure and other readings from the ascent, plotted against altitude.
- **Wind tower**: wind speed and direction at each altitude, stacked in 3D.

The 3D tabs need WebGL. On a phone, the full screen viewer is easier to use.

## Telemetry

The raw data behind the viewer, as CSV:

- [EOSL-410.csv](EOSL-410.csv): APRS packets from EOSS-410
- [EOSL-411.csv](EOSL-411.csv): APRS packets from EOSS-411
- [chase-gps.csv](chase-gps.csv): GPS log from the chase vehicle
