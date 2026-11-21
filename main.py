#!/usr/bin/env python3
"""news-image-20261121 -- the world in one image, Saturday 21 November 2026.

Draws the front page of a newspaper for 21 November 2026 and writes it as
a 1024x1024 PNG to entry.png. Everything is built by hand from the Python
standard library only (math, os, struct, sys, zlib): the PNG encoder, the
5x7 bitmap type, the skyline-and-bridges illustration, every rule and
letter of the page.

No network, no randomness, no clock: two runs write byte-identical files.
Run it with `python3 main.py` -- it writes entry.png next to the script,
or into $MAKEFUN_OUTPUT_DIR when that is set (the grader's /output).
"""

import hashlib
import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024
EDGE = 16          # outer frame inset
GUTTER = 40        # text margin inside the frame

# ---------------------------------------------------------------------------
# Palette: warm newsprint, ink, one red accent, and a night panel for art.
# ---------------------------------------------------------------------------
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (158, 28, 28)
SLATE = (84, 84, 78)
FAINT = (196, 188, 172)
NIGHT = (18, 30, 44)
NIGHTLINE = (214, 222, 230)
RIVER = (70, 108, 140)
AMBER = (245, 197, 66)
SMOKE = (150, 158, 168)

# ---------------------------------------------------------------------------
# 5x7 bitmap type. Each glyph is seven rows of five cells; '#' is ink,
# ' ' is blank. Only capitals, digits and the punctuation this page uses.
# ---------------------------------------------------------------------------
GLYPHS = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"),
    "3": ("#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": ("  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", "  #  ", " #   "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "  ## ", "  #  ", "     ", "  #  "),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "*": ("     ", "# # #", " ### ", "# # #", "     ", "     ", "     "),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
}
UNKNOWN = (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### ")


def glyph_rows(ch):
    """Rows of a glyph; unknown characters fall back to a hollow box."""
    return GLYPHS.get(ch, UNKNOWN)


def text_px(text, scale):
    """Width in pixels of `text` drawn at `scale` (6 px per cell)."""
    return len(text) * 6 * scale


def wrap(text, chars_per_line):
    """Greedy word wrap into lines of at most `chars_per_line` characters."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= chars_per_line:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Sheet: an RGB canvas with small drawing tools.
# ---------------------------------------------------------------------------
class Sheet:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def _pos(self, x, y):
        return (y * self.width + x) * 3

    def dot(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            p = self._pos(x, y)
            self.pixels[p:p + 3] = bytes(colour)

    def block(self, x, y, w, h, colour):
        """Filled rectangle, clipped to the canvas."""
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            p = self._pos(x0, yy)
            self.pixels[p:p + len(row)] = row

    def frame(self, x, y, w, h, colour, thick=1):
        self.block(x, y, w, thick, colour)
        self.block(x, y + h - thick, w, thick, colour)
        self.block(x, y, thick, h, colour)
        self.block(x + w - thick, y, thick, h, colour)

    def hbar(self, x, y, w, colour, thick=1):
        self.block(x, y, w, thick, colour)

    def vbar(self, x, y, h, colour, thick=1):
        self.block(x, y, thick, h, colour)

    def segment(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line with a square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.block(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def blob(self, cx, cy, r, colour):
        """Filled disc."""
        for yy in range(cy - r, cy + r + 1):
            span = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.block(cx - span, yy, 2 * span + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        """Thin circle outline."""
        steps = max(24, int(2 * math.pi * r))
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            self.block(int(cx + r * math.cos(a)) - thick // 2,
                       int(cy + r * math.sin(a)) - thick // 2,
                       thick, thick, colour)

    def arch(self, cx, base_y, rx, ry, colour, thick=3):
        """Upper half of an ellipse: a bridge span."""
        steps = 90
        prev = None
        for i in range(steps + 1):
            a = math.pi * (1 - i / steps)  # pi -> 0, left to right
            px = int(cx + rx * math.cos(a))
            py = int(base_y - ry * math.sin(a))
            if prev is not None:
                self.segment(prev[0], prev[1], px, py, colour, thick)
            prev = (px, py)

    def put_text(self, text, x, y, scale, colour, align="left"):
        """Draw one line of text; y is the top of the glyphs.

        The typeface holds capitals only, so copy is set in caps --
        the paper's house style -- and lower case is folded up here
        rather than falling back to the hollow-box glyph.
        """
        text = text.upper()
        if align == "center":
            x -= text_px(text, scale) // 2
        elif align == "right":
            x -= text_px(text, scale)
        cx = x
        for ch in text:
            rows = glyph_rows(ch)
            for row_i, row in enumerate(rows):
                for col_i, cell in enumerate(row):
                    if cell == "#":
                        self.block(cx + col_i * scale, y + row_i * scale,
                                   scale, scale, colour)
            cx += 6 * scale
        return y + 7 * scale

    def paragraph(self, text, x, y, width_px, scale, colour, leading=None):
        """Wrapped paragraph; returns the y just below the last line."""
        if leading is None:
            leading = 9 * scale
        per_line = max(1, width_px // (6 * scale))
        for line in wrap(text, per_line):
            self.put_text(line, x, y, scale, colour)
            y += leading
        return y


# ---------------------------------------------------------------------------
# PNG: hand-rolled encoder (filter 0) and a strict reader for self-checks.
# ---------------------------------------------------------------------------
def png_chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(
        ">I", zlib.crc32(body) & 0xFFFFFFFF)


def encode_png(sheet):
    header = struct.pack(">IIBBBBB", sheet.width, sheet.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = sheet.width * 3
    for yy in range(sheet.height):
        raw.append(0)
        start = yy * stride
        raw += sheet.pixels[start:start + stride]
    out = b"\x89PNG\r\n\x1a\n"
    out += png_chunk(b"IHDR", header)
    out += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += png_chunk(b"IEND", b"")
    return out


def inspect_png(path):
    """Read a PNG back and check signature, chunk CRCs and dimensions."""
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
    pos = 8
    dims = None
    seen_iend = False
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        assert zlib.crc32(kind + body) & 0xFFFFFFFF == crc, \
            "CRC mismatch in %r chunk" % kind
        if kind == b"IHDR":
            dims = struct.unpack(">II", body[:8])
        if kind == b"IEND":
            seen_iend = True
            pos += 12 + length
            break
        pos += 12 + length
    assert dims == (W, H), "dimensions are %r, want 1024x1024" % (dims,)
    assert seen_iend, "missing IEND chunk"
    assert pos == len(data), "trailing bytes after IEND"
    return len(data)


# ---------------------------------------------------------------------------
# The front page.
# ---------------------------------------------------------------------------
LEFT = GUTTER
RIGHT = W - GUTTER


def draw_masthead(page):
    page.frame(EDGE, EDGE, W - 2 * EDGE, H - 2 * EDGE, INK, 2)
    page.frame(EDGE + 6, EDGE + 6, W - 2 * EDGE - 12, H - 2 * EDGE - 12,
               INK, 1)
    page.put_text("THE DAILY GLOBE", W // 2, 44, 7, INK, align="center")
    page.hbar(LEFT, 108, RIGHT - LEFT, INK, 2)
    page.put_text("SATURDAY, 21 NOVEMBER 2026", W // 2, 120, 2, RED,
                  align="center")
    page.put_text("THE WORLD IN ONE IMAGE", W // 2, 142, 2, SLATE,
                  align="center")
    page.hbar(LEFT, 164, RIGHT - LEFT, INK, 1)


def draw_hero_art(page):
    """Night over Kyiv: skyline, three bridges across the Dnipro, streaks."""
    x0, y0 = LEFT, 232
    x1, y1 = RIGHT, 402
    page.block(x0, y0, x1 - x0, y1 - y0, NIGHT)
    page.frame(x0, y0, x1 - x0, y1 - y0, INK, 2)
    # Stars.
    for sx, sy in ((90, 250), (210, 268), (330, 246), (470, 262), (600, 248),
                   (730, 266), (860, 252), (940, 270), (150, 292), (540, 290),
                   (800, 292), (680, 244)):
        page.dot(sx, sy, NIGHTLINE)
        page.dot(sx + 1, sy, NIGHTLINE)
    # Missile streaks falling from the top.
    for (sx, sy, ex, ey) in ((180, 236, 150, 330), (420, 234, 396, 322),
                             (700, 238, 668, 336), (880, 236, 852, 320),
                             (560, 234, 540, 300)):
        page.segment(sx, sy, ex, ey, AMBER, 3)
        page.blob(ex, ey, 4, AMBER)
    # Skyline silhouette along the river.
    skyline = [(46, 96), (96, 70), (150, 110), (206, 62), (262, 96),
               (318, 78), (372, 116), (428, 66), (484, 100), (540, 74),
               (596, 108), (652, 64), (708, 98), (764, 76), (820, 112),
               (876, 70), (930, 100)]
    for bx, bh in skyline:
        top = max(y0 + 2, y1 - 58 - bh)
        page.block(bx, top, 44, y1 - 58 - top + 58, (10, 18, 28))
    for bx, bh in skyline[::3]:
        page.block(bx + 18, max(y0 + 2, y1 - 58 - bh - 12), 8, 12,
                   (10, 18, 28))
    # The river.
    page.block(x0 + 2, y1 - 58, x1 - x0 - 4, 56, RIVER)
    page.hbar(x0 + 2, y1 - 58, x1 - x0 - 4, NIGHTLINE, 1)
    for wx in range(x0 + 30, x1 - 20, 64):
        page.hbar(wx, y1 - 34, 34, (120, 165, 195), 2)
        page.hbar(wx + 18, y1 - 18, 26, (120, 165, 195), 2)
    # Three arched bridges across the river.
    for cx in (250, 512, 774):
        page.arch(cx, y1 - 58, 92, 34, NIGHTLINE, 3)
        for px in (cx - 88, cx - 44, cx, cx + 44, cx + 88):
            page.vbar(px, y1 - 92, 34, NIGHTLINE, 2)
        page.hbar(cx - 92, y1 - 58, 184, NIGHTLINE, 3)
    # Smoke over a struck building.
    page.ring(428, 316, 10, SMOKE, 2)
    page.ring(446, 300, 14, SMOKE, 2)
    page.ring(466, 282, 18, SMOKE, 2)


def draw_hero(page):
    page.put_text("MISSILES RAIN ON KYIV", W // 2, 178, 5, INK,
                  align="center")
    draw_hero_art(page)
    page.put_text("400 DRONES, 110 MISSILES - ONE OF THE WAR'S LARGEST ATTACKS",
                  W // 2, 416, 2, RED, align="center")
    hero = ("Russia fired more than 400 drones and over 110 missiles, 27 of "
            "them ballistic, at Ukraine overnight. Three bridges over the "
            "Dnipro in Kyiv were hit, at least nine people were killed and "
            "power was cut across the country. The barrage came hours after "
            "Trump, Xi and Putin met in Shenzhen.")
    page.paragraph(hero, LEFT, 446, RIGHT - LEFT, 2, INK, leading=20)


def draw_middle(page):
    page.hbar(LEFT, 540, RIGHT - LEFT, INK, 2)
    mid = W // 2
    page.vbar(mid, 556, 196, FAINT, 1)
    col_w = (RIGHT - LEFT) // 2 - 24
    # Washington.
    page.put_text("WASHINGTON", LEFT, 556, 2, RED)
    page.put_text("NO DATA CENTRES ABROAD", LEFT, 578, 3, INK)
    wash = ("President Trump said US firms that build data centres overseas "
            "will face a 'tremendous tax' - or a ban. 'China will take all "
            "of them,' he said, a day after the first Trump-Xi-Putin "
            "trilateral in Shenzhen.")
    page.paragraph(wash, LEFT, 612, col_w, 2, INK, leading=19)
    # The Hague.
    rx = mid + 24
    page.put_text("THE HAGUE", rx, 556, 2, RED)
    page.put_text("MYANMAR: 'UNFAIR'", rx, 578, 3, INK)
    hague = ("Myanmar rejected the world court's ruling that it committed "
             "genocide against the Rohingya, calling it 'unfair'. Rights "
             "groups urged action, and Malaysia said it will resettle "
             "10,000 Rohingya refugees in Turkiye.")
    page.paragraph(hague, rx, 612, col_w, 2, INK, leading=19)


def draw_briefs(page):
    page.hbar(LEFT, 768, RIGHT - LEFT, INK, 2)
    boxes = [
        ("BRASILIA",
         "Bolsonaro, 71, in hospital with an intestinal obstruction. The "
         "jailed ex-president serves a 27-year coup-plot term."),
        ("ODISHA",
         "Cyclone Akvan weakens after landfall near Gopalpur. More than "
         "105,000 people were moved to shelters."),
        ("MARKETS",
         "Nvidia sinks to a 52-week low as the SEC is said to probe its "
         "accounting. S&P 500 -2.3%, Nasdaq 100 -4.0%."),
    ]
    box_w = (RIGHT - LEFT) // 3
    for i, (kicker, body) in enumerate(boxes):
        bx = LEFT + i * box_w
        if i:
            page.vbar(bx - 8, 784, 132, FAINT, 1)
        page.put_text(kicker, bx, 784, 2, RED)
        page.paragraph(body, bx, 808, box_w - 24, 2, INK, leading=19)


def draw_footer(page):
    page.hbar(LEFT, 934, RIGHT - LEFT, INK, 2)
    page.put_text("COP31 TALKS ENTER FINAL STAGE IN TURKIYE - PAKISTAN "
                  "BOMBING KILLS 5", W // 2, 948, 2, SLATE, align="center")
    page.put_text("INDIA 159/1 V NEW ZEALAND IN WELLINGTON - FIROUZJA WINS "
                  "CHESS TOUR PILOT", W // 2, 972, 2, SLATE, align="center")


def draw_front_page():
    page = Sheet(W, H, PAPER)
    draw_masthead(page)
    draw_hero(page)
    draw_middle(page)
    draw_briefs(page)
    draw_footer(page)
    return page


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------
def output_path(argv):
    """Where the PNG goes: $MAKEFUN_OUTPUT_DIR, /output, or beside us."""
    if len(argv) > 1:
        return argv[1]
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        return os.path.join(outdir, "entry.png")
    if os.path.isdir("/output"):
        return "/output/entry.png"
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def main(argv):
    path = output_path(argv)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    page = draw_front_page()
    data = encode_png(page)
    with open(path, "wb") as fh:
        fh.write(data)
    size = inspect_png(path)
    assert size <= 1048576, "entry.png is %d bytes, over the 1 MiB cap" % size
    print("wrote %s (%d bytes, 1024x1024, sha256 %s)"
          % (path, size, hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
