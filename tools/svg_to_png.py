from pathlib import Path
import sys

from cairosvg import svg2png


def convert(svg_path: Path, png_path: Path, size: int = 1024):
    svg = svg_path.read_bytes()
    # cairosvg can scale by target width/height via output_width/outpu_height
    svg2png(bytestring=svg, write_to=str(png_path), output_width=size, output_height=size)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: svg_to_png.py <input.svg> <output.png> [size]')
        sys.exit(2)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    convert(inp, out, size)
