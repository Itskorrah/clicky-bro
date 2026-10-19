#!/usr/bin/env python3
"""Generate the Clicky Bro app icon in Assets.xcassets/AppIcon.appiconset.

The final art is authored here as deterministic, antialiased geometry: a flat ink tile with a
cobalt assistant face and a small cyan spark. Two built-in ImageGen concepts were explored on
2026-10-19; their generated raster lighting and canvas proportions did not make a clean shared
source for macOS, Windows, and the native status/tray marks, so the retained source pipeline is
code-native instead. See docs/APP_ICON.md for palette, geometry and concept provenance.

Run from the repository root: python3 app/macos/OpenClicky/scripts/make-app-icon.py
or: python3 scripts/make-app-icon.py [--preview path.png] from macos/OpenClicky.
Needs Pillow.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SCALE = 4
TILE_FRACTION = 824 / 1024  # Preserve Apple's macOS icon grid and transparent edge margin.
TILE_RADIUS_FRACTION = 185 / 1024

INK = (0x13, 0x23, 0x3B, 255)
COBALT = (0x2F, 0x81, 0xF7, 255)
PALE_CYAN = (0xA5, 0xD6, 0xFF, 255)
PAPER = (0xF0, 0xF6, 0xFC, 255)


def unit_box(tile, x0, y0, x1, y1):
    """Return a normalized rectangle in the padded icon tile."""
    inset, body = tile
    return (
        inset + round(x0 * body),
        inset + round(y0 * body),
        inset + round(x1 * body),
        inset + round(y1 * body),
    )


def draw_round_rect(draw, tile, box, radius, colour):
    bounds = unit_box(tile, *box)
    draw.rounded_rectangle(bounds, radius=round(radius * tile[1]), fill=colour)


def draw_ellipse(draw, tile, box, colour):
    draw.ellipse(unit_box(tile, *box), fill=colour)


def draw_spark(draw, tile, cx, cy, radius, shoulder, colour):
    """Draw the small four-point click spark, with a wide readable silhouette."""
    inset, body = tile
    points = [
        (cx, cy - radius),
        (cx + shoulder, cy - shoulder),
        (cx + radius, cy),
        (cx + shoulder, cy + shoulder),
        (cx, cy + radius),
        (cx - shoulder, cy + shoulder),
        (cx - radius, cy),
        (cx - shoulder, cy - shoulder),
    ]
    draw.polygon(
        [(inset + round(x * body), inset + round(y * body)) for x, y in points],
        fill=colour,
    )


def render_icon(size=1024):
    canvas = size * SCALE
    body = round(size * SCALE * TILE_FRACTION)
    inset = (canvas - body) // 2
    tile = (inset, body)
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (inset, inset, inset + body, inset + body),
        radius=round(size * SCALE * TILE_RADIUS_FRACTION),
        fill=INK,
    )

    # Feet, then the single rounded head. Keep the shape broad and high-contrast at 16 px.
    draw_round_rect(draw, tile, (0.31, 0.66, 0.445, 0.79), 0.055, COBALT)
    draw_round_rect(draw, tile, (0.555, 0.66, 0.69, 0.79), 0.055, COBALT)
    draw_round_rect(draw, tile, (0.21, 0.27, 0.79, 0.73), 0.15, COBALT)

    # Simple faceplate and two dark eyes keep the companion readable without tiny decoration.
    draw_round_rect(draw, tile, (0.285, 0.36, 0.715, 0.63), 0.105, PAPER)
    draw_ellipse(draw, tile, (0.385, 0.455, 0.455, 0.545), INK)
    draw_ellipse(draw, tile, (0.545, 0.455, 0.615, 0.545), INK)

    # The bright spark is attached to the head's upper-right edge and stays distinct on the tile.
    draw_spark(draw, tile, cx=0.755, cy=0.30, radius=0.13, shoulder=0.033, colour=PALE_CYAN)
    output = image.resize((size, size), Image.Resampling.LANCZOS)
    if size <= 32:
        # Large downsampling filters can bleed a faint halo into the one-pixel transparent margin.
        pixels = output.load()
        for coordinate in range(size):
            pixels[coordinate, 0] = (0, 0, 0, 0)
            pixels[coordinate, size - 1] = (0, 0, 0, 0)
            pixels[0, coordinate] = (0, 0, 0, 0)
            pixels[size - 1, coordinate] = (0, 0, 0, 0)
    return output


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        render_icon().save(sys.argv[2])
        print("preview", sys.argv[2])
        return
    out = Path(__file__).resolve().parent.parent / "OpenClicky/Assets.xcassets/AppIcon.appiconset"
    for size in (16, 32, 64, 128, 256, 512, 1024):
        render_icon(size).save(out / f"{size}-mac.png")
    print("wrote", out)


if __name__ == "__main__":
    main()
