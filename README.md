# Photo Album

A warm & vintage static photo album that auto-builds via GitHub Actions and deploys to GitHub Pages.

## How it works

```
repo/
├── photos/               ← drop your images here
│   ├── beach.jpg
│   └── mountain.png
├── build_album.py        ← scans photos/ and writes index.html
├── index.html            ← auto-generated, do not edit by hand
└── .github/
    └── workflows/
        └── build-album.yml
```

Every push to `main` that touches `photos/` or `build_album.py` automatically:

1. Runs `build_album.py` to generate `index.html`
2. Commits the updated `index.html` back to `main`
3. Deploys the site to GitHub Pages

## Setup (one-time)

1. **Enable GitHub Pages** in your repo settings:  
   *Settings → Pages → Source → GitHub Actions*

2. **Add your photos** to the `photos/` directory, commit, and push.

3. That's it — the action does the rest.

## Customise the title

**Option A — edit the workflow default** (permanent):  
Open `.github/workflows/build-album.yml` and change `ALBUM_TITLE`.

**Option B — manual run with a custom title** (one-off):  
Go to *Actions → Build & Deploy Photo Album → Run workflow* and type your title in the input box.

**Option C — run locally**:

```bash
python build_album.py --title "Summer 2025" --subtitle "Pacific Coast Road Trip"
```

## Supported image formats

`.jpg` · `.jpeg` · `.png` · `.gif` · `.webp` · `.avif`

Photos are sorted alphabetically. Prefix filenames with numbers to control order:  
`01-arrival.jpg`, `02-beach.jpg`, `03-sunset.jpg`
