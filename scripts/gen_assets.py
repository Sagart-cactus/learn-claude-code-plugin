#!/usr/bin/env python3
"""Generate header images + animated GIF diagrams for the promo articles.
Brand: warm-ink dark, clay accent, blueprint grid — matching the website."""

import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── paths ──────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "articles", "assets")
os.makedirs(OUT, exist_ok=True)

# ── palette ────────────────────────────────────────────────────────
INK      = (14, 11, 9)
INK2     = (21, 17, 13)
PANEL    = (29, 23, 16)
PANEL2   = (37, 29, 20)
GRID     = (30, 26, 21)
LINE     = (60, 52, 44)
CLAY     = (223, 129, 88)
CLAY_SFT = (239, 157, 115)
SKY      = (109, 185, 196)
SKY_SFT  = (146, 205, 214)
CREAM    = (244, 235, 223)
CREAM_D  = (217, 203, 184)
MUTED    = (156, 139, 120)
FAINT    = (111, 96, 82)
OK       = (136, 184, 144)
DANGER   = (224, 106, 90)

S = 2  # supersampling factor
FONTS = {
    "heavy":  ("/System/Library/Fonts/Avenir Next.ttc", 8),
    "bold":   ("/System/Library/Fonts/Avenir Next.ttc", 0),
    "demi":   ("/System/Library/Fonts/Avenir Next.ttc", 2),
    "medium": ("/System/Library/Fonts/Avenir Next.ttc", 5),
    "mono":   ("/System/Library/Fonts/Menlo.ttc", 0),
    "monob":  ("/System/Library/Fonts/Menlo.ttc", 1),
}
_cache = {}
def font(weight, size):
    key = (weight, size)
    if key not in _cache:
        path, idx = FONTS[weight]
        _cache[key] = ImageFont.truetype(path, int(size * S), index=idx)
    return _cache[key]

# ── drawing helpers (logical coords, auto-scaled by S) ─────────────
class Pen:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img, "RGBA")
    def _b(self, box): return [c * S for c in box]
    def rrect(self, box, r=10, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._b(box), radius=r * S, fill=fill,
                                 outline=outline, width=max(1, int(width * S)))
    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle(self._b(box), fill=fill, outline=outline, width=max(1, int(width * S)))
    def line(self, pts, fill, width=1):
        self.d.line([c * S for c in pts], fill=fill, width=max(1, int(width * S)))
    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse(self._b(box), fill=fill, outline=outline, width=max(1, int(width * S)))
    def text(self, xy, s, weight, size, fill, anchor="lm", spacing=4):
        self.d.text((xy[0] * S, xy[1] * S), s, font=font(weight, size),
                    fill=fill, anchor=anchor, spacing=spacing * S)
    def tw(self, s, weight, size):
        return self.d.textlength(s, font=font(weight, size)) / S

def base(w, h, glows=()):
    """RGB canvas: ink + blueprint grid + soft blurred glows."""
    img = Image.new("RGB", (w * S, h * S), INK)
    d = ImageDraw.Draw(img)
    step = 38 * S
    for x in range(0, w * S, step):
        d.line([(x, 0), (x, h * S)], fill=GRID, width=1)
    for y in range(0, h * S, step):
        d.line([(0, y), (w * S, y)], fill=GRID, width=1)
    if glows:
        gl = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        for (gx, gy, gr, col, a) in glows:
            gd.ellipse([(gx - gr) * S, (gy - gr) * S, (gx + gr) * S, (gy + gr) * S],
                       fill=col + (a,))
        gl = gl.filter(ImageFilter.GaussianBlur(48 * S))
        img = Image.alpha_composite(img.convert("RGBA"), gl).convert("RGB")
    return img

def wordmark(pen, x, y):
    """small 4-square glyph + claude·plugins."""
    s = 7
    cols = [CLAY, SKY, CLAY_SFT, CREAM_D]
    k = 0
    for ry in (0, 1):
        for rx in (0, 1):
            pen.rrect([x + rx * (s + 2), y + ry * (s + 2), x + rx * (s + 2) + s, y + ry * (s + 2) + s], r=2, fill=cols[k])
            k += 1
    pen.text((x + 2 * s + 8, y + s), "claude·plugins", "monob", 11, CREAM)

def downscale(img, w, h):
    return img.resize((w, h), Image.LANCZOS)

def soft_dot(pen, x, y, r, col, glow=True):
    if glow:
        for gr, a in ((r * 2.4, 40), (r * 1.6, 70)):
            pen.ellipse([x - gr, y - gr, x + gr, y + gr], fill=col + (a,))
    pen.ellipse([x - r, y - r, x + r, y + r], fill=col)

# ═══════════════════════════════════════════════════════════════════
#  HEADER IMAGES  (1200 x 630)
# ═══════════════════════════════════════════════════════════════════
HW, HH = 1200, 630

def block_cluster(pen, cx, cy, accent, lit=1):
    """3x3 cluster of rounded squares, one accented."""
    s, gap = 46, 12
    labels = ["", "", "", "", "", "", "", "", ""]
    k = 0
    for ry in range(3):
        for rx in range(3):
            x = cx + rx * (s + gap)
            y = cy + ry * (s + gap)
            on = (k == lit)
            pen.rrect([x, y, x + s, y + s], r=10,
                      fill=(PANEL2 if on else PANEL),
                      outline=(accent if on else LINE), width=2 if on else 1)
            if on:
                pen.rrect([x + 14, y + 14, x + s - 14, y + s - 14], r=4, outline=accent, width=2)
            k += 1

def header(fname, kicker, lines, sub, tag, accent=CLAY, motif="blocks"):
    img = base(HW, HH, glows=[
        (HW - 130, -40, 360, accent, 60),
        (40, HH - 40, 320, SKY, 26),
    ])
    pen = Pen(img)
    wordmark(pen, 64, 54)
    # kicker
    pen.text((64, 150), kicker.upper(), "monob", 15, accent)
    pen.line([64, 168, 64 + 46, 168], accent, 2)
    # headline
    y = 210
    for ln in lines:
        pen.text((62, y), ln, "heavy", 52, CREAM, anchor="lm")
        y += 64
    # subtitle
    pen.text((64, y + 18), sub, "medium", 21, MUTED, anchor="lm")
    # tag bottom
    pen.rrect([64, HH - 92, 64 + 14, HH - 78], r=3, fill=accent)
    pen.text((86, HH - 85), tag, "mono", 13, CREAM_D)
    # motif lower-right
    if motif == "blocks":
        block_cluster(pen, HW - 330, HH - 320, accent, lit=4)
    elif motif == "bars":
        bx, by = HW - 360, HH - 250
        vals = [0.35, 0.55, 0.7, 0.5, 0.85, 0.65, 0.95, 0.45]
        for i, v in enumerate(vals):
            x = bx + i * 34
            pen.rrect([x, by + int(150 * (1 - v)), x + 22, by + 150], r=5,
                      fill=accent if i == 6 else PANEL2, outline=LINE, width=1)
    elif motif == "shield":
        cx, cy = HW - 250, HH - 250
        pts = [(cx, cy - 110), (cx + 95, cy - 70), (cx + 95, cy + 30),
               (cx, cy + 110), (cx - 95, cy + 30), (cx - 95, cy - 70)]
        pen.d.polygon([(p[0] * S, p[1] * S) for p in pts], outline=accent, width=3 * S, fill=(accent[0], accent[1], accent[2], 18))
        pen.text((cx, cy), "✓", "heavy", 60, accent, anchor="mm")
    elif motif == "loop":
        cx, cy, r = HW - 250, HH - 250, 110
        pen.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LINE, width=2)
        for i, a in enumerate((-90, 0, 90, 180)):
            nx = cx + r * math.cos(math.radians(a))
            ny = cy + r * math.sin(math.radians(a))
            soft_dot(pen, nx, ny, 11, accent if i == 0 else PANEL2, glow=(i == 0))
        soft_dot(pen, cx + r, cy, 9, accent)
    elif motif == "route":
        tx, ty = HW - 430, HH - 250
        pen.rrect([tx, ty + 40, tx + 120, ty + 100], r=10, fill=PANEL, outline=SKY, width=2)
        ops = [("docs", LINE, PANEL), ("match", accent, PANEL2), ("tests", LINE, PANEL)]
        for i, (lab, oc, fc) in enumerate(ops):
            ox = tx + 230
            oy = ty + i * 56
            pen.rrect([ox, oy + 6, ox + 130, oy + 46], r=8, fill=fc, outline=oc, width=2 if i == 1 else 1)
        pen.line([tx + 120, ty + 70, tx + 230, ty + 64], accent, 3)
    img = downscale(img, HW, HH)
    img.save(os.path.join(OUT, fname), "PNG")
    print("  header", fname)

# ═══════════════════════════════════════════════════════════════════
#  GIF ENGINE
# ═══════════════════════════════════════════════════════════════════
def save_gif(fname, frames, duration=70):
    frames[0].save(os.path.join(OUT, fname), save_all=True,
                   append_images=frames[1:], duration=duration, loop=0,
                   optimize=True, disposal=2)
    print("  gif   ", fname, f"({len(frames)} frames)")

def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))
def smooth(t): return t * t * (3 - 2 * t)

def gif_render(w, h, n, draw_frame, glows=(), fname=None, duration=70, static=None):
    bg = base(w, h, glows=glows)
    if static:
        static(Pen(bg))
    frames = []
    for i in range(n):
        t = i / n
        fr = bg.copy()
        draw_frame(Pen(fr), t, i)
        frames.append(downscale(fr, w, h).convert("P", palette=Image.ADAPTIVE, colors=128))
    save_gif(fname, frames, duration)

def caption(pen, w, text, accent=CLAY):
    pen.rrect([24, 22, 24 + 11, 33], r=2, fill=accent)
    pen.text((44, 28), text, "mono", 12, MUTED)

# ── A. capability bloom ─────────────────────────────────────────────
def gif_capabilities():
    W, H = 760, 340
    cx, cy, R = W // 2, H // 2 + 8, 120
    labels = ["skills", "agents", "hooks", "mcp", "lsp", "monitors"]
    def static(pen):
        caption(pen, W, "one plugin  ·  many capabilities")
    def frame(pen, t, i):
        # connectors + nodes
        head = t * 6.0
        for k, lab in enumerate(labels):
            ang = math.radians(-90 + k * 60)
            nx, ny = cx + R * math.cos(ang), cy + R * math.sin(ang)
            d = (head - k) % 6
            lit = max(0.0, 1 - d) if d < 1 else (max(0.0, 1 - (6 - d)) if d > 5 else 0.0)
            lc = mix(LINE, CLAY, lit)
            pen.line([cx, cy, nx, ny], mix(GRID, CLAY, lit * 0.8), 1 + lit)
            w2 = 34
            pen.rrect([nx - w2, ny - 14, nx + w2, ny + 14], r=8,
                      fill=mix(PANEL, PANEL2, lit), outline=lc, width=1 + int(lit + 0.4))
            pen.text((nx, ny), lab, "monob", 11, mix(MUTED, CLAY_SFT, lit), anchor="mm")
            if lit > 0.4:
                soft_dot(pen, nx, ny - 22, 3 + 2 * lit, CLAY_SFT)
        # core with pulsing ring
        pr = 4 * math.sin(t * 2 * math.pi)
        pen.ellipse([cx - 58 - pr, cy - 58 - pr, cx + 58 + pr, cy + 58 + pr], outline=mix(INK2, CLAY, 0.4), width=1)
        pen.rrect([cx - 52, cy - 40, cx + 52, cy + 40], r=16, fill=(35, 24, 18), outline=CLAY, width=2)
        pen.text((cx, cy - 9), "Claude", "demi", 18, CLAY_SFT, anchor="mm")
        pen.text((cx, cy + 13), "Code", "demi", 18, CLAY_SFT, anchor="mm")
    gif_render(W, H, 48, frame, fname="cap-bloom.gif",
               glows=[(cx, cy, 200, CLAY, 30)], static=static, duration=70)

# ── B. activation sequence ──────────────────────────────────────────
def gif_activation():
    W, H = 760, 300
    chips = ["manifest", "skills", "agents", "hooks", "mcp", "lsp", "monitors"]
    cw, gap = 86, 10
    total = len(chips) * cw + (len(chips) - 1) * gap
    x0 = (W - total) // 2
    cy = H // 2 + 6
    def static(pen):
        caption(pen, W, "activation  ·  all before Claude's first reply")
    def frame(pen, t, i):
        head = t * (len(chips) + 1.2)
        scan_x = x0 + (t * (total + 40)) - 20
        for k, c in enumerate(chips):
            x = x0 + k * (cw + gap)
            lit = 1.0 if head > k + 0.5 else 0.0
            oc = mix(LINE, OK, lit)
            pen.rrect([x, cy - 20, x + cw, cy + 20], r=9,
                      fill=mix(PANEL, (24, 30, 22), lit), outline=oc, width=1 + int(lit))
            pen.text((x + cw / 2, cy), c, "monob", 11, mix(MUTED, OK, lit), anchor="mm")
            if lit:
                pen.text((x + cw - 13, cy - 12), "✓", "monob", 10, OK, anchor="mm")
        # scan bar
        if x0 - 20 < scan_x < x0 + total + 20:
            pen.line([scan_x, cy - 34, scan_x, cy + 34], CLAY_SFT, 2)
            soft_dot(pen, scan_x, cy - 34, 4, CLAY_SFT)
    gif_render(W, H, 50, frame, fname="activation.gif",
               glows=[(W // 2, cy, 240, CLAY, 18)], static=static, duration=66)

# ── C. hook feedback loop ───────────────────────────────────────────
def gif_hookloop():
    W, H = 760, 340
    cx, cy, R = W // 2, H // 2 + 6, 108
    nodes = [("you write code", -90), ("PostToolUse hook", 0), ("lint / test output", 90), ("Claude fixes it", 180)]
    def static(pen):
        caption(pen, W, "the hook → Claude feedback loop")
        pen.ellipse([cx - R, cy - R, cx + R, cy + R], outline=LINE, width=1)
        pen.text((cx, cy - 8), "AUTO", "monob", 12, MUTED, anchor="mm")
        pen.text((cx, cy + 12), "CORRECT", "monob", 12, MUTED, anchor="mm")
    def frame(pen, t, i):
        head = (t * 4) % 4
        # traveling dot
        ang = math.radians(-90 + t * 360)
        dx, dy = cx + R * math.cos(ang), cy + R * math.sin(ang)
        for k, (lab, a) in enumerate(nodes):
            nx = cx + R * math.cos(math.radians(a))
            ny = cy + R * math.sin(math.radians(a))
            d = (head - k) % 4
            lit = max(0.0, 1 - d * 1.4)
            oc = mix(LINE, CLAY, lit)
            tw = pen.tw(lab, "monob", 11) / 2 + 12
            pen.rrect([nx - tw, ny - 15, nx + tw, ny + 15], r=9,
                      fill=mix(PANEL, PANEL2, lit), outline=oc, width=1 + int(lit + .3))
            pen.text((nx, ny), lab, "monob", 11, mix(CREAM_D, CLAY_SFT, lit), anchor="mm")
        soft_dot(pen, dx, dy, 7, CLAY_SFT)
    gif_render(W, H, 52, frame, fname="hook-loop.gif",
               glows=[(cx, cy, 200, CLAY, 22)], static=static, duration=64)

# ── D. hook pipeline (Pre/Tool/Post) ────────────────────────────────
def gif_hookflow():
    W, H = 820, 240
    stops = ["request", "pick tool", "PreToolUse", "tool runs", "PostToolUse", "continue"]
    cols = [MUTED, MUTED, SKY, CLAY, SKY, MUTED]
    cw = 116; gap = 18
    total = len(stops) * cw + (len(stops) - 1) * gap
    x0 = (W - total) // 2; cy = H // 2 + 6
    centers = [x0 + k * (cw + gap) + cw / 2 for k in range(len(stops))]
    def static(pen):
        caption(pen, W, "every tool call runs the gauntlet")
        for k, s in enumerate(stops):
            x = x0 + k * (cw + gap)
            accent = cols[k]
            pen.rrect([x, cy - 22, x + cw, cy + 22], r=9, fill=PANEL,
                      outline=mix(LINE, accent, 0.5) if accent in (SKY, CLAY) else LINE, width=1)
            pen.text((x + cw / 2, cy), s, "monob", 11, mix(MUTED, accent, 0.6) if accent in (SKY, CLAY) else CREAM_D, anchor="mm")
            if k < len(stops) - 1:
                ax = x + cw + 2
                pen.line([ax, cy, ax + gap - 4, cy], FAINT, 2)
    def frame(pen, t, i):
        p = t * (len(centers) - 1)
        seg = min(int(p), len(centers) - 2)
        ft = p - seg
        dx = lerp(centers[seg], centers[seg + 1], smooth(ft))
        soft_dot(pen, dx, cy, 7, CLAY_SFT)
    gif_render(W, H, 48, frame, fname="hook-flow.gif",
               glows=[(W // 2, cy, 260, CLAY, 14)], static=static, duration=66)

# ── E. routing by description ───────────────────────────────────────
def gif_routing():
    W, H = 760, 320
    tx, ty = 70, H // 2 - 40
    skills = ["format-docs", "security-review", "run-tests"]
    match = 1
    sx = W - 300; sy = H // 2 - 76
    sh = 50; sgap = 12
    def static(pen):
        caption(pen, W, "the description is the router")
        pen.rrect([tx, ty, tx + 220, ty + 78], r=12, fill=(18, 24, 26), outline=SKY, width=2)
        pen.text((tx + 18, ty + 28), "“review this PR", "demi", 15, CREAM, anchor="lm")
        pen.text((tx + 18, ty + 52), "for security”", "demi", 15, CREAM, anchor="lm")
    def frame(pen, t, i):
        scan = (t * 3.2)
        for k, s in enumerate(skills):
            y = sy + k * (sh + sgap)
            hover = 1.0 if (scan > k and scan < k + 1.1 and t < 0.55) else 0.0
            locked = 1.0 if (t >= 0.55 and k == match) else 0.0
            on = max(hover, locked)
            acc = CLAY if locked else (CREAM_D if hover else LINE)
            pen.rrect([sx, y, sx + 230, y + sh], r=10,
                      fill=mix(PANEL, PANEL2, on), outline=acc, width=1 + int(on + .3))
            pen.text((sx + 18, y + sh / 2), s, "monob", 13,
                     mix(MUTED, CLAY_SFT, locked) if locked else mix(MUTED, CREAM, hover), anchor="lm")
        # beam draws after lock
        if t >= 0.58:
            bt = smooth(min(1, (t - 0.58) / 0.28))
            ymatch = sy + match * (sh + sgap) + sh / 2
            bx0 = tx + 220
            bx1 = lerp(bx0, sx, bt)
            pen.line([bx0, ty + 39, bx1, ymatch], CLAY, 3)
            soft_dot(pen, bx1, lerp(ty + 39, ymatch, 1), 5, CLAY_SFT)
    gif_render(W, H, 54, frame, fname="routing.gif",
               glows=[(sx + 100, H // 2, 200, CLAY, 18)], static=static, duration=66)

# ── F. validation gate ──────────────────────────────────────────────
def gif_gate():
    W, H = 760, 320
    gate_x = int(W * 0.62); top = 60; bot = H - 50
    lanes = [0.30, 0.46, 0.62]
    def static(pen):
        caption(pen, W, "validate every input, allowlist the rest", DANGER)
        pen.text((70, H // 2), "hook\nstdin", "monob", 12, MUTED, anchor="mm", spacing=3)
        pen.text((W - 70, H // 2), "tool\nruns", "monob", 12, OK, anchor="mm", spacing=3)
        pen.line([gate_x, top, gate_x, bot], CLAY_SFT, 3)
        pen.text((gate_x, top - 22), "VALIDATE", "monob", 11, CLAY_SFT, anchor="mm")
    def lane_y(f): return int(H * f)
    def frame(pen, t, i):
        # ok packets
        for li, f in enumerate(lanes):
            phase = (t + li * 0.31) % 1.0
            x = lerp(130, W - 120, phase)
            y = lane_y(f)
            soft_dot(pen, x, y, 7, OK)
        # bad packet
        bp = (t * 1.0) % 1.0
        by = H - 70
        if bp < 0.46:
            x = lerp(130, gate_x - 16, bp / 0.46)
            soft_dot(pen, x, by, 7, DANGER)
        elif bp < 0.72:
            sh = math.sin(bp * 60) * 3
            soft_dot(pen, gate_x - 16 + sh, by, 7, DANGER)
            pen.text((gate_x - 16, by - 22), "✕", "monob", 13, DANGER, anchor="mm")
    gif_render(W, H, 50, frame, fname="gate.gif",
               glows=[(gate_x, H // 2, 160, CLAY, 16), (W - 90, H // 2, 120, OK, 12)],
               static=static, duration=64)

# ── G. trust pyramid ────────────────────────────────────────────────
def gif_pyramid():
    W, H = 700, 340
    tiers = [("monitors · bin", 0.34, SKY), ("MCP servers", 0.52, SKY_SFT),
             ("hooks", 0.72, CLAY), ("skills · agents", 0.92, CLAY_SFT)]
    cx = W // 2; top = 66; th = 42; tg = 8
    bottom = top + len(tiers) * (th + tg)
    def static(pen):
        caption(pen, W, "you trust every component inside", DANGER)
        # tiers are always present
        for k, (lab, wf, col) in enumerate(tiers):
            w = int(W * wf * 0.84)
            y = top + k * (th + tg)
            pen.rrect([cx - w // 2, y, cx + w // 2, y + th], r=8, fill=col)
            pen.text((cx, y + th // 2), lab, "monob", 12, (22, 16, 12), anchor="mm")
        pen.text((cx, bottom + 18), "a single bad component can exfiltrate keys or run code",
                 "monob", 12, DANGER, anchor="mm")
    def frame(pen, t, i):
        # red scan sweeping top→bottom, highlighting the tier it crosses
        sy = lerp(top - 6, bottom + 2, t)
        for k, (lab, wf, col) in enumerate(tiers):
            y = top + k * (th + tg)
            if y - 6 <= sy <= y + th + 6:
                w = int(W * wf * 0.84)
                pen.rrect([cx - w // 2 - 3, y - 3, cx + w // 2 + 3, y + th + 3], r=10,
                          outline=DANGER, width=2)
        pen.line([60, sy, W - 60, sy], (DANGER[0], DANGER[1], DANGER[2], 150), 2)
        soft_dot(pen, 60, sy, 4, DANGER)
        soft_dot(pen, W - 60, sy, 4, DANGER)
    gif_render(W, H, 46, frame, fname="trust-pyramid.gif",
               glows=[(cx, top + 100, 220, DANGER, 16)], static=static, duration=70)

# ── H. 20 min vs 2 min ──────────────────────────────────────────────
def gif_compress():
    W, H = 760, 300
    mlabel_y = 96; plabel_y = 196
    bx = 150; bw = W - 200
    def static(pen):
        caption(pen, W, "~20 minutes collapses to ~2")
        pen.text((44, mlabel_y - 28), "MANUAL · 8 STEPS · ~20 MIN", "monob", 12, DANGER)
        pen.text((44, plabel_y - 28), "PLUGIN · ONE COMMAND · ~2 MIN", "monob", 12, OK)
    def frame(pen, t, i):
        # manual: 8 staggered segments
        seg = bw / 8; pad = 6
        for k in range(8):
            x = bx + k * seg
            pen.rrect([x, mlabel_y, x + seg - pad, mlabel_y + 30], r=5, fill=PANEL, outline=LINE, width=1)
            local = max(0.0, min(1.0, (t * 8) - k))
            if local > 0:
                fillw = (seg - pad) * smooth(local)
                pen.rrect([x, mlabel_y, x + fillw, mlabel_y + 30], r=5, fill=DANGER)
        # plugin: one bar fills fast
        pen.rrect([bx, plabel_y, bx + bw - pad, plabel_y + 30], r=5, fill=PANEL, outline=LINE, width=1)
        pf = smooth(max(0.0, min(1.0, t * 8)))
        pen.rrect([bx, plabel_y, bx + (bw - pad) * pf, plabel_y + 30], r=5, fill=OK)
        if t * 8 >= 1:
            pen.text((bx + bw - pad + 16, plabel_y + 15), "done", "monob", 12, OK, anchor="lm")
    gif_render(W, H, 48, frame, fname="compress.gif",
               glows=[(W // 2, H // 2, 240, CLAY, 12)], static=static, duration=72)

# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Headers:")
    header("hdr-capabilities.png", "Claude Code · Plugins",
           ["Stop re-explaining", "your stack to your AI", "every single morning."],
           "Plugins give Claude permanent memory of how your team works.",
           "the definitive guide  ·  chapter 01", accent=CLAY, motif="blocks")
    header("hdr-hooks.png", "Claude Code · Hooks",
           ["Your standards,", "enforced while", "you sleep."],
           "How hooks turn “please follow the style guide” into a guarantee.",
           "the definitive guide  ·  chapter 08", accent=CLAY, motif="loop")
    header("hdr-description.png", "Claude Code · Skills",
           ["The most important", "code in your plugin", "isn’t code."],
           "Why a single description field decides what your AI actually does.",
           "the definitive guide  ·  chapter 10", accent=SKY, motif="route")
    header("hdr-security.png", "Claude Code · Security",
           ["The plugin you", "didn’t audit is one", "you can’t trust."],
           "The security model every Claude Code power-user should know.",
           "the definitive guide  ·  chapter 07", accent=DANGER, motif="shield")
    header("hdr-workflow.png", "Claude Code · Workflows",
           ["From a 20-minute", "chore to a", "2-minute command."],
           "Designing Claude Code plugins for the work you repeat every day.",
           "the definitive guide  ·  chapter 08", accent=CLAY, motif="bars")

    print("GIFs:")
    gif_capabilities()
    gif_activation()
    gif_hookloop()
    gif_hookflow()
    gif_routing()
    gif_gate()
    gif_pyramid()
    gif_compress()
    print("Done →", OUT)
