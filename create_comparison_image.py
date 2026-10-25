"""
Create a side-by-side comparison image:
Reference Photo vs AI-Generated 3D Model in Blender
"""
import os
from PIL import Image, ImageDraw, ImageFont

REF_PATH = "D:/code/3d/img/27ac37d8a9d38a54726d8342f3362aab.jpg"
RENDER_PATH = "D:/code/3d/screenshots/01_web_takeoff_showcase.png"
OUT_PATH = "D:/code/3d/screenshots/03_reference_vs_render.png"

ref_img = Image.open(REF_PATH).convert("RGBA")
render_img = Image.open(RENDER_PATH).convert("RGBA")

# Target image size for both panels: 1000 x 750
PANEL_W, PANEL_H = 1000, 750

# Resize & crop to cover PANEL_W x PANEL_H
def fit_panel(img, target_w, target_h):
    w, h = img.size
    scale = max(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))

panel_ref = fit_panel(ref_img, PANEL_W, PANEL_H)
panel_render = fit_panel(render_img, PANEL_W, PANEL_H)

# Final Canvas: 2040 x 860 (includes top banner & padding)
CANVAS_W = 2040
CANVAS_H = 870
HEADER_H = 90
canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (6, 19, 43, 255))
draw = ImageDraw.Draw(canvas)

# Paste panels
canvas.paste(panel_ref, (15, HEADER_H))
canvas.paste(panel_render, (CANVAS_W - PANEL_W - 15, HEADER_H))

# Border & divider
draw.rectangle([15, HEADER_H, 15 + PANEL_W, HEADER_H + PANEL_H], outline=(31, 161, 201, 180), width=2)
draw.rectangle([CANVAS_W - PANEL_W - 15, HEADER_H, CANVAS_W - 15, HEADER_H + PANEL_H], outline=(31, 161, 201, 180), width=2)

# Load font
try:
    font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
    font_label = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
except:
    font_title = font_label = font_sub = ImageFont.load_default()

# Header text
draw.text((30, 26), "BLENDER MCP  •  AUTONOMOUS IMAGE-TO-3D PIPELINE", font=font_title, fill=(255, 255, 255, 255))
draw.text((CANVAS_W - 540, 34), "Airbus A320neo • Procedural Modeling • WebGL", font=font_sub, fill=(156, 181, 217, 255))

# Panel Badges
def draw_badge(x, y, text, bg_col, text_col):
    pad_x, pad_y = 16, 8
    bbox = draw.textbbox((0, 0), text, font=font_label)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle([x, y, x + bw + pad_x*2, y + bh + pad_y*2], radius=8, fill=bg_col)
    draw.text((x + pad_x, y + pad_y - 2), text, font=font_label, fill=text_col)

draw_badge(35, HEADER_H + 20, "INPUT: Reference Photograph", (5, 14, 82, 220), (255, 255, 255, 255))
draw_badge(CANVAS_W - PANEL_W + 5, HEADER_H + 20, "OUTPUT: Autonomous 3D Model in Blender", (31, 161, 201, 230), (5, 14, 82, 255))

canvas.save(OUT_PATH, "PNG")
print(f"Comparison image saved to: {OUT_PATH}")
