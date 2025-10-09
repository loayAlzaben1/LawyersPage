Place the following icon files in this directory (recommended sizes and filenames):

- favicon-16x16.png (16x16)
- favicon-32x32.png (32x32)
- apple-touch-icon.png (180x180)
- android-chrome-192x192.png (192x192)
- android-chrome-512x512.png (512x512)
- safari-pinned-tab.svg (monochrome SVG used by Safari pinned tabs)

Create a recognisable lawyer-themed favicon (e.g. scales of justice, stylised 'L', or initials) and export it at the sizes above. If you have a vector source (SVG) provide `favicon.svg` too (already referenced in `base.html`).

After adding the files, run `python manage.py collectstatic` on the server and reload the web app so browsers pick up the new icons and manifest.
