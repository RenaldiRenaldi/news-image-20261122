"""Draw the Sunday Wire image. Requires Pillow; the entry runner does not."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1024, 1024
PAPER = "#F3F0E8"
INK = "#14232C"
MUTED = "#5A6A70"
RED = "#D53D32"
GOLD = "#E5B457"
LAND = "#B8C7C5"
SEA = "#E2E8E4"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
MAP_SOURCE = Path("/tmp/news-wire-ne-land.geojson")
MAP_ASSET = ROOT / "assets" / "world-outline.png"

# Coordinates are lon, lat from the pre-research ledger. NYC's four distinct
# threads intentionally share one map marker. Other near points remain true.
STORIES = [
    ("SUN22", "BTC slides to $55.1K, rebounds near $60K", -74.0, 40.7),
    ("SUN22", "COP31 tables new package; deal still pending", 30.7, 36.9),
    ("SUN22", "India–NZ Test day 4 opens; India led by 118", 174.8, -41.3),
    ("FRI20", "Mexico captures FBI fugitive El Chapo Isidro", -108.5, 25.6),
    ("FRI20", "Russia's 400-drone barrage hits Kyiv bridges; 8 killed, 28 injured", 30.5, 50.4),
    ("FRI20", "Kryvyi Rih strike kills 2; 58 injured", 33.4, 47.9),
    ("FRI20", "Russian weapons cross into Poland", 22.7, 50.0),
    ("FRI20", "GTA VI: 32.5m sold; $3.79bn day one", -74.0, 40.7),
    ("FRI20", "Daraxonrasib trial: tumours shrank/disappeared in 60.7%", 2.2, 41.4),
    ("FRI20", "Youth strikes span 25 countries", 13.4, 52.5),
    ("FRI20", "FBI probes apparent NCIC data breach", -77.0, 38.9),
    ("FRI20", "US sanctions 4 Iran oil trustees", 51.4, 35.7),
    ("THU19", "NASA pauses Perseverance science after radio loss", -118.2, 34.2),
    ("THU19", "Moyale conflict displaces nearly 700,000", 39.1, 3.5),
    ("TUE17", "DR Congo Ebola toll passes 11,000 cases", 30.2, 1.6),
    ("SAT21", "Basra power-station fire kills at least 4", 47.8, 30.5),
    ("SAT21", "Iran strikes US bases in Bahrain; plant fire, no injuries reported", 50.55, 26.07),
    ("FRI20", "EU–UK plan outlines 100,000 youth visas each way", -0.1, 51.5),
    ("THU19", "ICJ: Myanmar responsible for Rohingya genocide", 4.3, 52.1),
    ("THU19", "Spain election polls disagree on leader", -3.7, 40.4),
    ("FRI20", "Estonia to close 5 road crossings with Russia", 28.2, 59.4),
    ("FRI20", "3 Salvadoran soldiers killed in Haiti", -72.3, 18.5),
    ("THU19", "Denmark backs Greenland defence pact 109–0", 12.6, 55.7),
    ("WED18", "IAEA flags Yongbyon enrichment-site expansion", 125.3, 39.8),
    ("WED–FRI", "Bangladesh unrest: 3 killed in two days", 90.4, 23.8),
    ("WED18", "US and Venezuela sign military-cooperation deal", -66.9, 10.5),
    ("FRI20", "Nikhil Gupta gets 235 months in Pannun plot", -74.0, 40.7),
    ("THU19", "14 charged in $22.5m California train heist", -118.2, 34.1),
    ("FRI20", "Palisades Fire arsonist convicted at retrial", -118.5, 34.0),
    ("FRI20", "Peru hit by M6.7 quake; 1 dead, 16 injured", -76.0, -11.2),
    ("THU19", "South Africa holds repo rate at 7.25%", 28.2, -25.7),
    ("SAT21", "U17 World Cup: Mali win 3–0; Belgium 3–2", 51.5, 25.3),
    ("FRI20", "West Bank Shira plan proposes 60,000 homes", 35.0, 32.1),
    ("FRI20", "Japan inflation eases to 2.3% in October", 139.7, 35.7),
    ("THU19", "n0n vendor breach reaches 3 payment firms", -74.0, 40.7),
]

def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)

F_SANS = "DejaVuSans.ttf"
F_BOLD = "DejaVuSans-Bold.ttf"
F_MONO = "DejaVuSansMono.ttf"

def centered(draw, xy, value, face, fill):
    draw.text(xy, value, font=face, fill=fill, anchor="mm")

def fit(draw, value, face, max_width):
    text = value
    while text and draw.textbbox((0, 0), text, font=face)[2] > max_width:
        text = text[:-2].rstrip() + "…"
    return text

def project(lon, lat, box):
    x, y, w, h = box
    lat = max(-60, min(84, lat))
    return (x + (lon + 180) / 360 * w, y + (84 - lat) / 144 * h)

def outline_from_geojson():
    data = json.loads(MAP_SOURCE.read_text(encoding="utf-8"))
    iw, ih = 968, 88
    base = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    for feature in data["features"]:
        geom = feature.get("geometry") or {}
        kind, coords = geom.get("type"), geom.get("coordinates", [])
        polygons = [coords] if kind == "Polygon" else coords if kind == "MultiPolygon" else []
        for polygon in polygons:
            if not polygon:
                continue
            ring = [project(lon, lat, (0, 0, iw - 1, ih - 1)) for lon, lat in polygon[0]]
            if len(ring) > 2:
                d.polygon(ring, fill=LAND, outline="#7F9695")
    MAP_ASSET.parent.mkdir(parents=True, exist_ok=True)
    base.save(MAP_ASSET, optimize=True)
    return base

def map_base():
    if MAP_SOURCE.exists():
        return outline_from_geojson()
    return Image.open(MAP_ASSET).convert("RGBA")

def main():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # Masthead and prominent day label.
    d.rectangle((0, 0, W, 106), fill=INK)
    d.rectangle((0, 0, 15, 106), fill=RED)
    d.text((38, 18), "THE WIRE", font=font(F_BOLD, 42), fill=PAPER)
    d.text((40, 68), "WORLD DESK  /  SUNDAY EDITION  /  07:53 WIB", font=font(F_MONO, 15), fill="#AFC0C1")
    d.rounded_rectangle((740, 16, 994, 90), radius=8, fill="#203741", outline="#587077", width=1)
    centered(d, (867, 38), "SUNDAY", font(F_BOLD, 23), "#F4C86D")
    centered(d, (867, 68), "22 NOV 2026", font(F_BOLD, 25), PAPER)

    # Live market lead.
    d.rounded_rectangle((24, 120, 1000, 282), radius=10, fill="#FFFDF7", outline="#D5D2C8", width=2)
    d.rectangle((24, 120, 34, 282), fill=RED)
    d.text((55, 134), "LIVE WIRE  /  CRYPTO", font=font(F_BOLD, 15), fill=RED)
    d.text((53, 156), "BITCOIN'S $55K LOW", font=font(F_BOLD, 48), fill=INK)
    d.text((53, 207), "BOUNCES BACK ABOVE $60K", font=font(F_BOLD, 43), fill=INK)
    d.text((56, 256), "$55,100 24h low  →  $60,066 spot at 00:53 UTC  ·  Kraken XBT/USD", font=font(F_SANS, 17), fill=MUTED)
    d.text((809, 143), "TROUGH −56%", font=font(F_BOLD, 22), fill=RED)
    d.text((839, 176), "vs Oct ’25 peak", font=font(F_SANS, 12), fill=MUTED)

    # Three flash dispatches; each is a separate verified thread.
    flash = [
        ("ANTALYA · SUN 22", "New package tabled; final deal", "still not adopted."),
        ("WELLINGTON · SUN 22", "India–NZ Test day 4 opens;", "India held a 118-run lead."),
        ("GUASAVE · FRI 20", "FBI fugitive El Chapo Isidro", "captured; US reward $5m."),
    ]
    card_w = 316
    for i, (tag, line1, line2) in enumerate(flash):
        x = 24 + i * 326
        d.rounded_rectangle((x, 298, x + card_w, 396), radius=7, fill="#E7ECE8", outline="#C7D2CD", width=1)
        d.rectangle((x, 298, x + 5, 396), fill=RED if i == 0 else GOLD)
        d.text((x + 16, 308), tag, font=font(F_BOLD, 13), fill=RED if i == 0 else MUTED)
        d.text((x + 16, 331), fit(d, line1, font(F_BOLD, 16), card_w - 28), font=font(F_BOLD, 16), fill=INK)
        d.text((x + 16, 354), fit(d, line2, font(F_SANS, 15), card_w - 28), font=font(F_SANS, 15), fill=INK)
        d.text((x + 16, 377), "VERIFIED DISPATCH", font=font(F_MONO, 10), fill=MUTED)

    # Continuous red spine with alternating dated bulletins (31 other threads).
    d.text((28, 410), "THE TAPE", font=font(F_BOLD, 20), fill=INK)
    d.text((145, 415), "31 MORE VERIFIED THREADS  ·  EVENT / REPORT DATE SHOWN", font=font(F_MONO, 12), fill=MUTED)
    spine_x = 512
    d.line((spine_x, 440, spine_x, 696), fill=RED, width=4)
    timeline = STORIES[4:]
    step = 8.0
    start_y = 445
    date_face = font(F_BOLD, 11)
    body_face = font(F_SANS, 13)
    for idx, (stamp, title, lon, lat) in enumerate(timeline):
        y = start_y + idx * step
        left = idx % 2 == 0
        line_face = font(F_SANS, 11) if title.startswith(("Russia's 400-drone barrage", "Iran strikes US bases")) else body_face
        dot_y = int(y + 7)
        d.ellipse((spine_x - 4, dot_y - 4, spine_x + 4, dot_y + 4), fill=RED, outline=PAPER, width=1)
        if left:
            d.text((26, y), stamp, font=date_face, fill=RED)
            body = fit(d, title, line_face, 390)
            d.text((105, y - 1), body, font=line_face, fill=INK)
            d.line((491, dot_y, spine_x - 6, dot_y), fill="#C5C8C1", width=1)
        else:
            d.line((spine_x + 6, dot_y, 530, dot_y), fill="#C5C8C1", width=1)
            d.text((541, y), stamp, font=date_face, fill=RED)
            body = fit(d, title, line_face, 395)
            d.text((624, y - 1), body, font=line_face, fill=INK)

    # Accurate equirectangular map strip: Natural Earth coastlines + ledger dots.
    d.line((25, 700, 999, 700), fill="#C4CBC6", width=1)
    d.text((27, 704), "DISPATCH MAP", font=font(F_BOLD, 14), fill=INK)
    d.text((166, 706), "35 threads · NYC cluster ×4 (BTC / GTA / Pannun / n0n)", font=font(F_SANS, 12), fill=MUTED)
    map_box = (28, 731, 968, 88)
    d.rectangle((map_box[0], map_box[1], map_box[0] + map_box[2], map_box[1] + map_box[3]), fill=SEA)
    coast = map_base()
    im.paste(coast, (map_box[0], map_box[1]), coast)
    d = ImageDraw.Draw(im)
    for lat in (-30, 0, 30, 60):
        x1, y1 = project(-180, lat, map_box)
        x2, y2 = project(180, lat, map_box)
        d.line((x1, y1, x2, y2), fill="#C5D1CE", width=1)
    for lon in (-120, -60, 0, 60, 120):
        x1, y1 = project(lon, 84, map_box)
        x2, y2 = project(lon, -60, map_box)
        d.line((x1, y1, x2, y2), fill="#C5D1CE", width=1)
    # Merge only the required four-story New York cluster; other dots remain true.
    seen_nyc = False
    points = []
    for stamp, title, lon, lat in STORIES:
        if lon == -74.0 and lat == 40.7:
            if seen_nyc:
                continue
            seen_nyc = True
            points.append((lon, lat, "NYC ×4"))
        else:
            points.append((lon, lat, None))
    for lon, lat, label in points:
        x, y = project(lon, lat, map_box)
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=RED, outline="#FFFDF7", width=1)
        if label:
            d.rounded_rectangle((x + 5, y - 15, x + 56, y - 2), radius=3, fill=INK)
            d.text((x + 8, y - 14), label, font=font(F_BOLD, 10), fill=PAPER)
    # A few anchors make the map readable without turning it into a label cloud.
    for label, lon, lat, dx, dy in [
        ("ANTALYA", 30.7, 36.9, -54, 4), ("KYIV", 30.5, 50.4, 7, -16),
        ("MOYALE", 39.1, 3.5, 7, 5), ("DOHA - BAHRAIN", 51.5, 25.3, 7, -15),
        ("WELLINGTON", 174.8, -41.3, -72, -16), ("LA", -118.2, 34.1, -21, -16),
    ]:
        x, y = project(lon, lat, map_box)
        d.text((x + dx, y + dy), label, font=font(F_BOLD, 10), fill=INK, stroke_width=1, stroke_fill=SEA)

    # Footer owns the Sunday date; the full required date check stays verbatim.
    d.rectangle((0, 825, W, H), fill=INK)
    d.rectangle((0, 825, 12, H), fill=RED)
    d.text((28, 829), "DATE CHECK  ·  SUN 22 NOVEMBER 2026", font=font(F_BOLD, 22), fill="#F4C86D")
    date_face = font(F_SANS, 37)
    d.text((28, 858), "This edition was published on", font=date_face, fill=PAPER)
    d.text((28, 904), "Sunday 22 November 2026. Event and", font=date_face, fill=PAPER)
    d.text((28, 950), "report dates are shown in the text.", font=date_face, fill=PAPER)
    d.text((28, 1003), "THE WIRE  ·  SOURCES: REUTERS / AP / OFFICIALS / PRIMARY REPORTS  ·  SOURCES.MD", font=font(F_MONO, 9), fill="#9AAEAE")

    im.save(ROOT / "entry.png", format="PNG", optimize=True)

if __name__ == "__main__":
    main()
