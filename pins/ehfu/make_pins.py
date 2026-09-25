"""EHFU Pinterest pin builder — 1000x1500 typographic pins, one unique design per pin."""
import json
from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 1500
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
LORA_I = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
POP_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
POP_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
POP_R = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"

GOLD = (201, 162, 74)
PALETTES = [  # (background, headline, body)
    ((17, 34, 64), (246, 241, 230), (205, 214, 228)),   # deep navy
    ((246, 241, 230), (17, 34, 64), (70, 82, 104)),     # cream
    ((28, 52, 48), (246, 241, 230), (200, 216, 208)),   # forest
    ((44, 30, 56), (246, 241, 230), (214, 204, 224)),   # plum
    ((236, 230, 220), (48, 36, 28), (96, 84, 72)),      # sand
]


def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght is not None:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def tracked(draw, xy, text, f, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing
    return x


def tracked_width(draw, text, f, spacing):
    return sum(draw.textlength(c, font=f) + spacing for c in text) - spacing


def build(pin, idx, out):
    bg, head, body = PALETTES[idx % len(PALETTES)]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    M = 90

    # frame hairline
    d.rectangle([40, 40, W - 40, H - 40], outline=GOLD, width=3)

    # eyebrow
    ef = font(POP_M, 30)
    eb = pin["eyebrow"].upper()
    tracked(d, ((W - tracked_width(d, eb, ef, 6)) / 2, 150), eb, ef, GOLD, 6)

    # big number / mark
    nf = font(LORA_I, 120, 500)
    mark = pin.get("mark", "")
    if mark:
        d.text((W / 2, 290), mark, font=nf, fill=GOLD, anchor="mm")

    # headline
    size = 104
    while True:
        hf = font(LORA, size, 700)
        lines = wrap(d, pin["headline"], hf, W - 2 * M)
        lh = int(size * 1.18)
        if len(lines) * lh <= 620 or size <= 60:
            break
        size -= 4
    y = 400 + (620 - len(lines) * lh) / 2
    for ln in lines:
        d.text((W / 2, y + lh / 2), ln, font=hf, fill=head, anchor="mm")
        y += lh

    # rule
    d.line([(W / 2 - 70, 1070), (W / 2 + 70, 1070)], fill=GOLD, width=4)

    # subline
    sf = font(POP_R, 38)
    sl = wrap(d, pin["sub"], sf, W - 2 * M - 40)
    y = 1110
    for ln in sl[:3]:
        d.text((W / 2, y + 26), ln, font=sf, fill=body, anchor="mm")
        y += 56

    # footer
    ff = font(POP_B, 30)
    ft = "EVERYTHINGHAPPENSFORUS.COM"
    tracked(d, ((W - tracked_width(d, ft, ff, 4)) / 2, H - 150), ft, ff, GOLD, 4)
    rf = font(POP_R, 28)
    d.text((W / 2, H - 90), "Read the full guide", font=rf, fill=body, anchor="mm")

    im.save(out, "JPEG", quality=92)


if __name__ == "__main__":
    pins = json.load(open("pins.json"))
    for i, p in enumerate(pins):
        build(p, i, f"{i + 1:02d}.jpg")
        print("built", f"{i + 1:02d}.jpg", p["slug"])
