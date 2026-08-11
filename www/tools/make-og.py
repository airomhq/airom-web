#!/usr/bin/env python3
"""Generate www/og.png, the 1200x630 social preview card.

Committed as a script rather than just a PNG so the image is reproducible: when
the tagline or the mark changes, this regenerates it instead of someone having
to reverse-engineer a binary in the repo.

    python3 www/tools/make-og.py

Requires Pillow. Uses only fonts that ship with macOS; falls back to DejaVu
(present on most Linux CI images) so it also runs in a container.
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630

BG = (7, 11, 24)
FG = (236, 239, 246)
MUTED = (154, 164, 187)
ACCENT = (139, 147, 255)
INDIGO = (79, 70, 229)
BORDER = (27, 36, 56)

OUT = pathlib.Path(__file__).resolve().parents[1] / "og.png"

# (path, index-within-collection). macOS ships variable/collection fonts, so the
# bold face is selected by index rather than by a separate file.
FONT_CANDIDATES = {
    "bold": [
        ("/System/Library/Fonts/SFNSDisplay.ttf", 0),
        ("/System/Library/Fonts/Helvetica.ttc", 1),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 0),
    ],
    "regular": [
        ("/System/Library/Fonts/SFNSText.ttf", 0),
        ("/System/Library/Fonts/Helvetica.ttc", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
    ],
    "mono": [
        ("/System/Library/Fonts/Menlo.ttc", 0),
        ("/System/Library/Fonts/Monaco.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0),
    ],
}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for path, index in FONT_CANDIDATES[kind]:
        if pathlib.Path(path).exists():
            try:
                return ImageFont.truetype(path, size, index=index)
            except OSError:
                continue
    print(f"warning: no {kind} font found; falling back to the PIL default", file=sys.stderr)
    return ImageFont.load_default(size)


def rounded(draw: ImageDraw.ImageDraw, box, radius, **kw) -> None:
    draw.rounded_rectangle(box, radius=radius, **kw)


def mark(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """The AIROM mark: three nested ridges, matching www/favicon.svg.

    The canvas is flat RGB with no alpha, so the two receding ridges are
    pre-blended against the background rather than drawn translucent. Pillow
    has no round line caps either, so each vertex is stamped with a circle of
    the stroke's radius to match the SVG's stroke-linecap="round".
    """
    s = size / 32.0
    w = max(1, round(3.2 * s))
    r = w / 2.0

    def blend(fg, bg, a):
        return tuple(round(b + a * (f - b)) for f, b in zip(fg, bg))

    def ridge(points, colour):
        pts = [(x + px * s, y + py * s) for px, py in points]
        draw.line(pts, fill=colour, width=w, joint="curve")
        for cx, cy in pts:
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colour)

    ridge([(3.2, 23.5), (16, 10.7), (28.8, 23.5)], blend(FG, BG, 0.26))
    ridge([(6.6, 18.9), (16, 9.5), (25.4, 18.9)], blend(FG, BG, 0.55))
    ridge([(10, 14.5), (16, 8.5), (22, 14.5)], ACCENT)


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # A soft indigo wash behind the headline. One ellipse blurred hard, rather
    # than a stack of translucent ones: stacking leaves a visible seam at the
    # outermost radius, which reads as a hard circular edge on a dark card.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-260, -170, 900, 770), fill=(79, 70, 229, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(190))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    pad = 84

    mark(d, pad, pad - 10, 64)
    d.text((pad + 84, pad + 6), "AIROM", font=font("bold", 42), fill=FG)

    d.text(
        (pad, 224),
        "Find the AI in your code,",
        font=font("bold", 68),
        fill=FG,
    )
    d.text(
        (pad, 304),
        "and prove it.",
        font=font("bold", 68),
        fill=FG,
    )

    d.text(
        (pad, 412),
        "An AI Bill of Materials scanner. Every component carries",
        font=font("regular", 27),
        fill=MUTED,
    )
    d.text(
        (pad, 450),
        "the file:line it was seen at.",
        font=font("regular", 27),
        fill=MUTED,
    )

    # Install pill.
    chip = font("mono", 25)
    text = "$ pip install airom"
    tw = d.textlength(text, font=chip)
    box = (pad, 522, pad + tw + 56, 522 + 62)
    rounded(d, box, radius=12, fill=(20, 23, 31), outline=BORDER, width=1)
    d.text((pad + 28, 522 + 17), text, font=chip, fill=ACCENT)

    d.text(
        (W - pad, 556),
        "airom.dev",
        font=font("regular", 25),
        fill=MUTED,
        anchor="rs",
    )

    # A hairline accent along the bottom edge — the "evidence baseline" again.
    d.rectangle((0, H - 6, W, H), fill=INDIGO)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
