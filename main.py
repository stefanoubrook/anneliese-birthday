import pygame
import asyncio
import random
import math
import sys

# ==========================================
# 1. SETUP CONSTANTS & CONFIGURATION
# ==========================================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
GRID_SIZE = 8
TILE_SIZE = 70
BOARD_WIDTH = GRID_SIZE * TILE_SIZE
BOARD_HEIGHT = GRID_SIZE * TILE_SIZE

BOARD_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 320

BRAT_GREEN = (138, 206, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ==========================================
# 2. TILE CLASS
# ==========================================
class Tile:
    def __init__(self, row, col, color_id, start_y=None):
        self.row = row
        self.col = col
        self.color_id = color_id
        self.visual_x = col * TILE_SIZE
        self.visual_y = start_y if start_y is not None else row * TILE_SIZE
        self.speed = 12

    def update(self):
        target_y = self.row * TILE_SIZE
        if self.visual_y < target_y:
            self.visual_y = min(self.visual_y + self.speed, target_y)
        elif self.visual_y > target_y:
            self.visual_y = max(self.visual_y - self.speed, target_y)

        target_x = self.col * TILE_SIZE
        if self.visual_x < target_x:
            self.visual_x = min(self.visual_x + self.speed, target_x)
        elif self.visual_x > target_x:
            self.visual_x = max(self.visual_x - self.speed, target_x)

# ==========================================
# 3. CORE GAME LOGIC
# ==========================================
def find_matches(grid):
    matched_indices = set()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            t1, t2, t3 = grid[r][c], grid[r][c+1], grid[r][c+2]
            if t1 and t2 and t3 and t1.color_id == t2.color_id == t3.color_id:
                matched_indices.update([(r, c), (r, c+1), (r, c+2)])
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            t1, t2, t3 = grid[r][c], grid[r+1][c], grid[r+2][c]
            if t1 and t2 and t3 and t1.color_id == t2.color_id == t3.color_id:
                matched_indices.update([(r, c), (r+1, c), (r+2, c)])
    return list(matched_indices)

def apply_gravity(grid):
    for c in range(GRID_SIZE):
        existing_tiles = [grid[r][c] for r in range(GRID_SIZE) if grid[r][c] is not None]
        num_new = GRID_SIZE - len(existing_tiles)
        for r in range(GRID_SIZE):
            grid[r][c] = None
        for r in range(num_new):
            start_y = -(r + 1) * TILE_SIZE
            grid[r][c] = Tile(r, c, random.randint(0, 3), start_y=start_y)
        for i, tile in enumerate(existing_tiles):
            new_row = num_new + i
            tile.row = new_row
            grid[new_row][c] = tile

def is_board_stable(grid):
    for row in grid:
        for tile in row:
            if tile and (tile.visual_y != tile.row * TILE_SIZE or tile.visual_x != tile.col * TILE_SIZE):
                return False
    return True

def get_tinted_surface(surface, color):
    tinted = surface.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted

def load_image(path, size=None, smooth=False):
    """Load an image, optionally scale it. Returns None on failure."""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            if smooth:
                img = pygame.transform.smoothscale(img, size)
            else:
                img = pygame.transform.scale(img, size)
        return img
    except:
        return None

# ==========================================
# 5. MAIN GAME ENGINE
# ==========================================
async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Annelliese's 30th Birthday Match-3")
    clock = pygame.time.Clock()

    # --- ASSET LOADING ---
    disco_ball_img = load_image("assets/images/disco_ball.png", (225, 225))
    if not disco_ball_img:
        disco_ball_img = pygame.Surface((225, 225), pygame.SRCALPHA)
        pygame.draw.circle(disco_ball_img, (200, 200, 200), (112, 112), 110)

    neon_sign_img = load_image("assets/images/neon_sign.png", (200, 100))
    neon_flash_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255), (255, 255, 50), (255, 50, 255)]

    mystery_machine_img = load_image("assets/images/mystery_machine.png", (300, 200))
    crowd_img = load_image("assets/images/crowd.png", (SCREEN_WIDTH, 300))
    charli_img = load_image("assets/images/charli.png", (300, 390))
    scooby_img = load_image("assets/images/scooby.png", (150, 180))
    booth_left = load_image("assets/images/booth.png", (350, 250))
    addison_img = load_image("assets/images/addison.png", (150, 200))
    paparazzi_img = load_image("assets/images/paparazzi.png", (350, 150))
    homer_img = load_image("assets/images/homer.png", (127, 153))

    pink_img = None
    try:
        pink_raw = pygame.image.load("assets/images/pink.png").convert_alpha()
        p_orig_w, p_orig_h = pink_raw.get_size()
        p_target_w = 130
        p_target_h = int(p_target_w * (p_orig_h / p_orig_w))
        pink_img = pygame.transform.smoothscale(pink_raw, (p_target_w, p_target_h))
    except:
        pass

    paparazzi_2_img = load_image("assets/images/paparazzi_2.png")
    if paparazzi_2_img:
        p2_w = 350
        paparazzi_2_img = pygame.transform.smoothscale(paparazzi_2_img, (p2_w, int(p2_w * (768 / 1344))))

    vip_photo = load_image("assets/images/anneliese_photo.png")
    if vip_photo:
        vw = int(350 * 0.65)
        vip_photo = pygame.transform.smoothscale(vip_photo, (vw, int(vw * (1280 / 1775))))

    tile_id_colors = [(255, 0, 255), (0, 255, 255), (229, 237, 35), (255, 255, 255)]
    birthday_flash_colors = [(255, 255, 255), (0, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 80, 0), (255, 0, 0), (130, 0, 255)]

    annie_photos = []
    try:
        for i in range(1, 5):
            img = pygame.image.load(f"assets/images/anneliese_{i}.png").convert_alpha()
            if i == 3:
                orig_w, orig_h = img.get_size()
                crop_size = int(min(orig_w, orig_h) * 0.6)
                crop_x = (orig_w - crop_size) // 2
                crop_y = (orig_h - crop_size) // 2
                zoom_surf = pygame.Surface((crop_size, crop_size), pygame.SRCALPHA)
                zoom_surf.blit(img, (0, 0), (crop_x, crop_y, crop_size, crop_size))
                img = zoom_surf
            size = TILE_SIZE - 14
            img = pygame.transform.smoothscale(img, (size, size))
            mask = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255), (size // 2, size // 2), size // 2)
            img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            annie_photos.append(img)
    except:
        pass

    try:
        font_small = pygame.font.SysFont("Arial Narrow", 24)
        font_brat = pygame.font.SysFont("Arial", 75, bold=True)
    except:
        font_small = pygame.font.SysFont("Arial", 24)
        font_brat = pygame.font.SysFont("Arial", 60)

    try:
        font_brat_title = pygame.font.SysFont("Arial Narrow, Arial", 85, bold=True)
    except:
        font_brat_title = pygame.font.SysFont("Arial", 85, bold=True)

    # --- PRE-CACHE NEON SIGN TINTS ---
    neon_tinted = []
    if neon_sign_img:
        for color in neon_flash_colors:
            neon_tinted.append(get_tinted_surface(neon_sign_img, color))

    # --- PRE-CACHE TITLE RENDERS ---
    title_renders = []
    for col in birthday_flash_colors:
        l1 = font_brat_title.render("happy 30 birthday", True, col)
        l2 = font_brat_title.render("anneliese", True, col)
        title_renders.append((l1, l2))

    # --- PRE-CREATE REUSABLE SURFACES ---
    beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    glitch_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pop_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pop_surface.fill(WHITE)
    pop_surface.set_alpha(60)

    # --- PRE-CACHE PARTICLE SURFACES ---
    particle_cache = {}
    for col in tile_id_colors:
        for alpha in range(0, 256, 10):
            p_surf = pygame.Surface((6, 6))
            p_surf.fill(col)
            p_surf.set_alpha(alpha)
            particle_cache[(col, alpha)] = p_surf

    # --- INIT GAME STATE ---
    match_sounds = []
    party_girl_5 = None

    grid = [[Tile(r, c, random.randint(0, 3)) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
    while find_matches(grid):
        grid = [[Tile(r, c, random.randint(0, 3)) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

    light_colors = [(255, 255, 255, 60), (255, 20, 147, 80), (0, 191, 255, 80), (138, 43, 226, 80)]
    current_light_color = light_colors[0]

    # --- WAITING SCREEN ---
    waiting = True
    while waiting:
        screen.fill(BRAT_GREEN)
        title_surf = font_brat.render("happy 30th birthday annelliese", True, BLACK)
        start_surf = font_small.render("click to play", True, BLACK)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        screen.blit(start_surf, start_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONUP:
                waiting = False
                # Init audio after user gesture so browser allows AudioContext
                snd_ext = "ogg" if sys.platform == "emscripten" else "mp3"
                try:
                    pygame.mixer.music.load("assets/sounds/background_track.mp3")
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                except:
                    pass
                for i in [1, 2]:
                    try:
                        s = pygame.mixer.Sound(f"assets/sounds/party_girl_{i}.{snd_ext}")
                        s.set_volume(0.8)
                        match_sounds.append(s)
                    except:
                        pass
                try:
                    party_girl_5 = pygame.mixer.Sound(f"assets/sounds/party_girl_5.{snd_ext}")
                    party_girl_5.set_volume(1.0)
                except:
                    pass
        await asyncio.sleep(0)

    pygame.event.clear()

    selected_tile = None
    running = True
    color_timer = 0
    ball_angle = 0
    glitch_timer, glitch_active, glitch_rects = 0, False, []
    flash_timer, flash_active, current_lens = 0, False, (0, 0)
    particles = []
    lenses = [(110, 19, False), (75, 80, True), (125, 50, True), (168, 38, True), (215, 55, True), (270, 90, True), (180, -30, False), (240, 19, False)]
    pap_x1, pap_y1 = 20, 150
    pap_x2, pap_y2 = 20, 50
    vip_x, vip_y = 80, 90

    # --- MAIN GAME LOOP ---
    while running:
        stable = is_board_stable(grid)
        if stable:
            matches = find_matches(grid)
            if matches:
                if len(matches) >= 5 and party_girl_5:
                    try:
                        party_girl_5.play()
                    except:
                        pass
                elif match_sounds:
                    try:
                        random.choice(match_sounds).play()
                    except:
                        pass
                for r, c in matches:
                    t = grid[r][c]
                    if t:
                        for _ in range(random.randint(4, 6)):
                            particles.append({
                                'x': BOARD_X + t.visual_x + TILE_SIZE // 2,
                                'y': BOARD_Y + t.visual_y + TILE_SIZE // 2,
                                'vx': random.uniform(-4, 4),
                                'vy': random.uniform(-4, 4),
                                'life': 25,
                                'color': tile_id_colors[t.color_id % len(tile_id_colors)]
                            })
                    grid[r][c] = None
                apply_gravity(grid)

        glitch_timer += 1
        if not glitch_active and random.random() < 0.05:
            glitch_active, glitch_timer, glitch_rects = True, 0, []
            for _ in range(random.randint(2, 6)):
                g_col = random.choice(birthday_flash_colors) + (random.randint(40, 150),)
                glitch_rects.append((random.randint(0, SCREEN_HEIGHT), random.randint(2, 195), g_col))
        if glitch_active and glitch_timer > 7:
            glitch_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and stable:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if BOARD_X <= mouse_x <= BOARD_X + BOARD_WIDTH and BOARD_Y <= mouse_y <= BOARD_Y + BOARD_HEIGHT:
                    col, row = (mouse_x - BOARD_X) // TILE_SIZE, (mouse_y - BOARD_Y) // TILE_SIZE
                    if selected_tile is None:
                        selected_tile = (row, col)
                    else:
                        r1, c1 = selected_tile
                        r2, c2 = (row, col)
                        if abs(r1 - r2) + abs(c1 - c2) == 1:
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            grid[r1][c1].row, grid[r1][c1].col = r1, c1
                            grid[r2][c2].row, grid[r2][c2].col = r2, c2
                            if not find_matches(grid):
                                grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                                grid[r1][c1].row, grid[r1][c1].col = r1, c1
                                grid[r2][c2].row, grid[r2][c2].col = r2, c2
                        selected_tile = None

        screen.fill(BRAT_GREEN)
        ball_angle += 1.5
        color_timer += 1
        if color_timer % 45 == 0:
            current_light_color = random.choice(light_colors)

        # --- LIGHT BEAMS (reuse surface) ---
        beam_surface.fill((0, 0, 0, 0))
        cx, cy = SCREEN_WIDTH // 2, 110
        for i in range(8):
            rad = math.radians(ball_angle + (i * 45))
            cos_r, sin_r = math.cos(rad), math.sin(rad)
            e1 = (cx + cos_r * 1500 - sin_r * 225, cy + sin_r * 1500 + cos_r * 225)
            e2 = (cx + cos_r * 1500 + sin_r * 225, cy + sin_r * 1500 - cos_r * 225)
            pygame.draw.polygon(beam_surface, current_light_color, [(cx, cy), e1, e2])
            e1c = (cx + cos_r * 1500 - sin_r * 75, cy + sin_r * 1500 + cos_r * 75)
            e2c = (cx + cos_r * 1500 + sin_r * 75, cy + sin_r * 1500 - cos_r * 75)
            pygame.draw.polygon(beam_surface, (255, 255, 255, 120), [(cx, cy), e1c, e2c])
        screen.blit(beam_surface, (0, 0))

        # --- VIP & PAPARAZZI ---
        if not flash_active and random.random() < 0.035:
            flash_active, flash_timer = True, 0
            choice = random.choice(lenses)
            base_x = pap_x2 if choice[2] else pap_x1
            base_y = pap_y2 if choice[2] else pap_y1
            current_lens = (base_x + choice[0], base_y + choice[1])

        if flash_active:
            flash_surface.fill((0, 0, 0, 0))
            radius = int(140 * (0.75 ** flash_timer))
            if radius > 5:
                pygame.draw.circle(flash_surface, (255, 255, 255, 160), current_lens, radius)
            screen.blit(flash_surface, (0, 0))

        if paparazzi_2_img:
            screen.blit(paparazzi_2_img, (pap_x2, pap_y2))
        if vip_photo:
            screen.blit(vip_photo, (vip_x, vip_y))
            if flash_active and flash_timer < 4:
                glow = vip_photo.copy()
                glow.fill((120, 120, 120), special_flags=pygame.BLEND_RGB_ADD)
                screen.blit(glow, (vip_x, vip_y))

        if paparazzi_img:
            screen.blit(paparazzi_img, (pap_x1, pap_y1))

        if flash_active:
            if flash_timer < 2:
                screen.blit(pop_surface, (0, 0))
            flash_timer += 1
            if flash_timer > 8:
                flash_active = False

        # --- TITLE (cached renders) ---
        c_idx = (color_timer // 15) % len(title_renders)
        l1, l2 = title_renders[c_idx]
        screen.blit(l1, l1.get_rect(center=(SCREEN_WIDTH // 2, 180)))
        screen.blit(l2, l2.get_rect(center=(SCREEN_WIDTH // 2, 250)))

        # --- DISCO BALL ---
        wobble = math.sin(ball_angle * 0.05) * 8
        screen.blit(disco_ball_img, (SCREEN_WIDTH // 2 - 112 + wobble, 5))

        # --- EXTRAS ---
        if crowd_img:
            screen.blit(crowd_img, (0, 780 + math.sin(ball_angle * 0.1) * 10))
        if neon_tinted:
            screen.blit(neon_tinted[(color_timer // 30) % len(neon_tinted)], (75, 450))
        if booth_left:
            screen.blit(booth_left, (20, 580))
            if homer_img:
                screen.blit(homer_img, (210, 580))
            if pink_img:
                screen.blit(pink_img, (160, 610))
            if scooby_img:
                screen.blit(scooby_img, (70, 540))
        if mystery_machine_img:
            mx, my = SCREEN_WIDTH - 300, 300
            if addison_img:
                bop = math.sin(color_timer * 0.1) * 10
                screen.blit(addison_img, (mx + 60, my - 135 + bop))
            screen.blit(mystery_machine_img, (mx, my))
        if charli_img:
            screen.blit(charli_img, (SCREEN_WIDTH - 270, SCREEN_HEIGHT - 450))

        if glitch_active:
            glitch_surface.fill((0, 0, 0, 0))
            for g_y, g_h, g_col in glitch_rects:
                pygame.draw.rect(glitch_surface, g_col, (0, g_y, SCREEN_WIDTH, g_h))
            screen.blit(glitch_surface, (0, 0))

        # --- GAME BOARD ---
        strobe_val = (math.sin(color_timer * 0.4) + 1) / 2
        strobe_color = (int(255 - strobe_val * 50), 255, int(255 - strobe_val * 50))

        pygame.draw.rect(screen, BLACK, (BOARD_X - 5, BOARD_Y - 5, BOARD_WIDTH + 10, BOARD_HEIGHT + 10))
        pygame.draw.rect(screen, strobe_color, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                t = grid[r][c]
                if t:
                    t.update()
                    dx, dy = BOARD_X + t.visual_x, BOARD_Y + t.visual_y
                    g_col = tile_id_colors[t.color_id % len(tile_id_colors)]
                    pygame.draw.circle(screen, g_col, (dx + 35, dy + 35), 33)
                    pygame.draw.circle(screen, BLACK, (dx + 35, dy + 35), 29, 2)
                    if annie_photos:
                        screen.blit(annie_photos[t.color_id % len(annie_photos)], (dx + 7, dy + 7))
                    if selected_tile == (r, c):
                        pygame.draw.rect(screen, BRAT_GREEN, (dx, dy, 70, 70), 4)

        # --- PARTICLES (optimized) ---
        alive = []
        for p in particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] > 0:
                alpha = (p['life'] * 255 // 25) // 10 * 10
                alpha = max(0, min(250, alpha))
                key = (p['color'], alpha)
                if key in particle_cache:
                    screen.blit(particle_cache[key], (p['x'], p['y']))
                alive.append(p)
        particles = alive

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
