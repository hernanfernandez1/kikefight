"""
fighter.py – Fighter class: physics, input, animation state machine,
             attack hitbox detection, combo counter.
"""

import pygame
from settings import *

# Animation state indices (also dict keys into animation_list)
IDLE         = 'idle'
WALK         = 'walk'
JUMP         = 'jump'
LIGHT_ATTACK = 'light_attack'
HEAVY_ATTACK = 'heavy_attack'
SPECIAL      = 'special'
BLOCK        = 'block'
HIT          = 'hit'
DEAD         = 'dead'

# Map to "priority" – higher means harder to interrupt
STATE_PRIO = {
    IDLE: 0, WALK: 0, JUMP: 1,
    LIGHT_ATTACK: 3, HEAVY_ATTACK: 4, SPECIAL: 5,
    BLOCK: 2, HIT: 6, DEAD: 99,
}

# How many frames each attack "holds" the active hitbox
ATTACK_ACTIVE_FRAMES = {
    LIGHT_ATTACK: (1, 2),   # frames 1-2
    HEAVY_ATTACK: (1, 3),
    SPECIAL:      (3, 4),   # frame 3-4 is the throw
}


class Fighter:
    def __init__(self, player_num, x, y, anim_dict, name='Fighter', flip=False):
        self.player = player_num
        self.name   = name
        self.flip   = flip          # True = faces left (P2)

        # Position – we track the feet centre
        self.x = float(x)
        self.y = float(y)
        self.vel_y = 0.0

        self.health = MAX_HEALTH
        self.alive  = True

        # State machine
        self.state       = IDLE
        self.frame_index = 0
        self.frame_timer = 0        # ms since last frame change
        self.state_done  = False    # True when the current state has played out

        # Combo
        self.combo_count = 0
        self.combo_timer = 0        # ms since last hit registered

        # Input flags set each frame by the controller
        self.inp = {k: False for k in
                    ('left','right','up','light','heavy','special','block')}

        # On-ground flag
        self.on_ground = True

        # Stun timer (ms to remain in HIT state)
        self.stun_timer = 0

        # Animation data
        self.anim = anim_dict       # {state_name: [Surface, ...]}

        # Hitbox (for both receiving and dealing damage)
        self.rect = pygame.Rect(int(self.x) - 40, int(self.y) - 180, 80, 180)

        # Attack-hitbox (forward extended box, active during attack frames)
        self.attack_rect = None
        self.did_hit     = False    # prevent multi-hit per swing

        # Special / furniture projectile
        self.spawn_projectile = False   # set to True by game to create projectile

        # Screen shake request
        self.shake_request = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Update
    # ──────────────────────────────────────────────────────────────────────────

    def update(self, dt, screen_w):
        if not self.alive:
            self._advance_anim(dt, DEAD, loop=False)
            return

        self.combo_timer += dt
        if self.combo_timer > COMBO_WINDOW:
            self.combo_count = 0

        # Stun
        if self.stun_timer > 0:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stun_timer = 0
                self._set_state(IDLE)

        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
        self.y += self.vel_y

        # Ground clamp
        if self.y >= FLOOR_Y:
            self.y       = FLOOR_Y
            self.vel_y   = 0
            self.on_ground = True

        # Screen bounds (left/right walls)
        self.x = max(80, min(screen_w - 80, self.x))

        # Update hitbox
        self.rect.topleft = (int(self.x) - 40, int(self.y) - 180)

        # State machine
        if self.state in (HIT, DEAD):
            self._advance_anim(dt, self.state, loop=False)
            return

        # Choose next state from input
        self._handle_input(dt)
        self._advance_anim(dt, self.state)
        self._update_attack_rect()

    def _handle_input(self, dt):
        inp = self.inp
        cur = self.state

        # Can't interrupt active attacks except by HIT
        if cur in (LIGHT_ATTACK, HEAVY_ATTACK, SPECIAL):
            if not self.state_done:
                return
            # After attack finishes, go idle
            self._set_state(IDLE)
            return

        if inp['block']:
            self._set_state(BLOCK)
            return

        if inp['special'] and self.on_ground:
            self._set_state(SPECIAL)
            self.did_hit = False
            self.spawn_projectile = False
            return

        if inp['heavy'] and self.on_ground:
            self._set_state(HEAVY_ATTACK)
            self.did_hit = False
            return

        if inp['light']:
            self._set_state(LIGHT_ATTACK)
            self.did_hit = False
            return

        if inp['up'] and self.on_ground:
            self.vel_y    = JUMP_VEL
            self.on_ground = False
            self._set_state(JUMP)
            return

        if not self.on_ground:
            self._set_state(JUMP)
            return

        dx = 0
        if inp['left']:  dx = -SPEED
        if inp['right']: dx =  SPEED
        if dx != 0:
            self.x += dx
            self._set_state(WALK)
        else:
            self._set_state(IDLE)

    def _set_state(self, new_state):
        if new_state == self.state:
            return
        if STATE_PRIO.get(new_state, 0) < STATE_PRIO.get(self.state, 0):
            return
        self.state       = new_state
        self.frame_index = 0
        self.frame_timer = 0
        self.state_done  = False
        self.attack_rect = None
        self.did_hit     = False

    def _advance_anim(self, dt, state_key, loop=True):
        frames = self.anim.get(state_key, self.anim[IDLE])
        ms_per_frame = ANIM_MS.get(state_key, 120)
        self.frame_timer += dt
        if self.frame_timer >= ms_per_frame:
            self.frame_timer -= ms_per_frame
            self.frame_index += 1
            if self.frame_index >= len(frames):
                if loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(frames) - 1
                    self.state_done  = True
                    if state_key == DEAD:
                        self.alive = False

    def _update_attack_rect(self):
        """Set attack_rect during active attack frames; None otherwise."""
        self.attack_rect = None
        if self.state not in ATTACK_ACTIVE_FRAMES:
            return
        lo, hi = ATTACK_ACTIVE_FRAMES[self.state]
        if lo <= self.frame_index <= hi:
            direction = -1 if self.flip else 1
            if self.state == LIGHT_ATTACK:
                w, h = 110, 80
            elif self.state == HEAVY_ATTACK:
                w, h = 140, 100
            else:  # SPECIAL
                w, h = 160, 120
            ax = self.rect.centerx + direction * 20
            ay = self.rect.top + 30
            if direction == 1:
                self.attack_rect = pygame.Rect(ax, ay, w, h)
            else:
                self.attack_rect = pygame.Rect(ax - w, ay, w, h)

            # Trigger furniture projectile on SPECIAL frame 3
            if self.state == SPECIAL and self.frame_index == 3:
                self.spawn_projectile = True

    # ──────────────────────────────────────────────────────────────────────────
    # Receive damage
    # ──────────────────────────────────────────────────────────────────────────

    def take_hit(self, damage, attacker_state):
        if not self.alive:
            return
        if self.state == DEAD:
            return

        # Blocking reduces damage
        if self.state == BLOCK:
            damage = DMG_BLOCK

        self.health -= damage
        self.shake_request = 6 if attacker_state == HEAVY_ATTACK else 3

        if self.health <= 0:
            self.health = 0
            self.alive  = False
            self.state  = DEAD
            self.frame_index = 0
            self.frame_timer = 0
            self.state_done  = False
        else:
            self.stun_timer = 350 if attacker_state == HEAVY_ATTACK else 200
            self.state       = HIT
            self.frame_index = 0
            self.frame_timer = 0
            self.state_done  = False

    def register_combo_hit(self):
        self.combo_timer = 0
        self.combo_count += 1

    # ──────────────────────────────────────────────────────────────────────────
    # Draw
    # ──────────────────────────────────────────────────────────────────────────

    def draw(self, surface):
        frames = self.anim.get(self.state, self.anim[IDLE])
        idx    = min(self.frame_index, len(frames) - 1)
        img    = frames[idx]

        if self.flip:
            img = pygame.transform.flip(img, True, False)

        # Anchor: sprite bottom-centre at (self.x, self.y)
        draw_x = int(self.x) - SP_W // 2
        draw_y = int(self.y) - SP_H + 10   # +10 to seat boots on floor

        surface.blit(img, (draw_x, draw_y))

        # Debug hitbox (comment out in production)
        # pygame.draw.rect(surface, (255,0,0), self.rect, 1)
        # if self.attack_rect:
        #     pygame.draw.rect(surface, (255,255,0), self.attack_rect, 1)


# ──────────────────────────────────────────────────────────────────────────────
# Furniture Projectile
# ──────────────────────────────────────────────────────────────────────────────

class FurnitureProjectile:
    """A piece of furniture flying across the screen."""

    def __init__(self, x, y, direction, furniture_surf):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = direction * 14   # horizontal speed
        self.vy  = -8               # lob upward
        self.rot = 0.0
        self.rot_speed = direction * 8
        self.surf = furniture_surf
        self.rect = pygame.Rect(int(x), int(y), 80, 70)
        self.active = True
        self.hit_target = False

    def update(self, dt):
        self.vy  += GRAVITY * 0.5
        self.x   += self.vx
        self.y   += self.vy
        self.rot += self.rot_speed
        self.rect.topleft = (int(self.x), int(self.y))

        if self.y > FLOOR_Y + 50 or self.x < -200 or self.x > 2000:
            self.active = False

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.surf, self.rot)
        rr = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rr.topleft)
