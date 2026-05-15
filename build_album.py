#!/usr/bin/env python3
"""
build_album.py — Generates index.html from all images in the photos/ directory.

Usage:
    python build_album.py [--title "My Album"] [--photos-dir photos] [--output index.html]
"""

import argparse
import os
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

ALBUM_TITLE      = "Our Little Album"          # Default title (override with --title)
ALBUM_SUBTITLE   = "A collection of memories"  # Subtitle shown beneath the title
PHOTOS_DIR       = "photos"                    # Directory scanned for images
OUTPUT_FILE      = "index.html"               # Output HTML file

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

# ── Template ──────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lora:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --cream: #f5f0e8;
    --parchment: #ede4d0;
    --warm-tan: #c9a96e;
    --sepia-dark: #5c3d1e;
    --sepia-mid: #8b6340;
    --sepia-light: #b89060;
    --ink: #2e1f0f;
  }}

  body {{
    background-color: var(--cream);
    background-image:
      radial-gradient(ellipse at 20% 10%, rgba(201,169,110,0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 90%, rgba(139,99,64,0.12) 0%, transparent 50%);
    font-family: 'Lora', Georgia, serif;
    color: var(--ink);
    min-height: 100vh;
  }}

  header {{
    text-align: center;
    padding: 4rem 2rem 2.5rem;
  }}
  header::before, header::after {{
    content: '';
    display: block;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--warm-tan), transparent);
    margin: 0 auto;
    max-width: 500px;
  }}
  header::before {{ margin-bottom: 2rem; }}
  header::after  {{ margin-top: 2rem; }}

  .album-eyebrow {{
    font-family: 'Lora', serif;
    font-style: italic;
    font-size: 0.85rem;
    letter-spacing: 0.18em;
    color: var(--sepia-mid);
    text-transform: uppercase;
    margin-bottom: 0.75rem;
  }}

  h1 {{
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 400;
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    line-height: 1.15;
    color: var(--sepia-dark);
  }}

  h1 em {{
    font-style: italic;
    color: var(--sepia-mid);
  }}

  .album-subtitle {{
    margin-top: 0.6rem;
    font-size: 0.95rem;
    color: var(--sepia-light);
    letter-spacing: 0.04em;
  }}

  .gallery {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 1rem 2rem 5rem;
    columns: 3;
    column-gap: 1.5rem;
  }}
  @media (max-width: 800px) {{ .gallery {{ columns: 2; }} }}
  @media (max-width: 520px) {{ .gallery {{ columns: 1; }} }}

  .photo-card {{
    break-inside: avoid;
    margin-bottom: 1.5rem;
    cursor: pointer;
    position: relative;
    display: block;
  }}

  .photo-card:focus-visible {{
    outline: 2px solid var(--warm-tan);
    outline-offset: 3px;
    border-radius: 2px;
  }}

  .photo-frame {{
    background: #fff;
    padding: 10px;
    box-shadow: 0 2px 8px rgba(92,61,30,0.13), 0 0 0 1px rgba(92,61,30,0.07);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
  }}

  .photo-card:hover .photo-frame {{
    transform: translateY(-3px) rotate(0.3deg);
    box-shadow: 0 8px 24px rgba(92,61,30,0.2), 0 0 0 1px rgba(92,61,30,0.1);
  }}

  .photo-frame img {{
    width: 100%;
    display: block;
    filter: sepia(18%) contrast(1.04) brightness(0.97) saturate(0.9);
    transition: filter 0.3s ease;
  }}

  .photo-card:hover .photo-frame img {{
    filter: sepia(8%) contrast(1.06) brightness(1.0) saturate(1.0);
  }}

  .photo-card::before {{
    content: '';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%) rotate(-1deg);
    width: 52px;
    height: 18px;
    background: rgba(201,169,110,0.35);
    border: 1px solid rgba(201,169,110,0.5);
    z-index: 2;
    pointer-events: none;
  }}
  .photo-card:nth-child(even)::before  {{ transform: translateX(-50%) rotate(1.5deg);  left: 40%; }}
  .photo-card:nth-child(3n)::before   {{ transform: translateX(-50%) rotate(-2deg);   left: 60%; }}

  /* ─── Lightbox ─── */
  #lightbox {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(20, 12, 4, 0.88);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    animation: lbFadeIn 0.25s ease;
  }}
  #lightbox.active {{ display: flex; }}

  @keyframes lbFadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
  }}

  .lb-inner {{
    position: relative;
    max-width: 860px;
    width: 100%;
    animation: lbScale 0.25s ease;
  }}
  @keyframes lbScale {{
    from {{ transform: scale(0.94); opacity: 0; }}
    to   {{ transform: scale(1);    opacity: 1; }}
  }}

  .lb-frame {{
    background: #fff;
    padding: 12px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }}

  .lb-frame img {{
    width: 100%;
    display: block;
    max-height: 80vh;
    object-fit: contain;
    filter: sepia(10%) contrast(1.03) brightness(0.98);
  }}

  .lb-close {{
    position: absolute;
    top: -14px;
    right: -14px;
    width: 32px;
    height: 32px;
    background: var(--parchment);
    border: 1px solid var(--warm-tan);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: var(--sepia-dark);
    line-height: 1;
    transition: background 0.15s;
    z-index: 10;
  }}
  .lb-close:hover {{ background: var(--warm-tan); color: #fff; }}

  .lb-nav {{
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 38px;
    height: 38px;
    background: rgba(237,228,208,0.85);
    border: 1px solid var(--warm-tan);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    color: var(--sepia-dark);
    transition: background 0.15s;
    z-index: 10;
  }}
  .lb-nav:hover {{ background: var(--warm-tan); color: #fff; }}
  .lb-prev {{ left: -52px; }}
  .lb-next {{ right: -52px; }}
  @media (max-width: 700px) {{
    .lb-prev {{ left: -18px; }}
    .lb-next {{ right: -18px; }}
  }}

  .lb-counter {{
    position: absolute;
    bottom: -28px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.72rem;
    color: rgba(237,228,208,0.5);
    font-family: 'Lora', serif;
    font-style: italic;
    letter-spacing: 0.1em;
    white-space: nowrap;
  }}

  footer {{
    text-align: center;
    padding: 2rem;
    font-size: 0.75rem;
    font-style: italic;
    color: var(--sepia-light);
    opacity: 0.7;
  }}
</style>
</head>
<body>

<header>
  <p class="album-eyebrow">{subtitle}</p>
  <h1>{title_html}</h1>
</header>

<main class="gallery" id="gallery">
{photo_cards}
</main>

<div id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
  <div class="lb-inner">
    <button class="lb-close" id="lb-close" aria-label="Close">&times;</button>
    <button class="lb-nav lb-prev" id="lb-prev" aria-label="Previous photo">&#8592;</button>
    <div class="lb-frame">
      <img id="lb-img" src="" alt="">
    </div>
    <button class="lb-nav lb-next" id="lb-next" aria-label="Next photo">&#8594;</button>
    <span class="lb-counter" id="lb-counter"></span>
  </div>
</div>

<footer>
  &ldquo;In photographs, memory finds its most tender keeper.&rdquo;
</footer>

<script>
  const cards  = Array.from(document.querySelectorAll('.photo-card'));
  const lb     = document.getElementById('lightbox');
  const lbImg  = document.getElementById('lb-img');
  const lbCnt  = document.getElementById('lb-counter');
  let current  = 0;

  function openLightbox(idx) {{
    current = ((idx % cards.length) + cards.length) % cards.length;
    const img = cards[current].querySelector('img');
    lbImg.src = img.src;
    lbImg.alt = img.alt;
    lbCnt.textContent = (current + 1) + ' / ' + cards.length;
    lb.classList.add('active');
    document.body.style.overflow = 'hidden';
  }}

  function closeLightbox() {{
    lb.classList.remove('active');
    document.body.style.overflow = '';
  }}

  cards.forEach((card, i) => {{
    card.addEventListener('click',   () => openLightbox(i));
    card.addEventListener('keydown', e => {{ if (e.key === 'Enter' || e.key === ' ') openLightbox(i); }});
  }});

  document.getElementById('lb-close').addEventListener('click', closeLightbox);
  document.getElementById('lb-prev') .addEventListener('click', () => openLightbox(current - 1));
  document.getElementById('lb-next') .addEventListener('click', () => openLightbox(current + 1));

  lb.addEventListener('click', e => {{ if (e.target === lb) closeLightbox(); }});

  document.addEventListener('keydown', e => {{
    if (!lb.classList.contains('active')) return;
    if (e.key === 'Escape')     closeLightbox();
    if (e.key === 'ArrowLeft')  openLightbox(current - 1);
    if (e.key === 'ArrowRight') openLightbox(current + 1);
  }});
</script>
</body>
</html>
"""

PHOTO_CARD_TEMPLATE = """\
  <div class="photo-card" tabindex="0" data-index="{index}">
    <div class="photo-frame">
      <img src="{src}" alt="{alt}" loading="lazy">
    </div>
  </div>"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_title_html(title: str) -> str:
    """Wrap the last word of the title in <em> for the vintage italic accent."""
    words = title.strip().split()
    if len(words) <= 1:
        return title
    return " ".join(words[:-1]) + f" <em>{words[-1]}</em>"


def collect_photos(photos_dir: Path) -> list[Path]:
    if not photos_dir.exists():
        print(f"[warn] Photos directory '{photos_dir}' not found — creating it.")
        photos_dir.mkdir(parents=True)
        return []

    photos = sorted(
        p for p in photos_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return photos


def build_photo_cards(photos: list[Path], photos_dir: Path) -> str:
    if not photos:
        return '  <p style="text-align:center;color:#b89060;font-style:italic;padding:4rem 0;">No photos found in the photos/ directory.</p>'

    cards = []
    for i, photo in enumerate(photos):
        # Use a relative path from the output file (repo root)
        rel_path = photo.as_posix()
        alt = photo.stem.replace("-", " ").replace("_", " ").title()
        cards.append(PHOTO_CARD_TEMPLATE.format(index=i, src=rel_path, alt=alt))
    return "\n".join(cards)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Build the photo album HTML page.")
    parser.add_argument("--title",      default=ALBUM_TITLE,    help="Album title shown in the header")
    parser.add_argument("--subtitle",   default=ALBUM_SUBTITLE, help="Subtitle / eyebrow text")
    parser.add_argument("--photos-dir", default=PHOTOS_DIR,     help="Directory containing photos")
    parser.add_argument("--output",     default=OUTPUT_FILE,    help="Output HTML file path")
    args = parser.parse_args()

    photos_dir  = Path(args.photos_dir)
    output_path = Path(args.output)

    photos = collect_photos(photos_dir)
    print(f"[info] Found {len(photos)} photo(s) in '{photos_dir}'")

    photo_cards = build_photo_cards(photos, photos_dir)
    title_html  = make_title_html(args.title)

    html = HTML_TEMPLATE.format(
        title       = args.title,
        subtitle    = args.subtitle,
        title_html  = title_html,
        photo_cards = photo_cards,
    )

    output_path.write_text(html, encoding="utf-8")
    print(f"[info] Written → {output_path}  ({len(photos)} photo(s))")


if __name__ == "__main__":
    main()
