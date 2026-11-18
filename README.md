# Plant Care

Matt's indoor succulent and cactus care guide: every plant with its photo, watering block, light, soil, rot risk and dog safety. It's a small installable web app (PWA) that works offline.

## Editing

All content lives in `plants.json`, and photos live in `photos/`. To add or change a plant, edit `plants.json` (and drop a photo in `photos/`), then rebuild:

```
python3 build.py
```

This writes `index.html`, with the photos embedded. Commit both files.

## Hosting

GitHub Pages serves this repo from `main` at the root. Open the site in Chrome, then use **Install app** at the top, or Chrome's menu → Install, to add it to your phone or computer.
