"""
KikeFight – 2D fighting game
Run: python main.py
"""

import pygame, sys, math, random
from settings import *
from sprites  import build_kike_animations, build_blue_animations, make_furniture_surf
from fighter  import Fighter, FurnitureProjectile, IDLE, WALK, JUMP, LIGHT_ATTACK, \
                     HEAVY_ATTACK, SPECIAL, BLOCK, HIT, DEAD

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption('KikeFight')
clock  = pygame.time.Clock()

# ─── Fonts ────────────────────────────────────────────────────────────────────
try:
    font_lg = pygame.font.Font(None, 80)
    font_md = pygame.font.Font(None, 48)
    font_sm = pygame.font.Font(None, 32)
    font_xs = pygame.font.Font(None, 24)
except:
    font_lg = font_md = font_sm = font_xs = pygame.font.SysFont('Arial', 28)

# ─── Background: Cherry-blossom Dojo ─────────────────────────────────────────

def build_background():
    """Draw the dojo background once into a Surface."""
    bg = pygame.Surface((SCREEN_W, SCREEN_H))

    # Sky / window glow
    bg.fill((210, 185, 155))

    # Large windows / shoji screens (back wall)
    for i in range(4):
        wx = 60 + i * 290
        pygame.draw.rect(bg, (235, 220, 190), (wx, 60, 240, 350))
        pygame.draw.rect(bg, (160, 120, 70),  (wx, 60, 240, 350), 4)
        # grid lines
        for row in range(5):
            pygame.draw.line(bg, (160, 120, 70),
                             (wx, 60 + row*70), (wx+240, 60 + row*70), 2)
        for col in range(4):
            pygame.draw.line(bg, (160, 120, 70),
                             (wx + col*60, 60), (wx + col*60, 410), 2)

    # Kanji scroll on right
    scroll_x, scroll_y = 1060, 80
    pygame.draw.rect(bg, (230, 215, 180), (scroll_x, scroll_y, 100, 340))
    pygame.draw.rect(bg, (140, 100, 55),  (scroll_x, scroll_y, 100, 340), 3)
    pygame.draw.rect(bg, (140, 100, 55),  (scroll_x+10, scroll_y+10, 80, 320), 2)

    # Ceiling beams
    for bx in range(0, SCREEN_W, 160):
        pygame.draw.rect(bg, (120, 80, 40), (bx, 0, 30, 60))
    pygame.draw.rect(bg, (100, 65, 30), (0, 50, SCREEN_W, 18))

    # Cherry blossom tree (left side)
    _draw_cherry_tree(bg, 80, 480)

    # Wooden floor
    pygame.draw.rect(bg, (160, 100, 50), (0, FLOOR_Y, SCREEN_W, SCREEN_H - FLOOR_Y))
    for plank in range(0, SCREEN_W, 90):
        pygame.draw.line(bg, (140, 85, 40), (plank, FLOOR_Y), (plank, SCREEN_H), 2)
    for row in range(0, SCREEN_H - FLOOR_Y, 40):
        pygame.draw.line(bg, (140, 85, 40),
                         (0, FLOOR_Y + row), (SCREEN_W, FLOOR_Y + row), 1)
    # Floor highlight
    pygame.draw.rect(bg, (185, 120, 60), (0, FLOOR_Y, SCREEN_W, 6))

    # Shadow on floor
    shadow = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 60))
    bg.blit(shadow, (0, FLOOR_Y - 20))

    # Floating petals (static)
    random.seed(42)
    for _ in range(35):
        px = random.randint(0, SCREEN_W)
        py = random.randint(80, FLOOR_Y - 20)
        ps = random.randint(3, 7)
        alpha = random.randint(140, 220)
        petal = pygame.Surface((ps*2, ps), pygame.SRCALPHA)
        pygame.draw.ellipse(petal, (255, 180, 200, alpha), (0, 0, ps*2, ps))
        bg.blit(petal, (px, py))

    return bg


def _draw_cherry_tree(surf, cx, base_y):
    # Trunk
    pygame.draw.rect(surf, (90, 55, 30),  (cx-12, base_y-250, 24, 250))
    pygame.draw.rect(surf, (110, 70, 40), (cx-12, base_y-250, 8, 250))
    # Branches
    branches = [
        ((cx, base_y-220), (cx-80, base_y-310)),
        ((cx, base_y-200), (cx+60,  base_y-290)),
        ((cx, base_y-170), (cx-50,  base_y-240)),
    ]
    for p1, p2 in branches:
        pygame.draw.line(surf, (90, 55, 30), p1, p2, 8)
    # Blossom clusters
    blossoms = [
        (cx-80, base_y-340, 70),
        (cx+50, base_y-320, 65),
        (cx-20, base_y-370, 80),
        (cx-50, base_y-280, 55),
        (cx+20, base_y-300, 58),
        (cx,    base_y-420, 75),
    ]
    for bx, by, brad in blossoms:
        pygame.draw.circle(surf, (250, 160, 185), (bx, by), brad)
        pygame.draw.circle(surf, (255, 185, 205), (bx-10, by-10), brad//2)
        # inner flowers
        for _ in range(6):
            fx = bx + random.randint(-brad+10, brad-10)
            fy = by + random.randint(-brad+10, brad-10)
            pygame.draw.circle(surf, (255, 200, 215), (fx, fy), 8)
            pygame.draw.circle(surf, (255, 230, 235), (fx, fy), 4)

# ─── HUD Drawing ─────────────────────────────────────────────────────────────

def draw_hud(surface, p1, p2, round_time_ms):
    bar_w = 460
    bar_h = 26
    bar_y = 18

    # ── P1 health bar (left, grows right) ──
    pygame.draw.rect(surface, UI_FRAME,   (30, bar_y - 4, bar_w + 8, bar_h + 8), 0, 4)
    pygame.draw.rect(surface, UI_HP_BG,   (34, bar_y,     bar_w, bar_h), 0, 2)
    p1_w = int(bar_w * (p1.health / MAX_HEALTH))
    _draw_bar_gradient(surface, 34, bar_y, p1_w, bar_h, UI_HP_GREEN, UI_HP_GOLD)

    # ── P2 health bar (right, grows left) ──
    p2_bar_x = SCREEN_W - 30 - bar_w
    pygame.draw.rect(surface, UI_FRAME,   (p2_bar_x - 4, bar_y - 4, bar_w + 8, bar_h + 8), 0, 4)
    pygame.draw.rect(surface, UI_HP_BG,   (p2_bar_x, bar_y, bar_w, bar_h), 0, 2)
    p2_w = int(bar_w * (p2.health / MAX_HEALTH))
    _draw_bar_gradient(surface, p2_bar_x + bar_w - p2_w, bar_y, p2_w, bar_h,
                       UI_HP_RED, (240, 100, 30))

    # Names
    p1_name = _shadow_text(font_sm, 'KIKE  •  UA NINJA', UI_TEXT)
    p2_name = _shadow_text(font_sm, 'BLUE  FIGHTER', UI_TEXT)
    surface.blit(p1_name, (34, bar_y + bar_h + 6))
    nr = p2_name.get_rect(right=SCREEN_W - 30)
    nr.y = bar_y + bar_h + 6
    surface.blit(p2_name, nr)

    # Timer (centre)
    secs = max(0, round_time_ms // 1000)
    timer_col = (255, 80, 40) if secs <= 10 else UI_TEXT
    t_surf = _shadow_text(font_lg, f'{secs:02d}', timer_col)
    tr = t_surf.get_rect(centerx=SCREEN_W // 2, top=8)
    surface.blit(t_surf, tr)

    # Combo (P1)
    if p1.combo_count >= 2:
        c_surf  = _shadow_text(font_md, f'{p1.combo_count}', UI_COMBO)
        cl_surf = _shadow_text(font_xs, 'COMBO!', UI_COMBO)
        surface.blit(c_surf,  (34, bar_y + bar_h + 38))
        surface.blit(cl_surf, (34 + c_surf.get_width() + 6,
                               bar_y + bar_h + 38 + c_surf.get_height() - cl_surf.get_height()))

    # Combo (P2)
    if p2.combo_count >= 2:
        c_surf  = _shadow_text(font_md, f'{p2.combo_count}', UI_COMBO)
        cl_surf = _shadow_text(font_xs, 'COMBO!', UI_COMBO)
        cr = c_surf.get_rect(right=SCREEN_W - 30)
        cr.y = bar_y + bar_h + 38
        surface.blit(c_surf,  cr)
        surface.blit(cl_surf, (cr.x - cl_surf.get_width() - 6,
                               cr.y + c_surf.get_height() - cl_surf.get_height()))


def _draw_bar_gradient(surf, x, y, w, h, col_a, col_b):
    if w <= 0:
        return
    for i in range(w):
        t = i / max(w - 1, 1)
        c = tuple(int(col_a[j] + (col_b[j] - col_a[j]) * t) for j in range(3))
        pygame.draw.line(surf, c, (x + i, y), (x + i, y + h))


def _shadow_text(font, text, color, shadow=(0, 0, 0)):
    s = font.render(text, True, shadow)
    m = font.render(text, True, color)
    surf = pygame.Surface((m.get_width() + 2, m.get_height() + 2), pygame.SRCALPHA)
    surf.blit(s, (2, 2))
    surf.blit(m, (0, 0))
    return surf


# ─── Hit effect sparks ────────────────────────────────────────────────────────

class HitEffect:
    def __init__(self, x, y, heavy=False):
        self.x = x; self.y = y
        self.heavy   = heavy
        self.timer   = 0
        self.life    = 350 if heavy else 220
        self.sparks  = [(random.uniform(0, 360), random.uniform(3, 9 if heavy else 6))
                        for _ in range(16 if heavy else 10)]

    def update(self, dt):
        self.timer += dt

    @property
    def dead(self):
        return self.timer >= self.life

    def draw(self, surf):
        prog   = self.timer / self.life
        alpha  = int(255 * (1 - prog))
        spread = prog * (80 if self.heavy else 50)
        col    = (255, 240, 80) if not self.heavy else (255, 140, 30)
        # Ring flash
        ring_r = int(spread * 0.6)
        if ring_r > 2:
            ring_surf = pygame.Surface((ring_r*2+4, ring_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*col, alpha // 2),
                               (ring_r+2, ring_r+2), ring_r, 3)
            surf.blit(ring_surf, (int(self.x) - ring_r - 2, int(self.y) - ring_r - 2))
        # Sparks
        for angle, speed in self.sparks:
            rad  = math.radians(angle)
            ex   = int(self.x + math.cos(rad) * speed * spread * 0.3)
            ey   = int(self.y + math.sin(rad) * speed * spread * 0.3)
            size = max(1, int(4 * (1 - prog)))
            sp_s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(sp_s, (*col, alpha), (size, size), size)
            surf.blit(sp_s, (ex - size, ey - size))


# ─── Round overlay text ───────────────────────────────────────────────────────

def draw_centre_text(surf, text, sub='', color=UI_TEXT):
    s = _shadow_text(font_lg, text, color)
    sr = s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40))
    surf.blit(s, sr)
    if sub:
        ss = _shadow_text(font_md, sub, (220, 200, 160))
        ssr = ss.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 40))
        surf.blit(ss, ssr)


def draw_menu(surf):
    surf.fill((20, 10, 5))
    title = _shadow_text(font_lg, 'KIKEFIGHT', (255, 200, 30))
    sub   = _shadow_text(font_md, 'Press ENTER to Start  |  ESC to Quit', UI_TEXT)
    p1    = _shadow_text(font_sm, 'P1: WASD + U/I/O/P/K', (180, 255, 120))
    p2    = _shadow_text(font_sm, 'P2: ARROWS + NUM1/2/3/0/NUM5', (120, 180, 255))
    legend= _shadow_text(font_xs,
                         'U=Light  I=Heavy  O/NUM2=Special(FURNITURE THROW)  P/NUM0=Block',
                         (200, 200, 200))
    surf.blit(title,  title.get_rect(center=(SCREEN_W//2, 200)))
    surf.blit(sub,    sub.get_rect(center=(SCREEN_W//2, 310)))
    surf.blit(p1,     p1.get_rect(center=(SCREEN_W//2, 420)))
    surf.blit(p2,     p2.get_rect(center=(SCREEN_W//2, 470)))
    surf.blit(legend, legend.get_rect(center=(SCREEN_W//2, 530)))


# ─── Input mapping ────────────────────────────────────────────────────────────

def read_p1(keys, p1_flip):
    return {
        'left':    keys[pygame.K_a],
        'right':   keys[pygame.K_d],
        'up':      keys[pygame.K_w],
        'light':   keys[pygame.K_u],
        'heavy':   keys[pygame.K_i],
        'special': keys[pygame.K_o],
        'block':   keys[pygame.K_p],
    }

def read_p2(keys, p2_flip):
    return {
        'left':    keys[pygame.K_LEFT],
        'right':   keys[pygame.K_RIGHT],
        'up':      keys[pygame.K_UP],
        'light':   keys[pygame.K_KP1],
        'heavy':   keys[pygame.K_KP3],
        'special': keys[pygame.K_KP2],
        'block':   keys[pygame.K_KP0],
    }


# ─── Main game loop ───────────────────────────────────────────────────────────

def new_fighters():
    kike_anim = build_kike_animations()
    blue_anim = build_blue_animations()

    p1 = Fighter(1, 300, FLOOR_Y, kike_anim, name='KIKE',  flip=False)
    p2 = Fighter(2, 980, FLOOR_Y, blue_anim, name='BLUE',  flip=True)
    return p1, p2


def run_game():
    random.seed()
    bg     = build_background()
    furn_surfs = {ft: make_furniture_surf(ft) for ft in FURNITURE}

    # Game state
    STATE_MENU    = 'menu'
    STATE_FIGHT   = 'fight'
    STATE_ROUND_END = 'round_end'
    STATE_GAME_OVER = 'gameover'

    game_state = STATE_MENU
    p1 = p2 = None

    round_timer   = ROUND_TIME * 1000   # ms
    projectiles   = []
    effects       = []
    shake_frame   = 0
    shake_offset  = (0, 0)

    round_end_timer = 0
    winner_text     = ''
    p1_wins = p2_wins = 0

    while True:
        dt = clock.tick(FPS)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if game_state == STATE_MENU and event.key == pygame.K_RETURN:
                    p1, p2       = new_fighters()
                    round_timer  = ROUND_TIME * 1000
                    projectiles  = []
                    effects      = []
                    shake_frame  = 0
                    game_state   = STATE_FIGHT
                if game_state in (STATE_ROUND_END, STATE_GAME_OVER):
                    if event.key == pygame.K_RETURN:
                        if game_state == STATE_GAME_OVER:
                            p1_wins = p2_wins = 0
                            game_state = STATE_MENU
                        else:
                            p1, p2      = new_fighters()
                            round_timer = ROUND_TIME * 1000
                            projectiles = []
                            effects     = []
                            game_state  = STATE_FIGHT

        # ── MENU ──
        if game_state == STATE_MENU:
            draw_menu(screen)
            pygame.display.flip()
            continue

        # ── FIGHT update ──
        if game_state == STATE_FIGHT:
            keys  = pygame.key.get_pressed()

            # Auto-flip fighters to always face each other
            p1.flip = p1.x > p2.x
            p2.flip = p2.x < p1.x

            p1.inp = read_p1(keys, p1.flip)
            p2.inp = read_p2(keys, p2.flip)

            p1.update(dt, SCREEN_W)
            p2.update(dt, SCREEN_W)

            # Attack collision p1→p2
            if p1.attack_rect and not p1.did_hit:
                if p1.attack_rect.colliderect(p2.rect):
                    dmg = {'light_attack': DMG_LIGHT,
                           'heavy_attack': DMG_HEAVY,
                           'special': DMG_SPECIAL}.get(p1.state, DMG_LIGHT)
                    p2.take_hit(dmg, p1.state)
                    p1.did_hit = True
                    p1.register_combo_hit()
                    cx = (p1.attack_rect.centerx + p2.rect.centerx) // 2
                    cy = (p1.attack_rect.centery + p2.rect.centery) // 2
                    effects.append(HitEffect(cx, cy, heavy=(p1.state != LIGHT_ATTACK)))
                    shake_frame = 8 if p1.state == HEAVY_ATTACK else 4

            # Attack collision p2→p1
            if p2.attack_rect and not p2.did_hit:
                if p2.attack_rect.colliderect(p1.rect):
                    dmg = {'light_attack': DMG_LIGHT,
                           'heavy_attack': DMG_HEAVY,
                           'special': DMG_SPECIAL}.get(p2.state, DMG_LIGHT)
                    p1.take_hit(dmg, p2.state)
                    p2.did_hit = True
                    p2.register_combo_hit()
                    cx = (p2.attack_rect.centerx + p1.rect.centerx) // 2
                    cy = (p2.attack_rect.centery + p1.rect.centery) // 2
                    effects.append(HitEffect(cx, cy, heavy=(p2.state != LIGHT_ATTACK)))
                    shake_frame = 8 if p2.state == HEAVY_ATTACK else 4

            # Furniture spawn
            for fighter in (p1, p2):
                if fighter.spawn_projectile:
                    fighter.spawn_projectile = False
                    ft   = random.choice(FURNITURE)
                    dirn = -1 if fighter.flip else 1
                    proj = FurnitureProjectile(
                        fighter.x + dirn * 60, fighter.y - 120,
                        dirn, furn_surfs[ft]
                    )
                    projectiles.append(proj)

            # Update projectiles
            for proj in projectiles[:]:
                proj.update(dt)
                if not proj.active:
                    projectiles.remove(proj)
                    continue
                # Check hit
                if not proj.hit_target:
                    for target in (p1, p2):
                        if proj.rect.colliderect(target.rect):
                            target.take_hit(DMG_SPECIAL, SPECIAL)
                            proj.hit_target = True
                            proj.active     = False
                            effects.append(HitEffect(proj.rect.centerx, proj.rect.centery, True))
                            shake_frame = 6
                            # find attacker for combo
                            attacker = p2 if target is p1 else p1
                            attacker.register_combo_hit()
                            break

            # Hit effects
            for e in effects[:]:
                e.update(dt)
                if e.dead:
                    effects.remove(e)

            # Screen shake
            if shake_frame > 0:
                shake_frame -= 1
                shake_offset = (random.randint(-4, 4), random.randint(-3, 3))
            else:
                shake_offset = (0, 0)

            # Timer countdown
            round_timer -= dt
            if round_timer <= 0:
                round_timer = 0
                # Time over – higher health wins
                if p1.health > p2.health:
                    winner_text = 'KIKE WINS!'
                    p1_wins += 1
                elif p2.health > p1.health:
                    winner_text = 'BLUE WINS!'
                    p2_wins += 1
                else:
                    winner_text = 'DRAW!'
                round_end_timer = 2500
                game_state = STATE_ROUND_END

            # KO check
            for dead_fighter, other, name in [(p1, p2, 'BLUE WINS!'), (p2, p1, 'KIKE WINS!')]:
                if not dead_fighter.alive and game_state == STATE_FIGHT:
                    winner_text = name
                    if name == 'KIKE WINS!':
                        p1_wins += 1
                    else:
                        p2_wins += 1
                    round_end_timer = 3000
                    game_state = STATE_ROUND_END

        # ── ROUND END countdown ──
        if game_state == STATE_ROUND_END:
            round_end_timer -= dt
            if round_end_timer <= 0:
                if p1_wins >= 2 or p2_wins >= 2:
                    game_state = STATE_GAME_OVER
                else:
                    p1, p2 = new_fighters()
                    round_timer = ROUND_TIME * 1000
                    projectiles = []
                    effects     = []
                    game_state  = STATE_FIGHT

        # ─── RENDER ──────────────────────────────────────────────────────────

        ox, oy = shake_offset

        # Background
        screen.blit(bg, (ox, oy))

        if p1 and p2:
            # Fighter shadows (ellipses on floor)
            for f in (p1, p2):
                sw = int(60 * (1 - max(0, (FLOOR_Y - f.y) / 200)))
                if sw > 10:
                    sh_surf = pygame.Surface((sw*2, 20), pygame.SRCALPHA)
                    pygame.draw.ellipse(sh_surf, (0, 0, 0, 80), (0, 0, sw*2, 20))
                    screen.blit(sh_surf, (int(f.x) - sw + ox, FLOOR_Y - 8 + oy))

            # Projectiles
            for proj in projectiles:
                proj.draw(screen)

            # Fighters
            p1.draw(screen)
            p2.draw(screen)

            # Hit effects
            for e in effects:
                e.draw(screen)

            # HUD
            draw_hud(screen, p1, p2, round_timer)

            # Scores (win dots)
            for i in range(2):
                col1 = UI_HP_GREEN if i < p1_wins else (60, 60, 60)
                col2 = UI_HP_RED   if i < p2_wins else (60, 60, 60)
                pygame.draw.circle(screen, col1, (34 + i * 22, 90), 8)
                pygame.draw.circle(screen, col2, (SCREEN_W - 34 - i * 22, 90), 8)

        if game_state == STATE_ROUND_END:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            ko_col = (255, 80, 40) if not p1.alive or not p2.alive else UI_TEXT
            draw_centre_text(screen, winner_text,
                             'KO!' if (not p1.alive or not p2.alive) else 'TIME!',
                             color=ko_col)

        if game_state == STATE_GAME_OVER:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            final = 'KIKE IS CHAMPION!' if p1_wins >= 2 else 'BLUE IS CHAMPION!'
            draw_centre_text(screen, final, 'Press ENTER to Restart')

        pygame.display.flip()


if __name__ == '__main__':
    run_game()
