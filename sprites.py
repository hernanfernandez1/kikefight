"""
sprites.py – draws every animation frame for Kike and the Blue Fighter
using pygame.draw primitives.  All poses taken from the reference images.

Coordinate system: canvas is SP_W x SP_H (200x220).
Characters are anchored to the bottom-centre at (100, 210).
Sprites face RIGHT by default; flip horizontally for player-2.
"""

import pygame, math
from settings import *

# ─── helpers ────────────────────────────────────────────────────────────────

def new_canvas():
    s = pygame.Surface((SP_W, SP_H), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s

def r(s, c, rect):                   # draw filled rect
    pygame.draw.rect(s, c, rect)

def line(s, c, p1, p2, w=3):
    pygame.draw.line(s, c, p1, p2, w)

def circle(s, c, pos, rad):
    pygame.draw.circle(s, c, pos, rad)

def scale_frame(surf, scale=1.0):
    if scale == 1.0:
        return surf
    w = int(SP_W * scale)
    h = int(SP_H * scale)
    return pygame.transform.scale(surf, (w, h))

# ─── shared parts ───────────────────────────────────────────────────────────

def draw_head(s, cx, top_y):
    """Kike's head: dark hair, skin face, green mask on lower half."""
    # Hair top
    r(s, K_HAIR,    (cx-22, top_y,    44, 20))
    r(s, K_HAIR,    (cx-25, top_y+10, 50, 12))
    # Side hair
    r(s, K_HAIR,    (cx-26, top_y+8,  10, 25))
    r(s, K_HAIR,    (cx+16, top_y+8,  10, 20))
    # Face skin
    r(s, K_SKIN,    (cx-18, top_y+16, 36, 22))
    r(s, K_SKIN_D,  (cx-18, top_y+34,  6, 8))
    # Green mask lower face
    r(s, K_MASK,    (cx-21, top_y+30, 42, 18))
    r(s, K_GREEN_D, (cx-21, top_y+30, 42,  3))  # top crease
    # Eyes (narrow, dark)
    r(s, K_HAIR,    (cx-14, top_y+20, 10,  5))
    r(s, K_HAIR,    (cx+4,  top_y+20, 10,  5))
    r(s, (255,255,200), (cx-12, top_y+21, 3, 3))  # left eye shine
    r(s, (255,255,200), (cx+6,  top_y+21, 3, 3))  # right eye shine
    # Neck
    r(s, K_SKIN,    (cx-8,  top_y+46, 16,  8))
    r(s, K_MASK,    (cx-10, top_y+44, 20,  6))

def draw_torso(s, cx, top_y, lean=0):
    """Torso with UA logo and belt. lean shifts the torso horizontally."""
    tx = cx - 28 + lean
    # Main body
    r(s, K_GREEN,    (tx,    top_y,    56, 62))
    # Shadow sides
    r(s, K_GREEN_D,  (tx,    top_y,     6, 62))
    r(s, K_GREEN_D,  (tx+50, top_y,     6, 62))
    # Centre crease
    r(s, K_GREEN_D,  (tx+25, top_y+8,   4, 46))
    # UA logo (two bars + crossbar)
    ly = top_y + 20
    r(s, K_UA, (cx-11+lean, ly,  5, 18))
    r(s, K_UA, (cx+6+lean,  ly,  5, 18))
    r(s, K_UA, (cx-11+lean, ly+7, 22,  5))
    # Collar / lapel
    r(s, K_GREEN_DD, (tx+20, top_y,    16,  8))
    # Belt
    r(s, K_BELT,     (tx-3,  top_y+56, 62, 11))
    r(s, (35,28,22), (cx-4+lean, top_y+56, 8, 11))  # buckle

def draw_gauntlet(s, cx, cy):
    """Dark forearm guard."""
    r(s, K_GAUNTLET, (cx-7, cy, 14, 18))
    r(s, (50,50,60),  (cx-7, cy,  2, 18))

def draw_boot(s, x, y, w=30, flip=False):
    """Boot with green toe accent."""
    r(s, K_BOOT,     (x,    y,    w,   22))
    r(s, K_BOOT_ACC, (x,    y+16, w,    6))
    if flip:
        r(s, K_BOOT_ACC, (x,    y,    5,  22))
    else:
        r(s, K_BOOT_ACC, (x+w-5, y,   5,  22))

def draw_katana(s, hx, hy, angle_deg, blade_len=75, facing_right=True):
    """
    Draw katana: handle at (hx,hy), blade goes in direction angle_deg.
    angle_deg=90 → straight up, 0 → right, 45 → upper-right diagonal.
    """
    rad = math.radians(angle_deg)
    # Tip of blade
    tx = int(hx + blade_len * math.cos(rad))
    ty = int(hy - blade_len * math.sin(rad))
    # Handle end (opposite)
    hend_x = int(hx - 20 * math.cos(rad))
    hend_y = int(hy + 20 * math.sin(rad))
    # Draw handle
    pygame.draw.line(s, K_HANDLE, (hend_x, hend_y), (hx, hy), 5)
    # Guard
    gx1 = int(hx - 9 * math.sin(rad))
    gy1 = int(hy - 9 * math.cos(rad))
    gx2 = int(hx + 9 * math.sin(rad))
    gy2 = int(hy + 9 * math.cos(rad))
    pygame.draw.line(s, K_GUARD, (gx1, gy1), (gx2, gy2), 5)
    # Blade
    pygame.draw.line(s, K_BLADE, (hx, hy), (tx, ty), 3)
    pygame.draw.line(s, K_SHINE, (hx+1, hy), (tx+1, ty), 1)

def draw_scabbard(s, hx, hy, angle_deg, length=65):
    """Draw scabbard (sheath), darker than blade."""
    rad = math.radians(angle_deg)
    tx = int(hx + length * math.cos(rad))
    ty = int(hy - length * math.sin(rad))
    pygame.draw.line(s, (45, 35, 25), (hx, hy), (tx, ty), 6)
    pygame.draw.line(s, (65, 55, 40), (hx, hy), (tx, ty), 2)
    # tip cap
    circle(s, K_GUARD, (tx, ty), 4)

# ─── KIKE frames ─────────────────────────────────────────────────────────────

def kike_idle(bob=0):
    """
    Idle – wide kung-fu stance, right arm raised with katana, left arm low
    with scabbard. bob=0/2 for subtle breathing animation.
    """
    s = new_canvas()
    cx = 100
    # Scabbard in left hand (behind body, angled forward-down)
    draw_scabbard(s, cx-20, 135+bob, 80, 65)
    # Left leg (wide, angled out)
    r(s, K_GREEN,   (cx-52, 125+bob, 30, 58))
    r(s, K_GREEN_D, (cx-52, 125+bob,  5, 58))
    draw_boot(s, cx-57, 178+bob, 34, flip=True)
    # Right leg
    r(s, K_GREEN,   (cx+22, 128+bob, 30, 55))
    r(s, K_GREEN_D, (cx+47, 128+bob,  5, 55))
    draw_boot(s, cx+20, 178+bob, 34)
    # Torso
    draw_torso(s, cx, 68+bob)
    # Left arm (down, holding scabbard/sword)
    r(s, K_GREEN,   (cx-50, 85+bob, 22, 50))
    r(s, K_GREEN_D, (cx-50, 85+bob,  4, 50))
    draw_gauntlet(s, cx-43, 128+bob)
    r(s, K_SKIN,    (cx-47, 142+bob, 18, 12))
    # Right arm (raised up-right)
    r(s, K_GREEN,   (cx+30, 60+bob, 22, 55))
    r(s, K_GREEN_D, (cx+48, 60+bob,  4, 55))
    draw_gauntlet(s, cx+35, 95+bob)
    r(s, K_SKIN,    (cx+32, 109+bob, 18, 12))
    # Right katana raised upper-right
    draw_katana(s, cx+40, 112+bob, 125, 78)
    # Head
    draw_head(s, cx, 18+bob)
    return s

def kike_idle2():
    return kike_idle(bob=2)

def kike_walk(step):
    """
    Walk pose. step=0: left foot forward; step=1: right foot forward.
    Guard position – swords held in front.
    """
    s = new_canvas()
    cx = 100
    if step == 0:
        # Left foot forward
        fl_x, fl_y = cx-50, 182
        rl_x, rl_y = cx+15, 188
        ll_top_y = 125
        rl_top_y = 130
    else:
        fl_x, fl_y = cx+15, 182
        rl_x, rl_y = cx-50, 188
        ll_top_y = 130
        rl_top_y = 125

    # Back leg
    r(s, K_GREEN,   (rl_x, rl_top_y, 28, 60))
    r(s, K_GREEN_D, (rl_x+24, rl_top_y, 4, 60))
    draw_boot(s, rl_x-2, rl_y-10, 32)
    # Front leg
    r(s, K_GREEN,   (fl_x, ll_top_y, 28, 60))
    r(s, K_GREEN_D, (fl_x, ll_top_y, 4, 60))
    draw_boot(s, fl_x-2, fl_y-10, 32)
    # Torso slight lean forward
    draw_torso(s, cx, 70, lean=3 if step==0 else -3)
    # Left arm – guard, sword angled forward-up
    r(s, K_GREEN,   (cx-45, 85, 22, 50))
    draw_gauntlet(s, cx-38, 128)
    r(s, K_SKIN,    (cx-42, 142, 18, 12))
    draw_scabbard(s, cx-30, 148, 70, 60)
    # Right arm – sword held mid
    r(s, K_GREEN,   (cx+28, 72, 22, 52))
    draw_gauntlet(s, cx+33, 110)
    r(s, K_SKIN,    (cx+30, 124, 18, 12))
    draw_katana(s, cx+38, 128, 120, 72)
    # Head
    draw_head(s, cx+2, 20)
    return s

def kike_jump():
    """
    Jump – crouching in air, sword raised overhead, wide knee-bend.
    From image: crouching squat, right arm up, left arm angled.
    """
    s = new_canvas()
    cx = 100
    # Legs bent (crouching in air)
    r(s, K_GREEN,   (cx-48, 130, 30, 45))  # left thigh
    r(s, K_GREEN,   (cx-52, 165, 35, 28))  # left shin (tucked)
    r(s, K_GREEN_D, (cx-52, 165,  5, 28))
    draw_boot(s, cx-54, 188, 34, flip=True)
    r(s, K_GREEN,   (cx+18, 130, 30, 45))  # right thigh
    r(s, K_GREEN,   (cx+20, 165, 35, 28))  # right shin (tucked)
    r(s, K_GREEN_D, (cx+46, 165,  4, 28))
    draw_boot(s, cx+18, 188, 34)
    # Torso
    draw_torso(s, cx, 68)
    # Left arm holding scabbard
    r(s, K_GREEN,   (cx-48, 82, 22, 48))
    draw_gauntlet(s, cx-41, 122)
    r(s, K_SKIN,    (cx-45, 136, 18, 12))
    draw_scabbard(s, cx-38, 145, 75, 60)
    # Right arm raised HIGH with katana
    r(s, K_GREEN,   (cx+30, 50, 22, 55))
    r(s, K_GREEN_D, (cx+48, 50, 4, 55))
    draw_gauntlet(s, cx+35, 88)
    r(s, K_SKIN,    (cx+32, 102, 18, 12))
    draw_katana(s, cx+40, 106, 135, 82)
    # Head
    draw_head(s, cx, 14)
    return s

def kike_light_atk(frame):
    """
    Light attack – quick single sword slash, 3 frames.
    frame 0: wind-up (sword back), 1: swing forward, 2: follow-through.
    """
    s = new_canvas()
    cx = 100
    # Legs same as idle
    r(s, K_GREEN,   (cx-52, 128, 30, 56))
    r(s, K_GREEN_D, (cx-52, 128,  5, 56))
    draw_boot(s, cx-57, 180, 34, flip=True)
    r(s, K_GREEN,   (cx+22, 130, 30, 54))
    r(s, K_GREEN_D, (cx+47, 130,  5, 54))
    draw_boot(s, cx+20, 180, 34)
    draw_torso(s, cx, 68)
    # Left arm holds scabbard low
    r(s, K_GREEN,   (cx-48, 86, 22, 50))
    draw_gauntlet(s, cx-41, 128)
    r(s, K_SKIN,    (cx-45, 142, 18, 12))
    draw_scabbard(s, cx-22, 150, 60, 60)

    if frame == 0:
        # Wind-up: sword pulled back overhead
        r(s, K_GREEN,   (cx+28, 55, 22, 58))
        draw_gauntlet(s, cx+33, 95)
        r(s, K_SKIN,    (cx+30, 109, 18, 12))
        draw_katana(s, cx+38, 113, 145, 80)
    elif frame == 1:
        # Strike: arm forward, sword nearly horizontal, slashing
        r(s, K_GREEN,   (cx+28, 70, 22, 58))
        draw_gauntlet(s, cx+50, 100)
        r(s, K_SKIN,    (cx+62, 98, 18, 12))
        draw_katana(s, cx+70, 104, 180, 80)
        # slash trail
        pygame.draw.arc(s, (200,230,255), (cx+40, 70, 80, 60), math.pi*0.1, math.pi*0.7, 3)
    else:
        # Follow-through: arm extended downward
        r(s, K_GREEN,   (cx+30, 80, 22, 56))
        draw_gauntlet(s, cx+50, 118)
        r(s, K_SKIN,    (cx+60, 128, 18, 12))
        draw_katana(s, cx+68, 134, 200, 75)

    draw_head(s, cx, 18)
    return s

def kike_heavy_atk(frame):
    """
    Heavy attack – horizontal sword sweep (cross slash), 5 frames.
    Matches the wide horizontal sweep poses from the reference.
    """
    s = new_canvas()
    cx = 100

    if frame < 3:
        # Wide sweep: lunge forward
        lean = [0, 8, 15][min(frame, 2)]
        r(s, K_GREEN,   (cx-55, 128, 32, 58))
        r(s, K_GREEN_D, (cx-55, 128,  5, 58))
        draw_boot(s, cx-60, 182, 36, flip=True)
        r(s, K_GREEN,   (cx+18+lean, 132, 32, 54))
        r(s, K_GREEN_D, (cx+46+lean, 132,  5, 54))
        draw_boot(s, cx+16+lean, 182, 36)
        draw_torso(s, cx, 70, lean=lean)
        # Left arm: sword LOW, sweeping
        lx = cx - 52 + lean
        r(s, K_GREEN,   (lx, 90, 22, 52))
        draw_gauntlet(s, lx+5, 132)
        r(s, K_SKIN,    (lx+2, 146, 18, 12))
        draw_scabbard(s, lx+10, 152, 5, 68)   # nearly horizontal, forward
        # Right arm: katana MID height extended right
        rx = cx + 30 + lean
        r(s, K_GREEN,   (rx, 78, 22, 56))
        draw_gauntlet(s, rx+25, 112)
        r(s, K_SKIN,    (rx+38, 108, 18, 12))
        angle = [100, 10, 355][min(frame, 2)]
        draw_katana(s, rx+48, 114, angle, 85)
    else:
        # Follow-through: arms crossed in front (cross-slash finish)
        lean = 12
        r(s, K_GREEN,   (cx-55, 128, 32, 58))
        draw_boot(s, cx-60, 182, 36, flip=True)
        r(s, K_GREEN,   (cx+18+lean, 132, 32, 54))
        draw_boot(s, cx+16+lean, 182, 36)
        draw_torso(s, cx, 70, lean=lean)
        # Both swords crossed
        r(s, K_GREEN,   (cx-45+lean, 82, 22, 55))
        draw_gauntlet(s, cx-38+lean, 128)
        r(s, K_SKIN,    (cx-42+lean, 142, 18, 12))
        draw_scabbard(s, cx-32+lean, 150, 50, 70)
        r(s, K_GREEN,   (cx+28+lean, 75, 22, 55))
        draw_gauntlet(s, cx+32+lean, 112)
        r(s, K_SKIN,    (cx+30+lean, 126, 18, 12))
        draw_katana(s, cx+38+lean, 130, 130, 78)

    draw_head(s, cx+lean//2, 18)
    return s

def kike_special(frame):
    """
    Special – furniture throw. 6 frames.
    0-1: reach back, 2: grab furniture, 3-4: throw, 5: follow-through (fist extended).
    Matches the fist-raised pose from reference.
    """
    s = new_canvas()
    cx = 100

    # Legs wide lunge position
    r(s, K_GREEN,   (cx-58, 130, 32, 58))
    r(s, K_GREEN_D, (cx-58, 130,  5, 58))
    draw_boot(s, cx-62, 184, 36, flip=True)
    r(s, K_GREEN,   (cx+20, 128, 32, 60))
    r(s, K_GREEN_D, (cx+48, 128,  5, 60))
    draw_boot(s, cx+18, 184, 36)

    if frame <= 1:
        # Wind-up: right fist pulled back
        draw_torso(s, cx, 68, lean=-5)
        r(s, K_GREEN,   (cx-48, 82, 22, 52))
        draw_gauntlet(s, cx-41, 126)
        r(s, K_SKIN,    (cx-45, 140, 18, 12))
        draw_scabbard(s, cx-20, 148, 70, 62)
        # Right arm pulled back (fist)
        r(s, K_GREEN,   (cx+26, 68, 22, 55))
        draw_gauntlet(s, cx+30, 105)
        r(s, K_SKIN,    (cx+28, 119, 18, 12))
        # Fist (clenched)
        r(s, K_SKIN,    (cx+26, 118, 22, 16))
        r(s, K_SKIN_D,  (cx+26, 118, 22,  4))
        # Hold sword in left
        draw_katana(s, cx-38, 142, 88, 68)
    elif frame == 2:
        # Grabbing: hands forward
        draw_torso(s, cx, 68, lean=5)
        r(s, K_GREEN,   (cx-38, 80, 22, 55))
        draw_gauntlet(s, cx-31, 125)
        r(s, K_SKIN,    (cx-35, 138, 18, 12))
        r(s, K_GREEN,   (cx+28, 72, 22, 58))
        draw_gauntlet(s, cx+48, 105)
        r(s, K_SKIN,    (cx+60, 104, 18, 12))
        # Show chair being grabbed (simple pixel chair)
        _draw_chair(s, cx+80, 105)
        draw_katana(s, cx-25, 140, 88, 68)
    elif frame <= 4:
        # Throwing: right arm fully extended forward
        ext = (frame - 2) * 18
        draw_torso(s, cx, 68, lean=10)
        r(s, K_GREEN,   (cx-40, 82, 22, 52))
        draw_gauntlet(s, cx-33, 126)
        r(s, K_SKIN,    (cx-37, 140, 18, 12))
        draw_scabbard(s, cx-22, 148, 68, 62)
        # Right arm lunging
        r(s, K_GREEN,   (cx+28, 72, 22+ext, 55))
        draw_gauntlet(s, cx+44+ext, 96)
        r(s, K_SKIN,    (cx+56+ext, 98, 18, 12))
        # Fist
        r(s, K_SKIN,    (cx+65+ext, 96, 22, 16))
        r(s, K_SKIN_D,  (cx+65+ext, 96, 22,  4))
    else:
        # Follow-through: fist raised up (matches image bottom-right pose)
        draw_torso(s, cx, 68, lean=8)
        r(s, K_GREEN,   (cx-44, 84, 22, 52))
        draw_gauntlet(s, cx-37, 128)
        r(s, K_SKIN,    (cx-41, 142, 18, 12))
        draw_scabbard(s, cx-20, 150, 68, 62)
        # Right arm raised triumphant fist
        r(s, K_GREEN,   (cx+28, 58, 22, 62))
        r(s, K_GREEN_D, (cx+46, 58,  4, 62))
        draw_gauntlet(s, cx+33, 92)
        r(s, K_SKIN,    (cx+30, 82, 22, 16))   # fist raised
        r(s, K_SKIN_D,  (cx+30, 82, 22,  4))

    draw_head(s, cx, 18)
    return s

def kike_block():
    """
    Block – both swords crossed in guard (centre block from reference).
    """
    s = new_canvas()
    cx = 100
    # Legs slightly bent / low stance
    r(s, K_GREEN,   (cx-50, 132, 30, 56))
    r(s, K_GREEN_D, (cx-50, 132,  5, 56))
    draw_boot(s, cx-55, 184, 34, flip=True)
    r(s, K_GREEN,   (cx+20, 132, 30, 56))
    r(s, K_GREEN_D, (cx+46, 132,  5, 56))
    draw_boot(s, cx+18, 184, 34)
    draw_torso(s, cx, 70)
    # Left arm up & inward
    r(s, K_GREEN,   (cx-42, 78, 22, 55))
    draw_gauntlet(s, cx-35, 120)
    r(s, K_SKIN,    (cx-38, 130, 18, 12))
    draw_scabbard(s, cx-18, 132, 55, 70)   # angled inward-up
    # Right arm up & inward (cross)
    r(s, K_GREEN,   (cx+20, 72, 22, 58))
    draw_gauntlet(s, cx+25, 116)
    r(s, K_SKIN,    (cx+22, 126, 18, 12))
    draw_katana(s, cx+30, 132, 130, 76)    # angled inward-up (cross)
    # Block glint
    circle(s, (220, 240, 255), (cx+2, 120), 6)
    draw_head(s, cx, 18)
    return s

def kike_hit(frame):
    """
    Hit / stumble pose – matches the off-balance pose in reference bottom-left.
    frame 0: impact, 1: stumble back, 2: recovering.
    """
    s = new_canvas()
    cx = 100

    if frame == 0:
        # Impact: torso recoils, arms flail
        lean = -12
        r(s, K_GREEN,   (cx-48, 130, 30, 58))
        draw_boot(s, cx-52, 184, 34, flip=True)
        r(s, K_GREEN,   (cx+24, 135, 30, 52))
        draw_boot(s, cx+22, 184, 34)
        draw_torso(s, cx, 72, lean=lean)
        r(s, K_GREEN,   (cx-55+lean, 88, 22, 50))
        draw_gauntlet(s, cx-48+lean, 130)
        r(s, K_SKIN,    (cx-52+lean, 144, 20, 12))
        r(s, K_GREEN,   (cx+28+lean, 78, 22, 52))
        draw_gauntlet(s, cx+32+lean, 118)
        r(s, K_SKIN,    (cx+30+lean, 130, 18, 12))
        draw_katana(s, cx+38+lean, 136, 165, 70)
        draw_head(s, cx+lean, 20)
    elif frame == 1:
        # Stumble: bent forward, off balance (from reference image)
        r(s, K_GREEN,   (cx-55, 132, 32, 56))
        r(s, K_GREEN_D, (cx-55, 132,  5, 56))
        draw_boot(s, cx-58, 184, 36, flip=True)
        r(s, K_GREEN,   (cx+10, 145, 32, 42))
        draw_boot(s, cx+8, 184, 36)
        draw_torso(s, cx, 80, lean=-18)
        # Arms dangling down
        r(s, K_GREEN,   (cx-62, 98, 22, 52))
        draw_gauntlet(s, cx-55, 142)
        r(s, K_SKIN,    (cx-58, 156, 20, 12))
        r(s, K_GREEN,   (cx+14, 95, 22, 50))
        draw_gauntlet(s, cx+18, 136)
        r(s, K_SKIN,    (cx+15, 148, 18, 12))
        draw_katana(s, cx+22, 152, 220, 65)
        draw_head(s, cx-18, 40)
    else:
        # Recovering: straightening up
        r(s, K_GREEN,   (cx-50, 128, 30, 58))
        draw_boot(s, cx-54, 182, 34, flip=True)
        r(s, K_GREEN,   (cx+20, 130, 30, 56))
        draw_boot(s, cx+18, 182, 34)
        draw_torso(s, cx, 70, lean=-6)
        r(s, K_GREEN,   (cx-46, 84, 22, 50))
        draw_gauntlet(s, cx-39, 126)
        r(s, K_SKIN,    (cx-43, 140, 18, 12))
        r(s, K_GREEN,   (cx+24, 74, 22, 52))
        draw_gauntlet(s, cx+28, 114)
        r(s, K_SKIN,    (cx+26, 126, 18, 12))
        draw_katana(s, cx+34, 130, 140, 74)
        draw_head(s, cx, 18)
    return s

def kike_dead(frame):
    """Dead – falls to ground, 4 frames."""
    s = new_canvas()
    cx = 100
    progress = frame / 3.0
    y_off = int(progress * 50)
    lean = int(progress * 55)
    # Collapse to ground
    ground_y = 185 + y_off
    r(s, K_GREEN,   (cx-50-lean, ground_y-60,  80, 60))
    r(s, K_GREEN_D, (cx-50-lean, ground_y-60,   5, 60))
    r(s, K_GREEN,   (cx+10-lean, ground_y-30, 100, 30))
    draw_boot(s, cx+60-lean, ground_y-30, 40)
    draw_boot(s, cx-55-lean, ground_y-28, 40, flip=True)
    draw_torso(s, cx-lean, ground_y-90, lean=-20-lean)
    # Arms splayed
    r(s, K_GREEN,   (cx-55-lean, ground_y-80, 22, 45))
    r(s, K_SKIN,    (cx-52-lean, ground_y-38, 18, 12))
    draw_katana(s, cx-45-lean, ground_y-34, 210, 65)
    r(s, K_GREEN,   (cx+20-lean, ground_y-85, 22, 40))
    r(s, K_SKIN,    (cx+22-lean, ground_y-48, 18, 12))
    draw_head(s, cx-lean, ground_y-118)
    return s

# ─── Furniture projectile ────────────────────────────────────────────────────

def _draw_chair(s, x, y):
    """Draw a small wooden chair at (x, y)."""
    # Seat
    r(s, (140, 90, 40),  (x-18, y,    36, 10))
    r(s, (100, 65, 30),  (x-18, y,    36,  3))
    # Legs
    r(s, (120, 75, 35),  (x-16, y+10, 5,  22))
    r(s, (120, 75, 35),  (x+11, y+10, 5,  22))
    r(s, (120, 75, 35),  (x-16, y+10, 5,  14))
    r(s, (120, 75, 35),  (x+11, y+10, 5,  14))
    # Back
    r(s, (140, 90, 40),  (x-18, y-22, 6,  24))
    r(s, (140, 90, 40),  (x+12, y-22, 6,  24))
    r(s, (140, 90, 40),  (x-18, y-22, 36,  6))
    # Rung
    r(s, (120, 75, 35),  (x-10, y+16, 20,  4))

def make_furniture_surf(furniture_type='chair'):
    """Return a Surface with the furniture piece drawn (for projectile)."""
    w, h = 80, 70
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    if furniture_type == 'chair':
        _draw_chair(s, 40, 28)
    elif furniture_type == 'table':
        r(s, (140, 90, 40),  (5,  15, 70, 12))
        r(s, (100, 65, 30),  (5,  15, 70,  3))
        r(s, (120, 75, 35),  (8,  27,  6, 28))
        r(s, (120, 75, 35),  (66, 27,  6, 28))
        r(s, (120, 75, 35),  (28, 27,  6, 28))
        r(s, (120, 75, 35),  (46, 27,  6, 28))
        r(s, (120, 75, 35),  (8,  38, 64,  4))
    elif furniture_type == 'barrel':
        circle(s, (160, 100, 45), (40, 40), 30)
        circle(s, (140,  85, 35), (40, 40), 28)
        r(s, (80,  50, 20),  (12, 20, 56,  5))
        r(s, (80,  50, 20),  (12, 35, 56,  5))
        r(s, (80,  50, 20),  (12, 50, 56,  5))
    else:  # vase
        circle(s, (180, 120, 40), (40, 45), 22)
        circle(s, (160, 100, 30), (40, 45), 20)
        r(s, (180, 120, 40),  (26, 24, 28, 10))
        r(s, (160, 100, 30),  (28, 26, 24,  8))
    return s

# ─── Blue Fighter frames ─────────────────────────────────────────────────────

def blue_idle(bob=0):
    s = new_canvas()
    cx = 100
    # Legs
    r(s, B_BLUE,   (cx-50, 128+bob, 28, 60))
    r(s, B_BLUE_D, (cx-50, 128+bob,  4, 60))
    r(s, K_BOOT,   (cx-54, 184+bob, 34, 20))
    r(s, B_BLUE,   (cx+22, 130+bob, 28, 58))
    r(s, B_BLUE_D, (cx+46, 130+bob,  4, 58))
    r(s, K_BOOT,   (cx+20, 184+bob, 34, 20))
    # Torso
    r(s, B_BLUE,   (cx-28, 70+bob, 56, 62))
    r(s, B_BLUE_D, (cx-28, 70+bob,  6, 62))
    r(s, B_BLUE_D, (cx+22, 70+bob,  6, 62))
    r(s, B_BELT,   (cx-30, 126+bob, 60, 10))
    # Arms
    r(s, B_BLUE,   (cx-48, 80+bob, 22, 50))
    r(s, B_SKIN,   (cx-46, 126+bob, 18, 14))
    r(s, B_BLUE,   (cx+26, 75+bob, 22, 52))
    r(s, B_SKIN,   (cx+28, 123+bob, 18, 14))
    # Head
    r(s, B_HAIR,   (cx-22, 20+bob, 44, 20))
    r(s, B_SKIN,   (cx-18, 30+bob, 36, 28))
    r(s, B_HAIR,   (cx-20, 20+bob, 10, 20))
    r(s, B_HAIR,   (cx+10, 20+bob, 10, 18))
    r(s, B_HAIR,   (cx-18, 50+bob, 10,  8))
    r(s, B_SKIN,   (cx-8,  56+bob, 16,  8))
    r(s, B_HAIR,   (cx-14, 32+bob,  8,  5))
    r(s, B_HAIR,   (cx+6,  32+bob,  8,  5))
    return s

def blue_idle2():
    return blue_idle(bob=2)

def blue_walk(step):
    s = new_canvas()
    cx = 100
    if step == 0:
        fl_y = 182; rl_y = 188
        fl_x = cx-48; rl_x = cx+18
    else:
        fl_y = 182; rl_y = 188
        fl_x = cx+18; rl_x = cx-48
    r(s, B_BLUE,   (rl_x, 130, 28, 58))
    r(s, K_BOOT,   (rl_x-2, rl_y-8, 32, 20))
    r(s, B_BLUE,   (fl_x, 128, 28, 58))
    r(s, K_BOOT,   (fl_x-2, fl_y-8, 32, 20))
    r(s, B_BLUE,   (cx-28, 70, 56, 62))
    r(s, B_BLUE_D, (cx-28, 70,  5, 62))
    r(s, B_BELT,   (cx-30, 126, 60, 10))
    r(s, B_BLUE,   (cx-46, 78, 22, 52))
    r(s, B_SKIN,   (cx-44, 126, 18, 14))
    r(s, B_BLUE,   (cx+24, 72, 22, 54))
    r(s, B_SKIN,   (cx+26, 122, 18, 14))
    r(s, B_HAIR,   (cx-22, 20, 44, 20))
    r(s, B_SKIN,   (cx-18, 30, 36, 28))
    r(s, B_SKIN,   (cx-8,  56, 16,  8))
    r(s, B_HAIR,   (cx-14, 32,  8,  5))
    r(s, B_HAIR,   (cx+6,  32,  8,  5))
    return s

def blue_attack(frame):
    s = new_canvas()
    cx = 100
    r(s, B_BLUE,   (cx-50, 130, 28, 58))
    r(s, K_BOOT,   (cx-54, 184, 34, 20))
    r(s, B_BLUE,   (cx+20, 128, 28, 58))
    r(s, K_BOOT,   (cx+18, 184, 34, 20))
    r(s, B_BLUE,   (cx-28, 68, 56, 62))
    r(s, B_BELT,   (cx-30, 124, 60, 10))
    r(s, B_BLUE,   (cx-46, 80, 22, 50))
    r(s, B_SKIN,   (cx-44, 126, 18, 14))
    ext = frame * 20
    r(s, B_BLUE,   (cx+24, 72, 22+ext, 50))
    r(s, B_SKIN,   (cx+40+ext, 74, 22, 14))
    r(s, B_HAIR,   (cx-22, 20, 44, 20))
    r(s, B_SKIN,   (cx-18, 30, 36, 28))
    r(s, B_SKIN,   (cx-8,  56, 16,  8))
    r(s, B_HAIR,   (cx-14, 32,  8,  5))
    r(s, B_HAIR,   (cx+6,  32,  8,  5))
    return s

def blue_hit(frame):
    s = new_canvas()
    cx = 100
    lean = -10 - frame * 8
    r(s, B_BLUE,   (cx-48, 132, 28, 56))
    r(s, K_BOOT,   (cx-52, 184, 34, 20))
    r(s, B_BLUE,   (cx+22, 134, 28, 54))
    r(s, K_BOOT,   (cx+20, 184, 34, 20))
    r(s, B_BLUE,   (cx-28+lean, 70, 56, 62))
    r(s, B_BELT,   (cx-30+lean, 126, 60, 10))
    r(s, B_BLUE,   (cx-46+lean, 82, 22, 50))
    r(s, B_SKIN,   (cx-44+lean, 128, 18, 14))
    r(s, B_BLUE,   (cx+24+lean, 76, 22, 52))
    r(s, B_SKIN,   (cx+26+lean, 124, 18, 14))
    r(s, B_HAIR,   (cx-22+lean, 22, 44, 20))
    r(s, B_SKIN,   (cx-18+lean, 32, 36, 28))
    r(s, B_SKIN,   (cx-8+lean,  56, 16,  8))
    r(s, B_HAIR,   (cx-14+lean, 34,  8,  5))
    r(s, B_HAIR,   (cx+6+lean,  34,  8,  5))
    return s

def blue_dead(frame):
    s = new_canvas()
    cx = 100
    prog = frame / 3.0
    lean = int(prog * 60)
    gy = int(185 + prog * 15)
    r(s, B_BLUE,   (cx-52-lean, gy-60, 90, 60))
    r(s, B_BLUE,   (cx+10-lean, gy-30, 90, 30))
    r(s, K_BOOT,   (cx+60-lean, gy-28, 40, 20))
    r(s, K_BOOT,   (cx-56-lean, gy-26, 40, 20))
    r(s, B_HAIR,   (cx-22-lean, gy-108, 44, 20))
    r(s, B_SKIN,   (cx-18-lean, gy-98, 36, 28))
    return s

# ─── Build animation dictionaries ────────────────────────────────────────────

def build_kike_animations():
    """Returns dict: anim_name → list of pygame.Surface frames."""
    return {
        'idle':         [kike_idle(0), kike_idle(2), kike_idle(0), kike_idle2()],
        'walk':         [kike_walk(0), kike_walk(1), kike_walk(0), kike_walk(1),
                         kike_walk(0), kike_walk(1)],
        'jump':         [kike_jump(), kike_jump(), kike_jump()],
        'light_attack': [kike_light_atk(0), kike_light_atk(1), kike_light_atk(2),
                         kike_light_atk(2)],
        'heavy_attack': [kike_heavy_atk(0), kike_heavy_atk(1), kike_heavy_atk(2),
                         kike_heavy_atk(3), kike_heavy_atk(4)],
        'special':      [kike_special(0), kike_special(1), kike_special(2),
                         kike_special(3), kike_special(4), kike_special(5)],
        'block':        [kike_block(), kike_block()],
        'hit':          [kike_hit(0), kike_hit(1), kike_hit(2)],
        'dead':         [kike_dead(0), kike_dead(1), kike_dead(2), kike_dead(3)],
    }

def build_blue_animations():
    return {
        'idle':         [blue_idle(0), blue_idle(2), blue_idle(0), blue_idle2()],
        'walk':         [blue_walk(0), blue_walk(1), blue_walk(0), blue_walk(1),
                         blue_walk(0), blue_walk(1)],
        'jump':         [blue_idle(0), blue_idle(0), blue_idle(0)],
        'light_attack': [blue_attack(0), blue_attack(1), blue_attack(2), blue_attack(2)],
        'heavy_attack': [blue_attack(0), blue_attack(1), blue_attack(2),
                         blue_attack(3), blue_attack(3)],
        'special':      [blue_attack(0), blue_attack(1), blue_attack(2),
                         blue_attack(2), blue_attack(1), blue_attack(0)],
        'block':        [blue_idle(0), blue_idle(0)],
        'hit':          [blue_hit(0), blue_hit(1), blue_hit(2)],
        'dead':         [blue_dead(0), blue_dead(1), blue_dead(2), blue_dead(3)],
    }
