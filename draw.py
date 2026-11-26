"""Render the 26 November 2026 world-news image. Pure Python standard
library only: no network, no fonts, no third-party packages.

The poster is drawn on a 1024x1024 canvas with a small embedded 5x7
bitmap font, then written out as a PNG.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (180, 35, 24)
BLUE = (29, 78, 216)
GREEN = (22, 101, 52)
GRAY = (107, 114, 128)
TAN = (226, 214, 186)
LINE = (201, 194, 180)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters, '#' on, '.' off.
# All poster text is upper-case; only the characters used are defined.
FONT = {
    'A': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".####", ".....", ".####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '<': ("...##", "..#..", ".#...", "#....", ".#...", "..#..", "...##"),
    '>': ("##...", "..#..", "...#.", "....#", "...#.", "..#..", "##..."),
    '\u00b7': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '\u2022': (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}


def _norm(text):
    """Upper-case the poster text and fold lookalike punctuation."""
    out = []
    for ch in text.upper():
        if ch in ("\u2019", "\u2018"):
            ch = "'"
        elif ch in ("\u2013",):
            ch = "\u2014"
        out.append(ch)
    return "".join(out)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.px(cx + dx, cy + dy, color)

    def fill_poly(self, points, color):
        """Even-odd scanline fill for a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                x0 = max(0, int(xs[j]))
                x1 = min(self.w, int(xs[j + 1]) + 1)
                row = bytes(color) * (x1 - x0)
                i = (y * self.w + x0) * 3
                self.buf[i:i + len(row)] = row

    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "#":
                    self.fill_rect(x + c * scale, y + r * scale,
                                   scale, scale, color)

    def text(self, x, y, s, scale, color):
        s = _norm(s)
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(_norm(s)) * 6 * scale - scale

    def text_right(self, x, y, s, scale, color):
        return self.text(x - self.text_w(s, scale), y, s, scale, color)

    def text_center(self, x, y, s, scale, color):
        return self.text(x - self.text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = _norm(s).split(" ")
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = b"".join(
        b"\x00" + bytes(canvas.buf[y * w * 3:(y + 1) * w * 3])
        for y in range(h)
    )
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- content: 26 November 2026, as reported that morning ----

LEADS = [
    ("TARIFFS RETURN",
     "US TARIFFS HIT 14 ECONOMIES",
     "INDIA UP TO 25%, CHINA 20%, EU 15% — AFTER THE SUPREME COURT "
     "STRUCK DOWN THE OLD LEVIES. USTR · SECTION 301"),
    ("CHIPS AND SPY ROW",
     "HOW CHINA GOT NVIDIA'S CHIPS",
     "US INTEL SAYS BEIJING MAY HAVE WATCHED THE NVIDIA CHIEF'S "
     "PARTNER. FIRMS TIED TO HER LISTED $270M OF SERVERS IN CHINA. CBS"),
    ("UKRAINE STRIKES BACK",
     "KYIV HITS RUSSIAN AIR BASE",
     "THREE MIG-31S AND TWO SU-34S KNOCKED OUT AT SAVASLEYKA; US "
     "CLEARS $622M OF F-16 KIT FOR KYIV. AL JAZEERA"),
]

# (number, one-line story of at most 35 characters, tag)
# OF = OFFICIAL, CF = CONFIRMED, RP = REPORTED
STORIES = [
    (4, "KOSPI -6.2%, TAIEX -4.8% IN ROUT", "RP"),
    (5, "EGYPT FUEL FIRE KILLS 31, HURTS 21", "CF"),
    (6, "THANKSGIVING: VANCE SERVES TROOPS", "OF"),
    (7, "SPACEX CLEARED FOR 1M SATELLITES", "CF"),
    (8, "KIM WANTS MORE TACTICAL NUKES", "RP"),
    (9, "MURMANSK GOVERNOR HELD FOR GRAFT", "CF"),
    (10, "LEBANON TO OPEN SECOND AIRPORT", "RP"),
    (11, "NATIONS URGE RUSSIA OVER GAS CLAIM", "RP"),
    (12, "BIRTHRIGHT ORDER BLOCKED BY JUDGE", "CF"),
    (13, "KENYA CULT LEADER CONVICTED AGAIN", "CF"),
    (14, "ANDY TAYLOR OF DURAN DURAN DIES, 65", "CF"),
    (15, "RAMAPHOSA REPORT RULED UNLAWFUL", "CF"),
    (16, "WHO: END US FUEL BLOCKADE ON CUBA", "RP"),
    (17, "SIX DEAD IN GULF COAST PLANE CRASH", "CF"),
    (18, "NATO BOOSTS EASTERN AIR WATCH", "CF"),
    (19, "UN: 5 WOMEN KILLED EVERY HOUR", "OF"),
    (20, "TRUMP SEEKS FASTER EXECUTIONS", "RP"),
    (21, "SEOUL WARNS AFTER RUSSIAN JETS NEAR", "RP"),
    (22, "CHINA TO HOST FOREIGN ASTRONAUT", "RP"),
    (23, "HOUTHIS HIT RIYADH; HORMUZ BLASTS", "RP"),
    (24, "US JOBLESS CLAIMS FALL TO 189,000", "OF"),
    (25, "US SHOPPERS PAUSE AFTER SPENDING", "RP"),
    (26, "GOLDMAN SEES GOLD AT $4,650 IN 2027", "RP"),
    (27, "GRAMEEN BANK: 100 ARSON ATTACKS", "RP"),
    (28, "NEPAL QUAKE 5.4; TREMORS IN INDIA", "CF"),
    (29, "BANGLADESH GARMENT PAY UP 36%", "CF"),
    (30, "ABREGO GARCIA LEAVES US FOR SPAIN", "CF"),
    (31, "IOWA AMMO PLANT BLAST ALARMS FARMS", "RP"),
    (32, "FINCEN HIT BY SUSPECTED CYBERATTACK", "RP"),
    (33, "IRAN SUSPECTED OF HACKING 50 SHIPS", "RP"),
    (34, "LIVERPOOL 3-0 BRUGGE; BARCA 4-1", "CF"),
    (35, "SOUTH AFRICA THRASH BANGLADESH", "CF"),
    (36, "INDIA THRASH JAPAN 4-0 IN HOCKEY", "CF"),
    (37, "ANTHROPIC CHIEF CLARIFIES AI STANCE", "RP"),
    (38, "GIULIANI RECEIVES MEDAL OF FREEDOM", "CF"),
    (39, "ECUADOR IN US TALKS ON OPERATIONS", "RP"),
    (40, "PAKISTANI ASTRONAUT DINES IN SPACE", "RP"),
]

# Coarse continent outlines (lon, lat), drawn as a schematic strip map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-65, 60), (-55, 47), (-60, 45), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 15), (-95, 17), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-80, -5), (-80, -15), (-70, -18), (-70, -30),
     (-65, -40), (-60, -50), (-65, -55), (-70, -50), (-72, -35), (-72, -20),
     (-77, -10), (-80, 5)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (40, 0), (35, -10), (30, -20), (25, -30),
     (20, -35), (15, -30), (12, -18), (9, -5), (9, 4), (-8, 4), (-15, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 70), (40, 68),
     (45, 65), (40, 55), (35, 50), (30, 45), (28, 40), (23, 36), (19, 40),
     (12, 44), (8, 44), (3, 43), (-1, 37), (-9, 37)],
    [(32, 70), (45, 68), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 67), (178, 65), (170, 60), (162, 55), (158, 50), (150, 45),
     (142, 42), (140, 38), (135, 35), (130, 32), (127, 35), (122, 38),
     (120, 32), (115, 25), (110, 20), (108, 12), (105, 9), (100, 7),
     (97, 15), (92, 20), (88, 22), (85, 18), (80, 13), (77, 8), (75, 12),
     (72, 20), (68, 23), (62, 25), (57, 26), (52, 27), (48, 29), (44, 29),
     (40, 31), (36, 36), (32, 40), (30, 45), (32, 55), (32, 65)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -22),
     (146, -19), (142, -15), (142, -11), (136, -12), (132, -12), (126, -14),
     (122, -17), (118, -20)],
]

# (lon, lat, pin number) for the map.
PINS = [
    (-77, 39, 1), (44, 56, 2), (31, 30, 3), (130, 35.5, 4),
    (121, 21, 5), (144, 33, 6), (116.4, 39.9, 7), (46.7, 24.6, 8),
    (-0.1, 51.5, 9), (-90, 25, 10), (77.2, 28.6, 11), (124, 42, 12),
]

MX = 24
CW = 976


def draw_line(cv, x1, y1, x2, y2, color):
    """Bresenham line on the canvas."""
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        cv.px(x1, y1, color)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy


def _proj(lon, lat):
    return (MX + (lon + 180) / 360 * CW, 396 + (85 - lat) / 145 * 134)


def render(path):
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.text(MX, 12, "THE WORLD", 6, INK)
    cv.text_right(MX + CW, 16, "THURSDAY 26 NOVEMBER 2026", 4, INK)
    cv.text(MX, 58, "THE WORLD'S NEWS, SUMMED UP · ONE DAY, ONE IMAGE", 2, INK)
    cv.text_right(MX + CW, 58, "THANKSGIVING DAY IN THE US", 2, RED)
    cv.hline(MX, 74, CW, INK, 2)

    # ---- UTC timeline bar ----
    cv.fill_rect(MX, 78, CW, 42, INK)
    x = cv.text(MX + 8, 84, "THE DAY IN UTC — ", 2, RED)
    cv.text(x, 84, "00:16 ASIA ROUT REPORTED · 01:20 US INTEL: CHINA WATCH",
            2, PAPER)
    cv.text(MX + 8, 100,
            "01:34 TARIFF DETAILS OUT · 01:39 UKRAINE HITS AIR BASE", 2, PAPER)

    # ---- day in numbers ----
    x = cv.text(MX, 126, "THE DAY IN NUMBERS · ", 2, RED)
    cv.text(x, 126, "14 ECONOMIES · INDIA UP TO 25% · CHINA 20% · VIETNAM UP TO 35%",
            2, INK)
    cv.text(MX, 142,
            "KOSPI -6.2% · 189,000 JOBLESS CLAIMS · 31 KILLED IN CAIRO · 5 PLANES HIT",
            2, INK)
    cv.hline(MX, 156, CW, LINE, 1)

    # ---- three leads ----
    col_x = [MX, 348, 672]
    for i, (kicker, headline, summary) in enumerate(LEADS):
        x0 = col_x[i]
        cv.text(x0, 166, kicker, 2, RED)
        y = 188
        for line in wrap(headline, 12):
            cv.text(x0, y, line, 4, INK)
            y += 32
        y += 6
        for line in wrap(summary, 25):
            cv.text(x0, y, line, 2, INK)
            y += 15
    cv.vline(338, 166, 196, LINE, 1)
    cv.vline(662, 166, 196, LINE, 1)
    cv.hline(MX, 370, CW, INK, 2)

    # ---- world map with numbered pins ----
    cv.text(MX, 378, "WHERE THE DAY HAPPENED", 2, INK)
    cv.text_right(MX + CW, 378, "PINS MARK THE STORIES", 2, GRAY)
    cv.rect(MX, 396, CW, 134, INK, 1)
    for poly in CONTINENTS:
        pts = [(_proj(lon, lat)[0], _proj(lon, lat)[1]) for lon, lat in poly]
        pts = [(int(px), int(py)) for px, py in pts]
        cv.fill_poly(pts, TAN)
        for j in range(len(pts)):
            x1, y1 = pts[j]
            x2, y2 = pts[(j + 1) % len(pts)]
            draw_line(cv, x1, y1, x2, y2, INK)
    for lon, lat, num in PINS:
        px, py = _proj(lon, lat)
        cv.circle(int(px), int(py), 11, RED)
        cv.text_center(int(px), int(py) - 7, str(num), 2, PAPER)
    cv.text(MX, 534,
            "MAP — 1 WASHINGTON · 2 SAVASLEYKA · 3 CAIRO · 4 SEOUL · 5 TAIPEI · 6 TOKYO",
            2, INK)
    cv.text(MX, 550,
            "7 BEIJING · 8 RIYADH · 9 LONDON · 10 GULF COAST · 11 NEW DELHI · 12 PYONGYANG",
            2, INK)

    # ---- numbered stories ----
    cv.text(MX, 570, "THE REST OF THE DAY — 37 MORE STORIES", 2, INK)
    cv.text_right(MX + CW, 570, "OF OFFICIAL · CF CONFIRMED · RP REPORTED", 2, GRAY)
    cv.hline(MX, 588, CW, INK, 1)
    half = (len(STORIES) + 1) // 2
    for col, chunk in enumerate((STORIES[:half], STORIES[half:])):
        x0 = MX + col * 496
        for row, (num, text, tag) in enumerate(chunk):
            y = 592 + row * 19
            cv.text(x0, y, "%02d" % num, 2, RED)
            cv.text(x0 + 30, y, text, 2, INK)
            cv.text_right(x0 + 480, y, tag, 2, GRAY)

    # ---- bottom band ----
    cv.hline(MX, 956, CW, INK, 2)
    cv.text(MX, 962,
            "ALSO ON: INDIA-CHINA TALKS RESUME · SAUDI DEFICIT 190BN RIYALS",
            2, INK)
    cv.text(MX, 978,
            "ESTONIA SHUTS RUSSIA BORDER 1 DEC · MI5 WARNS UK DEFENCE FIRMS",
            2, INK)
    x = cv.text(MX, 994, "DATE CHECK — LEFT OUT: ", 2, RED)
    cv.text(x, 994, "COP31 NO PACT · HUANG REINSTATEMENT · PERU QUAKE", 2, INK)
    cv.text(MX, 1010,
            "SOURCES: REUTERS · AL JAZEERA · WSJ · ET · BUSINESS RECORDER · NEWSBYTES",
            2, GRAY)

    return write_png(path, cv)


if __name__ == "__main__":
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "entry.png"))
