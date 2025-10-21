Place your hero background images in this folder to be used as the homepage fallback.

Recommended filenames:
- hero-backyard.jpg  # default fallback referenced by templates
- hero-backyard.webp # prefer WebP when available

Optional responsive variants (recommended):
- hero-backyard-800.webp
- hero-backyard-1600.webp

Tips:
- Optimize images for web (Squoosh, ImageOptim, cwebp). Aim for <400KB for large background images.
- Keep wide aspect ratios (16:9 or 16:7) so the image crops well on desktop.
- After adding files, run the dev server and hard-refresh the homepage (Ctrl+F5) to see changes.

Production: If you deploy to a server, run `python manage.py collectstatic` to copy these files to STATIC_ROOT.
