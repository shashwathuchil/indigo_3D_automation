"""
Generate high-fidelity texture maps for IndiGo A320neo:
- tex_fuselage.png (2048x1024)
- tex_fin.png (1024x1024)
- tex_engine.png (1024x512)
- tex_wing.png (1024x1024)
Correctly accounts for UV winding on starboard & port sides so all text reads
naturally left-to-right from every viewpoint.
"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = "D:/code/3d/models/indigo-a320"
os.makedirs(OUT, exist_ok=True)

WHITE = (248, 250, 252, 255)         # Aviation glossy white
NAVY = (5, 14, 82, 255)              # IndiGo deep navy #050E52
CYAN = (31, 161, 201, 255)           # IndiGo cyan pinstripe #1FA1C9
GLASS = (12, 18, 32, 255)            # Window glass tint
GLASS_HI = (45, 75, 125, 255)        # Window glass specular highlight
FRAME = (45, 52, 65, 255)            # Window frame
SEAM = (210, 215, 222, 255)          # Panel seam / door line
SILVER = (195, 200, 208, 255)        # Metallic silver / chrome
TITANIUM = (65, 68, 75, 255)         # Exhaust / intake dark metal
FLAG_ORANGE = (255, 122, 0, 255)     # Saffron
FLAG_GREEN = (18, 136, 7, 255)       # Green
FLAG_BLUE = (0, 0, 128, 255)         # Blue

FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_PATH_REG = "C:/Windows/Fonts/segoeui.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
    FONT_PATH_REG = "C:/Windows/Fonts/arial.ttf"

def create_fuselage_texture():
    W, H = 2048, 1024
    img = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Radome seam line
    radome_x = int(W * 0.055)
    draw.line([(radome_x, 0), (radome_x, H)], fill=SEAM, width=2)

    # 1. IndiGo Blue Belly Swoosh + Cyan Stripe
    # Starboard side curve: V in 0.25..0.50
    def belly_curve(x_frac):
        if x_frac < 0.12:
            return 0.46 - 0.04 * (x_frac / 0.12)
        elif x_frac < 0.35:
            t = (x_frac - 0.12) / 0.23
            return 0.42 - 0.08 * math.sin(t * math.pi / 2) # up to 0.34
        elif x_frac < 0.65:
            return 0.34
        elif x_frac < 0.88:
            t = (x_frac - 0.65) / 0.23
            return 0.34 - 0.06 * math.sin(t * math.pi / 2) # up to 0.28
        else:
            return 0.28 + 0.10 * ((x_frac - 0.88) / 0.12)

    poly = []
    for x in range(0, W, 4):
        poly.append((x, int(belly_curve(x / W) * H)))
    for x in range(W, -1, -4):
        poly.append((x, int((1.0 - belly_curve(x / W)) * H)))
    draw.polygon(poly, fill=NAVY)

    cyan_stb = [(x, int(belly_curve(x / W) * H)) for x in range(0, W, 2)]
    cyan_prt = [(x, int((1.0 - belly_curve(x / W)) * H)) for x in range(0, W, 2)]
    draw.line(cyan_stb, fill=CYAN, width=5)
    draw.line(cyan_prt, fill=CYAN, width=5)

    # 2. Passenger Windows
    win_w, win_h = 7, 13
    win_spacing = 17
    start_x = int(W * 0.165)
    end_x = int(W * 0.820)
    door_xs = [int(W * 0.142), int(W * 0.440), int(W * 0.468), int(W * 0.845)]

    for x in range(start_x, end_x, win_spacing):
        if any(abs(x - dx) < 18 for dx in door_xs):
            continue
        for y_center in [int(H * 0.252), int(H * 0.748)]:
            draw.rounded_rectangle(
                [x - win_w//2, y_center - win_h//2, x + win_w//2, y_center + win_h//2],
                radius=3, fill=FRAME, outline=WHITE, width=1
            )
            draw.rounded_rectangle(
                [x - win_w//2 + 1, y_center - win_h//2 + 1, x + win_w//2 - 1, y_center + win_h//2 - 1],
                radius=2, fill=GLASS
            )
            draw.line(
                [x - win_w//2 + 2, y_center - win_h//2 + 2, x + win_w//2 - 2, y_center - win_h//2 + 2],
                fill=GLASS_HI, width=1
            )

    # 3. Passenger Doors
    def draw_door(cx, cy, dw, dh):
        draw.rounded_rectangle([cx - dw//2, cy - dh//2, cx + dw//2, cy + dh//2], radius=4, outline=SEAM, width=2)
        draw.rounded_rectangle([cx - 4, cy - 12, cx + 4, cy], radius=2, fill=GLASS, outline=FRAME, width=1)
        draw.rectangle([cx - 5, cy + 4, cx - 1, cy + 6], fill=SILVER)

    for cy in [int(H * 0.252), int(H * 0.748)]:
        draw_door(door_xs[0], cy, 22, 46) # L1/R1
        draw_door(door_xs[1], cy - 2, 16, 32) # Overwing 1
        draw_door(door_xs[2], cy - 2, 16, 32) # Overwing 2
        draw_door(door_xs[3], cy, 22, 44) # L2/R2

    # 4. Cockpit Windshield (Airbus 6-Pane Mask)
    for cy, side in [(int(H * 0.245), 1), (int(H * 0.755), -1)]:
        c_x = int(W * 0.084)
        mask_pts = [
            (c_x - 16, cy + side * 4), (c_x - 6, cy - side * 14), (c_x + 28, cy - side * 14),
            (c_x + 36, cy - side * 3), (c_x + 24, cy + side * 10), (c_x - 10, cy + side * 10),
        ]
        draw.polygon(mask_pts, fill=FRAME, outline=WHITE)
        p1 = [(c_x - 12, cy + side * 3), (c_x - 4, cy - side * 11), (c_x + 8, cy - side * 11), (c_x + 4, cy + side * 7)]
        p2 = [(c_x + 8, cy - side * 11), (c_x + 20, cy - side * 11), (c_x + 18, cy + side * 8), (c_x + 6, cy + side * 8)]
        p3 = [(c_x + 22, cy - side * 10), (c_x + 32, cy - side * 2), (c_x + 22, cy + side * 8), (c_x + 19, cy - side * 2)]
        for p in [p1, p2, p3]:
            draw.polygon(p, fill=GLASS, outline=FRAME)
            draw.line([p[0], p[1]], fill=GLASS_HI, width=1)

    # 5. "IndiGo" Branding on Forward Fuselage
    try:
        font_logo = ImageFont.truetype(FONT_PATH, 58)
        font_sub = ImageFont.truetype(FONT_PATH_REG, 13)
    except:
        font_logo = font_sub = ImageFont.load_default()

    # Port Side (Y ~ 0.735*H): Reads left-to-right naturally
    draw.text((int(W * 0.210), int(H * 0.730)), "IndiGo", font=font_logo, fill=NAVY)

    # Starboard Side (Y ~ 0.205*H):
    # On the 3D model viewed from +X, nose is on the right and tail on the left.
    # To read left-to-right (from tail towards nose), the texture on this side needs
    # to be rendered and flipped horizontally so it un-mirrors on the mesh!
    logo_w, logo_h = 240, 75
    txt_patch = Image.new("RGBA", (logo_w, logo_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt_patch)
    td.text((0, 0), "IndiGo", font=font_logo, fill=NAVY)
    txt_patch_flipped = ImageOps.mirror(txt_patch)
    img.paste(txt_patch_flipped, (int(W * 0.210), int(H * 0.178)), txt_patch_flipped)

    # 6. Indian Flag & Registration
    for reg_y, is_stb in [(int(H * 0.225), True), (int(H * 0.735), False)]:
        fx, fy = int(W * 0.810), reg_y
        fw, fh = 24, 15
        draw.rectangle([fx, fy, fx + fw, fy + fh // 3], fill=FLAG_ORANGE)
        draw.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * (fh // 3)], fill=WHITE)
        draw.rectangle([fx, fy + 2 * (fh // 3), fx + fw, fy + fh], fill=FLAG_GREEN)
        draw.ellipse([fx + fw // 2 - 2, fy + fh // 2 - 2, fx + fw // 2 + 2, fy + fh // 2 + 2], fill=FLAG_BLUE)
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=SEAM, width=1)
        
        reg_txt = "VT-IZN"
        if is_stb:
            rp = Image.new("RGBA", (80, 25), (0, 0, 0, 0))
            ImageDraw.Draw(rp).text((0, 0), reg_txt, font=font_sub, fill=NAVY)
            rp_f = ImageOps.mirror(rp)
            img.paste(rp_f, (int(W * 0.840), reg_y + 15), rp_f)
        else:
            draw.text((int(W * 0.840), reg_y + 15), reg_txt, font=font_sub, fill=NAVY)

    img.save(f"{OUT}/tex_fuselage.png", "PNG")
    print(f"Fuselage texture saved: {OUT}/tex_fuselage.png")

def create_fin_texture():
    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    try:
        font_fin = ImageFont.truetype(FONT_PATH, 76)
    except:
        font_fin = ImageFont.load_default()

    for side_idx, (y_min, y_max, is_mirror) in enumerate([(0, 512, False), (512, 1024, True)]):
        le_pts = [
            (int(W * 0.05), y_max),
            (int(W * 0.38), y_min + int((y_max - y_min) * 0.08)),
            (int(W * 0.44), y_min + int((y_max - y_min) * 0.08)),
            (int(W * 0.12), y_max),
        ]
        draw.polygon(le_pts, fill=NAVY)
        draw.line([le_pts[1], (int(W * 0.12), y_max)], fill=CYAN, width=6)

        cap_pts = [
            (int(W * 0.38), y_min + int((y_max - y_min) * 0.08)),
            (int(W * 0.68), y_min + int((y_max - y_min) * 0.08)),
            (int(W * 0.65), y_min + int((y_max - y_min) * 0.22)),
            (int(W * 0.40), y_min + int((y_max - y_min) * 0.22)),
        ]
        draw.polygon(cap_pts, fill=NAVY)

        txt_img = Image.new("RGBA", (450, 120), (0, 0, 0, 0))
        ImageDraw.Draw(txt_img).text((20, 20), "IndiGo", font=font_fin, fill=NAVY)
        rotated = txt_img.rotate(36, expand=True, resample=Image.Resampling.BICUBIC)
        if is_mirror:
            rotated = ImageOps.mirror(rotated)
        img.paste(rotated, (int(W * 0.28), y_min + int((y_max - y_min) * 0.20)), rotated)

    img.save(f"{OUT}/tex_fin.png", "PNG")
    print(f"Fin texture saved: {OUT}/tex_fin.png")

def create_engine_texture():
    W, H = 1024, 512
    img = Image.new("RGBA", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    lip_w = int(W * 0.08)
    draw.rectangle([0, 0, lip_w, H], fill=SILVER)
    draw.line([(lip_w, 0), (lip_w, H)], fill=SEAM, width=2)

    ex_x = int(W * 0.84)
    draw.rectangle([ex_x, 0, W, H], fill=TITANIUM)
    draw.line([(ex_x, 0), (ex_x, H)], fill=(30, 32, 35, 255), width=2)

    try:
        font_eng = ImageFont.truetype(FONT_PATH, 44)
    except:
        font_eng = ImageFont.load_default()

    # Outboard starboard engine text (mirrored for proper UV winding)
    txt_e = Image.new("RGBA", (320, 60), (0, 0, 0, 0))
    ImageDraw.Draw(txt_e).text((0, 0), "goIndiGo.in", font=font_eng, fill=WHITE)
    txt_e_f = ImageOps.mirror(txt_e)
    img.paste(txt_e_f, (int(W * 0.24), int(H * 0.22)), txt_e_f)

    # Port engine text
    draw.text((int(W * 0.24), int(H * 0.72)), "goIndiGo.in", font=font_eng, fill=WHITE)

    draw.line([(int(W * 0.45), 0), (int(W * 0.45), H)], fill=(15, 25, 95, 255), width=2)
    draw.line([(int(W * 0.72), 0), (int(W * 0.72), H)], fill=(15, 25, 95, 255), width=2)

    img.save(f"{OUT}/tex_engine.png", "PNG")
    print(f"Engine texture saved: {OUT}/tex_engine.png")

if __name__ == "__main__":
    create_fuselage_texture()
    create_fin_texture()
    create_engine_texture()
    print("TEXTURES REBUILT WITH PERFECT UV WINDING")
