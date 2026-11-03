#!/usr/bin/env python3
"""wallet/pass/ の画像を生成する（要: pip install "qrcode[pil]"）。

- icon / logo: assets/card/avatar.jpg を円形に切り抜いたもの
- strip: 名刺ページと X の QR コードを並べた画像
"""
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pass"
AVATAR = ROOT.parent / "assets/card/avatar.jpg"

STRIP_SIZE = (375, 123)
BACKGROUND = (46, 66, 214)
INK = (27, 29, 34)
MUTED = (107, 111, 119)
QR_CODES = [
    ("Card", "eycjur.github.io", "https://eycjur.github.io/resume/ja/card/"),
    ("X", "@eycjur", "https://x.com/eycjur"),
]


def scaled_name(name, scale):
    return f"{name}.png" if scale == 1 else f"{name}@{scale}x.png"


def circle_avatar(size):
    big = size * 4
    image = Image.open(AVATAR).convert("RGBA").resize((big, big), Image.LANCZOS)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)
    image.putalpha(mask)
    return image.resize((size, size), Image.LANCZOS)


def draw_qr(draw, data, x, y, size):
    qr = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    matrix = qr.get_matrix()
    box = size // len(matrix)
    offset = (size - box * len(matrix)) // 2
    for row, cells in enumerate(matrix):
        for col, dark in enumerate(cells):
            if dark:
                left, top = x + offset + col * box, y + offset + row * box
                draw.rectangle((left, top, left + box - 1, top + box - 1), fill=INK)


def strip(scale):
    width, height = STRIP_SIZE[0] * scale, STRIP_SIZE[1] * scale
    margin = 6 * scale
    tile_w = (width - margin * 3) // 2
    tile_h = height - margin * 2
    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default(size=20 * scale)
    sub_font = ImageFont.load_default(size=9 * scale)
    for i, (title, sub, url) in enumerate(QR_CODES):
        left = margin + i * (tile_w + margin)
        draw.rounded_rectangle(
            (left, margin, left + tile_w, margin + tile_h), radius=10 * scale, fill="white"
        )
        draw_qr(draw, url, left, margin, tile_h)
        center = (left + tile_h + left + tile_w - 4 * scale) // 2
        draw.text((center, height // 2), title, font=title_font, fill=INK, anchor="md")
        draw.text((center, height // 2 + 6 * scale), sub, font=sub_font, fill=MUTED, anchor="mt")
    return image


def main():
    OUT.mkdir(exist_ok=True)
    for scale in (1, 2, 3):
        circle_avatar(29 * scale).save(OUT / scaled_name("icon", scale), optimize=True)
        circle_avatar(50 * scale).save(OUT / scaled_name("logo", scale), optimize=True)
        strip(scale).save(OUT / scaled_name("strip", scale), optimize=True)
    print(f"生成しました: {OUT}")


if __name__ == "__main__":
    main()
