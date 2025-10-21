from pathlib import Path
import sys
from playwright.sync_api import sync_playwright


def convert(svg_path: Path, png_path: Path, size: int = 1024):
    svg_abs = svg_path.resolve()
    file_url = svg_abs.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": size, "height": size}, device_scale_factor=1)
        page = context.new_page()
        # Ensure white background so transparent regions become white
        page.goto(file_url)
        # SVG files opened directly may not have a <body>; guard against null
        page.evaluate(
            "() => { if (document.documentElement) document.documentElement.style.background = 'white'; if (document.body) document.body.style.background = 'white'; }"
        )
        # Wait a bit for rendering
        page.wait_for_timeout(250)
        # Screenshot the viewport (which is square)
        page.screenshot(path=str(png_path), type="png", full_page=False)
        browser.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: svg_to_png_playwright.py <input.svg> <output.png> [size]')
        sys.exit(2)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    out.parent.mkdir(parents=True, exist_ok=True)
    convert(inp, out, size)
