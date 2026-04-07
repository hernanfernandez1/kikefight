import pygame

# Screen
SCREEN_W = 1280
SCREEN_H  = 720
FPS = 60

# Physics
GRAVITY   = 0.9
FLOOR_Y   = 530       # y where characters stand
SPEED     = 6
JUMP_VEL  = -22

# Game
ROUND_TIME    = 99    # seconds
MAX_HEALTH    = 100
COMBO_WINDOW  = 1800  # ms to chain hits

# Animation frame duration (ms)
ANIM_MS = {
    'idle':          160,
    'walk':          100,
    'jump':          100,
    'light_attack':   80,
    'heavy_attack':   90,
    'special':       100,
    'block':         120,
    'hit':           100,
    'dead':          120,
}

# Damage
DMG_LIGHT  = 7
DMG_HEAVY  = 14
DMG_SPECIAL = 20   # furniture throw
DMG_BLOCK   = 2   # chip damage

# Kike palette
K_GREEN     = (45,  165,  75)
K_GREEN_D   = (25,  110,  50)
K_GREEN_DD  = (15,   75,  35)
K_SKIN      = (215, 165, 110)
K_SKIN_D    = (180, 130,  85)
K_MASK      = (30,  140,  60)
K_HAIR      = (28,   18,  12)
K_BELT      = (48,   38,  32)
K_BLADE     = (205, 212, 220)
K_SHINE     = (245, 250, 255)
K_GUARD     = (185, 152,  38)
K_HANDLE    = (38,   28,  18)
K_BOOT      = (26,   26,  30)
K_BOOT_ACC  = (20,   90,  42)
K_GAUNTLET  = (32,   32,  40)
K_UA        = (18,   18,  18)

# Blue Fighter palette
B_BLUE      = (55,   90, 200)
B_BLUE_D    = (35,   60, 150)
B_WHITE     = (230, 230, 230)
B_SKIN      = (215, 165, 110)
B_SKIN_D    = (180, 130,  85)
B_HAIR      = (28,   18,  12)
B_BELT      = (20,   20,  20)
B_BOOT      = (26,   26,  30)

# UI colors
UI_HP_BG    = (60,   10,  10)
UI_HP_GREEN = (50,  210,  60)
UI_HP_RED   = (210,  40,  40)
UI_HP_GOLD  = (200, 160,  30)
UI_FRAME    = (30,   20,  10)
UI_COMBO    = (80,  200, 255)
UI_TEXT     = (240, 230, 210)
UI_SHADOW   = (0,    0,   0)

# Canvas size for sprites (pixels, transparent background)
SP_W = 200
SP_H = 220

# Hitbox offsets from sprite draw position
HIT_LIGHT  = pygame.Rect(0,  40, 100, 80)
HIT_HEAVY  = pygame.Rect(0,  30, 130, 100)
HIT_SPECIAL= pygame.Rect(0,   0, 180, 160)

# Furniture types for special attack
FURNITURE = ['chair', 'table', 'barrel', 'vase']
