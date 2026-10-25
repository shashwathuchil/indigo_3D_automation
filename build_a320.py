"""
IndiGo A320neo — high-fidelity rebuild script.
Run: blender.exe --background --factory-startup --python D:/code/3d/build_a320.py
"""
import bpy, math, os
from mathutils import Vector

OUT = "D:/code/3d/models/indigo-a320"
os.makedirs(OUT, exist_ok=True)

# ── Scene reset ─────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0
sc.render.engine = 'BLENDER_EEVEE'

# ── Materials ────────────────────────────────────────────────────────────────
def mat(name, r, g, b, rough=0.35, metal=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b_ = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b_.inputs['Base Color'].default_value = (r, g, b, 1)
    b_.inputs['Roughness'].default_value = rough
    b_.inputs['Metallic'].default_value = metal
    if 'Coat Weight' in b_.inputs: b_.inputs['Coat Weight'].default_value = coat
    return m

MAT = {
    'white':   mat('mat_white',   0.93, 0.93, 0.95, rough=0.26, coat=0.35),
    'blue':    mat('mat_blue',    0.038, 0.055, 0.32, rough=0.32, metal=0.05),
    'cyan':    mat('mat_cyan',    0.14, 0.60, 0.72, rough=0.28, coat=0.2),
    'window':  mat('mat_window',  0.018, 0.022, 0.06, rough=0.08, metal=0.15),
    'exhaust': mat('mat_exhaust', 0.04, 0.04, 0.06, rough=0.55, metal=0.75),
    'silver':  mat('mat_silver',  0.60, 0.60, 0.63, rough=0.38, metal=0.85),
    'ground':  mat('mat_ground',  0.08, 0.09, 0.10, rough=0.90),
}

def link(ob):
    bpy.context.collection.objects.link(ob); return ob

# ── Helpers ──────────────────────────────────────────────────────────────────
def lerp_station(stations, y, col):
    for k in range(len(stations)-1):
        y0, y1 = stations[k][0], stations[k+1][0]
        if y0 <= y <= y1 and y1 > y0:
            t = (y-y0)/(y1-y0)
            return stations[k][col]*(1-t) + stations[k+1][col]*t
    return stations[-1][col]

# ── 1. FUSELAGE ──────────────────────────────────────────────────────────────
# A320neo: L=37.57m, max diam=4.14m (r=2.07)
# stations: (y_from_nose, ring_radius, z_center_offset)
fuse_stations = [
    (0.00,  0.05,  0.00),
    (0.20,  0.14,  0.00),
    (0.60,  0.36,  0.00),
    (1.30,  0.70,  0.00),
    (2.20,  1.08,  0.00),
    (3.40,  1.50,  0.00),
    (5.00,  1.82,  0.00),
    (6.50,  2.00,  0.00),
    (8.00,  2.07,  0.00),   # full section
    (11.00, 2.07,  0.00),
    (14.50, 2.07,  0.00),
    (17.00, 2.07,  0.00),
    (20.00, 2.07,  0.00),
    (23.00, 2.07,  0.00),
    (26.00, 2.07,  0.00),
    (28.50, 2.07,  0.00),
    (29.80, 2.05,  0.02),
    (30.80, 1.92,  0.13),
    (31.80, 1.72,  0.38),
    (32.80, 1.48,  0.72),
    (33.90, 1.18,  1.12),
    (35.00, 0.85,  1.58),
    (36.00, 0.55,  2.00),
    (36.80, 0.28,  2.38),
    (37.57, 0.07,  2.65),
]

N = 64
fuse_verts, fuse_faces = [], []
for (y, r, zc) in fuse_stations:
    for i in range(N):
        a = 2*math.pi*i/N
        fuse_verts.append((r*math.cos(a), y, zc + r*math.sin(a)))
S = len(fuse_stations)
for s in range(S-1):
    for i in range(N):
        j = (i+1)%N
        fuse_faces.append((s*N+i, s*N+j, (s+1)*N+j, (s+1)*N+i))
fuse_faces.append(tuple(range(N-1,-1,-1)))
fuse_faces.append(tuple((S-1)*N+i for i in range(N)))

me = bpy.data.meshes.new('fuse_mesh')
me.from_pydata(fuse_verts, [], fuse_faces); me.update()
fuse = bpy.data.objects.new('fuselage', me); link(fuse)
for k in ('white','blue','cyan','window'):
    fuse.data.materials.append(MAT[k])

# per-face material assignment
for p in me.polygons:
    c = p.center
    r  = lerp_station(fuse_stations, c.y, 1)
    zc = lerp_station(fuse_stations, c.y, 2)
    h  = (c.z - zc) / max(r, 0.01)   # -1=bottom, +1=top
    sx = abs(c.x)   / max(r, 0.01)   # 0=top/bottom, 1=sides
    # IndiGo: cyan narrow cheatline at equator sides, blue below, windows upper-side
    if   abs(h) < 0.06 and sx > 0.42:                                  p.material_index = 2  # cyan
    elif h < -0.06:                                                     p.material_index = 1  # blue
    elif 0.13 < h < 0.58 and sx > 0.65 and 8.5 < c.y < 33.0:          p.material_index = 3  # windows
    else:                                                               p.material_index = 0  # white
for p in me.polygons: p.use_smooth = True
print("fuselage OK  verts=%d" % len(me.vertices))

# ── 2. WINGS with airfoil profile ────────────────────────────────────────────
def naca_profile(t=0.12, n=10):
    """NACA 00XX symmetric, returns upper then lower (x,z) lists, TE..LE..TE order for a closed loop."""
    upper, lower = [], []
    for i in range(n+1):
        x = (1 - math.cos(math.pi*i/n)) / 2
        yt = 5*t*(0.2969*x**0.5 - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
        upper.append((x, yt)); lower.append((x, -yt))
    return upper, lower   # each runs LE→TE

def build_wing(name, side):
    # Wing sections: (span_x, y_LE, z_height, chord, thickness_frac)
    # A320neo semi-span from CL = 17.9m; wing root at x=±2.0 fuselage side
    # Root chord (at fuselage) ≈6.5m, tip ≈1.5m
    # LE sweep ~27°, dihedral 5°, TE slightly swept back
    sects = [
        (2.00, 13.50, -2.07, 6.5, 0.12),
        (4.50, 14.82, -1.73, 5.6, 0.115),
        (7.50, 16.47, -1.30, 4.5, 0.11),
        (10.5, 18.12, -0.87, 3.5, 0.105),
        (13.5, 19.77, -0.44, 2.5, 0.10),
        (16.2, 21.22, -0.08, 1.8, 0.095),
        (17.9, 22.07,  0.15, 1.5, 0.09),
    ]
    all_verts, all_faces = [], []
    # Per section: N_af = 10 → 21 profile vertices per section
    N_af = 10
    for si, (sx, yle, z, chord, thick) in enumerate(sects):
        up, lo = naca_profile(thick, N_af)
        # build closed loop: upper LE→TE, then lower reversed TE→LE (no duplicate LE)
        profile = up + lo[-2:0:-1]  # 2*N_af points per section (LE shared)
        n_p = len(profile)
        base = len(all_verts)
        for (xc, zc) in profile:
            # xc: 0=LE, 1=TE along chord; zc: airfoil thickness offset
            sweep_offset = (sx - 2.0) * math.tan(math.radians(27))
            px = side * sx
            py = yle + xc * chord
            pz = z + zc * chord
            all_verts.append((px, py, pz))
        if si < len(sects)-1:
            nb = base + n_p  # next section base
            for i in range(n_p):
                j = (i+1) % n_p
                all_faces.append((base+i, base+j, nb+j, nb+i))
    # root + tip caps
    n_p = 2*N_af
    all_faces.append(tuple(range(n_p)))
    all_faces.append(tuple(range(len(all_verts)-1, len(all_verts)-1-n_p, -1)))

    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(all_verts, [], all_faces); me.update()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.data.materials.append(MAT['white'])
    for p in ob.data.polygons: p.use_smooth = True
    return ob

build_wing('wing_R', +1)
build_wing('wing_L', -1)
print("wings OK")

# ── 3. VERTICAL FIN ──────────────────────────────────────────────────────────
# Root chord 7m (y=29.5 to y=36.5), tip chord 3m, height 7m, sweep ~40°, symmetric NACA 9%
def build_fin():
    # 5 spanwise sections along Z (vertical height)
    # (dz, y_LE, chord, thickness_frac)
    sects = [
        (0.0,  29.5, 7.0, 0.09),
        (1.5,  30.8, 6.2, 0.09),
        (3.0,  32.1, 5.2, 0.085),
        (5.0,  33.7, 4.0, 0.08),
        (7.0,  35.2, 3.0, 0.075),
    ]
    # z_base = top of fuselage at y~32 ≈ zc + r ≈ 1.3 + 2.07
    z_base = 1.3
    all_verts, all_faces = [], []
    N_af = 8
    for si, (dz, yle, chord, thick) in enumerate(sects):
        up, lo = naca_profile(thick, N_af)
        profile = up + lo[-2:0:-1]
        n_p = len(profile)
        base = len(all_verts)
        for (xc, zc_af) in profile:
            all_verts.append((xc*chord - chord*0.25, yle + xc*chord, z_base + dz + zc_af*chord))
        if si < len(sects)-1:
            nb = base + n_p
            for i in range(n_p):
                j = (i+1)%n_p
                all_faces.append((base+i, base+j, nb+j, nb+i))
    n_p = 2*N_af
    all_faces.append(tuple(range(n_p)))
    all_faces.append(tuple(range(len(all_verts)-1, len(all_verts)-1-n_p, -1)))
    me = bpy.data.meshes.new('fin_mesh')
    me.from_pydata(all_verts, [], all_faces); me.update()
    ob = bpy.data.objects.new('fin', me); link(ob)
    ob.data.materials.append(MAT['blue'])  # IndiGo fin is blue at top
    # lower fin portion white - remap
    for p in ob.data.materials: pass
    ob.data.materials.append(MAT['white'])
    for p in me.polygons:
        c = p.center
        ob_z = c.z - z_base
        ob.data.materials.append  # skip
        if ob_z > 3.5:
            p.material_index = 0   # blue (tip)
        else:
            p.material_index = 1   # white (base)
        p.use_smooth = True
    return ob
build_fin()
print("fin OK")

# ── 4. HORIZONTAL STABS ──────────────────────────────────────────────────────
def build_hstab(name, side):
    sects = [
        (0.8,  33.2, 3.4, 0.09),
        (2.5,  34.3, 2.8, 0.085),
        (4.2,  35.4, 2.1, 0.08),
        (5.8,  36.3, 1.4, 0.075),
        (6.6,  36.8, 1.1, 0.075),
    ]
    z_base = 2.05
    all_verts, all_faces = [], []
    N_af = 8
    for si, (sx, yle, chord, thick) in enumerate(sects):
        up, lo = naca_profile(thick, N_af)
        profile = up + lo[-2:0:-1]
        n_p = len(profile)
        base = len(all_verts)
        for (xc, zc_af) in profile:
            all_verts.append((side*sx, yle + xc*chord, z_base + zc_af*chord))
        if si < len(sects)-1:
            nb = base + n_p
            for i in range(n_p):
                j = (i+1)%n_p
                all_faces.append((base+i, base+j, nb+j, nb+i))
    n_p = 2*N_af
    all_faces.append(tuple(range(n_p)))
    all_faces.append(tuple(range(len(all_verts)-1, len(all_verts)-1-n_p, -1)))
    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(all_verts, [], all_faces); me.update()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.data.materials.append(MAT['white'])
    for p in me.polygons: p.use_smooth = True
    return ob
build_hstab('hstab_R', +1)
build_hstab('hstab_L', -1)
print("hstabs OK")

# ── 5. ENGINE NACELLES (CFM LEAP-1A style) ───────────────────────────────────
# Real LEAP-1A: fan dia 1.98m (r=0.99), nacelle length ~3.3m
# Position on A320: x=±4.5m from CL, z=-2.85m, y_center~16.5m (lon axis)
# The pylon hangs the engine ~3m below the wing
def build_engine(name, side):
    # Multi-station nacelle tube: (y_along_engine, outer_r, z_offset)
    # engine axis runs along Y; center at (x, y_ctr, z_ctr)
    x_ctr = side * 4.5
    y_ctr = 16.2   # LE of nacelle
    z_ctr = -3.00  # center height (below fuselage CL)
    # stations: (dist_from_LE, outer_r, inner_r)
    nac_stations = [
        (0.00, 1.00, 0.90),   # intake face
        (0.15, 1.05, 0.95),   # intake lip (slight flare)
        (0.40, 1.05, 0.0),    # fan cowl
        (1.00, 1.05, 0.0),    # fan cowl mid
        (1.80, 1.00, 0.0),    # bypass duct
        (2.50, 0.88, 0.0),    # core cowl
        (3.00, 0.78, 0.0),    # nozzle
        (3.30, 0.65, 0.0),    # exhaust exit
    ]
    M = 36  # nacelle ring segments
    verts, faces = [], []
    for (dist, ro, ri) in nac_stations:
        for i in range(M):
            a = 2*math.pi*i/M
            verts.append((x_ctr + ro*math.cos(a), y_ctr + dist, z_ctr + ro*math.sin(a)))
    N_st = len(nac_stations)
    for s in range(N_st-1):
        for i in range(M):
            j = (i+1)%M
            faces.append((s*M+i, s*M+j, (s+1)*M+j, (s+1)*M+i))
    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.data.materials.append(MAT['blue'])
    ob.data.materials.append(MAT['exhaust'])
    # exhaust section = last 2 rings
    for p in me.polygons:
        c = p.center
        if c.y > y_ctr + 2.5: p.material_index = 1
        p.use_smooth = True

    # Dark intake face disc
    bpy.ops.mesh.primitive_circle_add(vertices=M, radius=0.90, fill_type='TRIFAN',
        location=(x_ctr, y_ctr - 0.01, z_ctr))
    disc = bpy.context.object; disc.name = name+'_intake'
    disc.rotation_euler = (math.radians(90), 0, 0)
    disc.data.materials.append(MAT['exhaust'])

    # Fan spinner cone
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.30, radius2=0.0, depth=0.50,
        location=(x_ctr, y_ctr + 0.28, z_ctr))
    spin = bpy.context.object; spin.name = name+'_spinner'
    spin.rotation_euler = (math.radians(-90), 0, 0)
    spin.data.materials.append(MAT['silver'])
    for p in spin.data.polygons: p.use_smooth = True

    # Pylon: swept trapezoidal wedge
    py = 0.14  # pylon half-thickness
    wing_z = -1.35  # approx wing attachment z at engine spanwise pos
    pylon_verts = [
        (x_ctr-py, 15.0, wing_z),   (x_ctr+py, 15.0, wing_z),
        (x_ctr+py, 17.5, wing_z),   (x_ctr-py, 17.5, wing_z),
        (x_ctr-py, 15.5, z_ctr+1.05),(x_ctr+py, 15.5, z_ctr+1.05),
        (x_ctr+py, 17.8, z_ctr+1.05),(x_ctr-py, 17.8, z_ctr+1.05),
    ]
    pylon_faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]
    pme = bpy.data.meshes.new(name+'_pylon_mesh')
    pme.from_pydata(pylon_verts, [], pylon_faces); pme.update()
    pob = bpy.data.objects.new(name+'_pylon', pme); link(pob)
    pob.data.materials.append(MAT['blue'])
    bev = pob.modifiers.new('bev', 'BEVEL'); bev.width = 0.08; bev.segments = 2

    return ob

build_engine('engine_R', +1)
build_engine('engine_L', -1)
print("engines OK")

# ── 6. SHARKLETS (proper curved winglets) ────────────────────────────────────
def build_sharklet(name, side):
    # Tip of A320neo sharklet: curved upward winglet, ~2.4m height
    # Starts at wing tip (x=±17.9, y≈22, z≈0.15)
    # Curves upward; narrow chord ~1.0m, swept back ~55°
    tip_x = side * 17.9
    tip_y = 22.1
    tip_z = 0.15
    sects = [
        (0.0,  0.0,  1.0, 0.09),   # (dz_up, dx_out, chord, thick)
        (0.6,  side*0.25, 0.85, 0.088),
        (1.2,  side*0.45, 0.70, 0.085),
        (1.8,  side*0.55, 0.55, 0.08),
        (2.4,  side*0.60, 0.35, 0.075),
    ]
    all_verts, all_faces = [], []
    N_af = 7
    for si, (dz, dx, chord, thick) in enumerate(sects):
        up, lo = naca_profile(thick, N_af)
        profile = up + lo[-2:0:-1]
        n_p = len(profile)
        base = len(all_verts)
        for (xc, zc_af) in profile:
            sweep_y = dz * math.tan(math.radians(55))
            all_verts.append((tip_x + dx, tip_y + sweep_y + xc*chord, tip_z + dz + zc_af*chord))
        if si < len(sects)-1:
            nb = base + n_p
            for i in range(n_p):
                j = (i+1)%n_p
                all_faces.append((base+i, base+j, nb+j, nb+i))
    n_p = 2*N_af
    all_faces.append(tuple(range(n_p)))
    all_faces.append(tuple(range(len(all_verts)-1, len(all_verts)-1-n_p, -1)))
    me = bpy.data.meshes.new(name+'_mesh')
    me.from_pydata(all_verts, [], all_faces); me.update()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.data.materials.append(MAT['blue'])
    for p in me.polygons: p.use_smooth = True
    return ob

build_sharklet('sharklet_R', +1)
build_sharklet('sharklet_L', -1)
print("sharklets OK")

# ── 7. COCKPIT NOSE GLAZING ──────────────────────────────────────────────────
def build_cockpit_glazing():
    # Dark visor panels on forward upper fuselage; modeled as a shallow dome inset
    # 2 flat-angled panels per side
    segs = 10
    panels = []
    for side in (-1, 1):
        # Forward windscreen panel (roughly at y=3.5 to 5.5, upper side)
        for (y0, y1, h0, h1, ang0, ang1) in [
            (3.5, 5.5, 0.45, 0.90, 50, 80),   # main windscreen
            (5.5, 7.2, 0.30, 0.68, 40, 70),    # side windows
        ]:
            verts_p = []
            for y, h, ang in [(y0, h0, ang0), (y1, h1, ang1)]:
                r = lerp_station(fuse_stations, y, 1)
                zc = lerp_station(fuse_stations, y, 2)
                for da in range(segs+1):
                    a_deg = ang0 + (ang1 - ang0)*da/segs
                    a = math.radians(a_deg) * (math.pi/2) / (math.pi/2)
                    a = math.radians(ang + (90-ang)*da/segs) if False else math.radians(a_deg)
                    x = side * r * math.sin(a)
                    z = zc + r * math.cos(a)
                    verts_p.append((x, y, z + 0.02))  # slight offset outward
            n = segs + 1
            fs = []
            for i in range(segs):
                fs.append((i, i+1, n+i+1, n+i))
            me_p = bpy.data.meshes.new('cpit_mesh')
            me_p.from_pydata(verts_p, [], fs); me_p.update()
            ob_p = bpy.data.objects.new('cockpit_glz', me_p); link(ob_p)
            ob_p.data.materials.append(MAT['window'])
            for p in me_p.polygons: p.use_smooth = True

build_cockpit_glazing()
print("cockpit glazing OK")

# ── 8. INDIVIDUAL WINDOWS ────────────────────────────────────────────────────
# A320 has ~30 windows per side, spaced ~0.53m apart from y≈8.5 to y≈32
WIN_SPACING = 0.53
WIN_START   = 8.8
WIN_END     = 32.5
WIN_ANGLE   = math.radians(62)  # ~62° from top (upper side, just above cyan line)
WIN_W       = 0.22  # window width along fuselage axis
WIN_H_RATIO = 0.11  # height as fraction of local radius

win_ys = [WIN_START + i*WIN_SPACING for i in range(int((WIN_END-WIN_START)/WIN_SPACING)+1)]
print(f"  adding {len(win_ys)*2} window patches")
for wy in win_ys:
    r  = lerp_station(fuse_stations, wy, 1)
    zc = lerp_station(fuse_stations, wy, 2)
    for side in (-1, +1):
        a = WIN_ANGLE * side if side > 0 else math.pi - WIN_ANGLE
        cx = r * math.cos(a)
        cz = zc + r * math.sin(a)
        dz = r * WIN_H_RATIO
        bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, wy, cz + 0.03))
        w = bpy.context.object; w.name = 'win'
        # orient flat to fuselage surface
        normal = Vector((cx, 0, cz - zc)).normalized()
        w.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()
        w.scale = (0.13, WIN_W/2, 1)
        w.data.materials.append(MAT['window'])

print("windows OK")

# ── 9. MASTER EMPTY + PARENT ─────────────────────────────────────────────────
master = bpy.data.objects.new('indigo-a320', None)
bpy.context.collection.objects.link(master)
for o in bpy.data.objects:
    if o != master and o.parent is None and o.name != 'ground':
        o.parent = master

# ── 10. LIGHTS ───────────────────────────────────────────────────────────────
def area_light(name, loc, energy, size, color=(1,1,1)):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.shape, d.size, d.color = energy, 'DISK', size, color
    o = bpy.data.objects.new(name, d); bpy.context.collection.objects.link(o)
    o.location = loc
    target = Vector((0, 18.5, 1.2))  # aircraft center (pre-normalize)
    o.rotation_euler = (target - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o
area_light('LGT_key',  (10, 3,  22), 40000, 12, (1.0, 0.96, 0.9))
area_light('LGT_fill', (-9, 5,  14), 18000, 12, (0.85, 0.9, 1.0))
area_light('LGT_rim',  (2,  40, 20), 28000, 10, (1.0, 1.0, 1.0))

w = bpy.data.worlds.new('world')
bpy.context.scene.world = w; w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs['Color'].default_value = (0.04, 0.045, 0.055, 1)
bg.inputs['Strength'].default_value = 0.4

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 18.5, -2.08))
gnd = bpy.context.object; gnd.name = 'ground'
gnd.data.materials.append(MAT['ground'])

# ── 11. CAMERA + RENDER ──────────────────────────────────────────────────────
cd = bpy.data.cameras.new('CAM'); cam = bpy.data.objects.new('CAM', cd)
bpy.context.collection.objects.link(cam); cd.lens = 80
# 3/4 view from front-left-above, looking toward mid-fuselage
cam.location = (-18, -6, 15)
target = Vector((0, 18, 1))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

sc = bpy.context.scene
sc.render.resolution_x = sc.render.resolution_y = 1024
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = f"{OUT}/render_hq.png"
sc.render.film_transparent = False
print("Rendering...")
bpy.ops.render.render(write_still=True)
print("Render done")

# ── 12. SAVE .blend ──────────────────────────────────────────────────────────
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/model.blend")
print("Saved .blend")

# ── 13. EXPORT Draco GLB (model mesh only) ───────────────────────────────────
# Select only aircraft parts (exclude ground, lights, camera)
bpy.ops.object.select_all(action='DESELECT')
exclude = {'ground', 'CAM', 'LGT_key', 'LGT_fill', 'LGT_rim'}
for o in bpy.data.objects:
    if o.name not in exclude and o.type in {'MESH', 'EMPTY'}:
        o.select_set(True)

kwargs = dict(
    filepath=f"{OUT}/model.glb",
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_texcoords=True,
    export_normals=True,
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_image_format='WEBP',
)
valid = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
kwargs = {k: v for k, v in kwargs.items() if k in valid}
try:
    bpy.ops.export_scene.gltf(**kwargs)
except Exception as e:
    kwargs['export_image_format'] = 'AUTO'; bpy.ops.export_scene.gltf(**kwargs)
import os as _os
print(f"GLB bytes: {_os.path.getsize(OUT+'/model.glb')}")
print("DONE")
