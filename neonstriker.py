import pygame
import random
import math
import array
import os

# ======================================
# PATH FIX (For Launcher Compatibility)
# ======================================
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_path(filename):
    return os.path.join(BASE_PATH, filename)


# --- Constants ---
WHITE, GREEN, YELLOW, ORANGE, BLACK, RED, GRAY, CYAN = ((255, 255, 255), (0, 255, 0), (255, 255, 0), (255, 165, 0),
                                                        (0, 0, 0), (220, 20, 60), (40, 40, 40), (0, 255, 255))
HEADER_HEIGHT = 120
MENU, PLAYING, PAUSED, DYING, GAMEOVER, TRANSITION = 0, 1, 2, 3, 4, 5


def get_angle(origin, target):
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    return math.degrees(math.atan2(-dy, dx)) - 90


def create_beep(freq, duration, volume=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = float(i) / sample_rate
        buf[i] = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
    return pygame.mixer.Sound(buf)


# --- Sprite Classes ---
class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, color, font):
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=pos)
        self.vel_y = -2
        self.alpha = 255

    def update(self):
        self.rect.y += self.vel_y
        self.alpha -= 5
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class Button:
    def __init__(self, text, pos, size, font):
        self.text = text
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = pos
        self.font = font
        self.is_selected = False

    def draw(self, screen, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos) or self.is_selected
        color = GREEN if hover else GRAY
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=5)
        txt = self.font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))


class Item(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.type = random.choice(["heal", "speed", "shield"])
        self.color = GREEN if self.type == "heal" else YELLOW if self.type == "speed" else CYAN
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (12, 12), 10, 2)
        pygame.draw.circle(self.image, WHITE, (12, 12), 4)
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0

    def update(self):
        self.timer += 0.1
        self.rect.y += math.sin(self.timer) * 0.6


# --- Core Game Logic ---
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.joystick.init()

        info = pygame.display.Info()
        self.WIDTH, self.HEIGHT = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)

        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Impact", 100)
        self.font_md = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 20, bold=True)

        self.state = MENU
        self.high_score, self.score, self.shake = 0, 0, 0
        self.music_vol, self.sound_vol = 1.0, 0.25
        self.death_timer, self.transition_timer = 0, 0

        # Power-up System
        self.inventory = {"speed": 0, "shield": 0}
        self.boost_timers = {"speed": 0, "shield": 0}

        # Audio Setup
        try:
            self.snd_shoot = pygame.mixer.Sound(get_path("assets/sounds/shoot.mp3"))
        except:
            self.snd_shoot = create_beep(440, 0.1)
        try:
            self.snd_explode = pygame.mixer.Sound(get_path("assets/sounds/explode.mp3"))
        except:
            self.snd_explode = create_beep(100, 0.3)
        try:
            self.snd_hit = pygame.mixer.Sound(get_path("assets/sounds/hit.mp3"))
        except:
            self.snd_hit = create_beep(200, 0.1)
        try:
            self.snd_heal = pygame.mixer.Sound(get_path("assets/sounds/heal.mp3"))
        except:
            self.snd_heal = create_beep(600, 0.2)
        try:
            self.snd_powerup = pygame.mixer.Sound(get_path("assets/sounds/powerup.mp3"))
        except:
            self.snd_powerup = create_beep(800, 0.2)
        self.apply_sound_volumes()

        try:
            pygame.mixer.music.load(get_path("assets/sounds/music.mp3"))
            pygame.mixer.music.set_volume(self.music_vol)
            pygame.mixer.music.play(-1)
        except:
            pass

        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0);
            self.joystick.init()

        self.is_wave = False
        self.wave_count = 1
        self.phase_duration = random.randint(50000, 90000)
        self.timer_ms = self.phase_duration
        self.btn_index = 0

        self.reset_game()
        self.init_buttons()

    def apply_sound_volumes(self):
        sounds = [self.snd_shoot, self.snd_explode, self.snd_hit, self.snd_heal, self.snd_powerup]
        for s in sounds: s.set_volume(self.sound_vol)

    def init_buttons(self):
        mid_x, mid_y = self.WIDTH // 2, self.HEIGHT // 2
        b_w, b_h = 320, 60
        self.start_btns = [
            Button("PLAY", (mid_x, mid_y - 40), (b_w, b_h), self.font_md),
            Button(f"MUSIC: {int(self.music_vol * 100)}%", (mid_x, mid_y + 40), (b_w, b_h), self.font_md),
            Button(f"SOUND: {int(self.sound_vol * 100)}%", (mid_x, mid_y + 120), (b_w, b_h), self.font_md),
            Button("EXIT", (mid_x, mid_y + 200), (b_w, b_h), self.font_md)
        ]
        self.pause_btns = [
            Button("RESUME", (mid_x, mid_y - 40), (b_w, b_h), self.font_md),
            Button("RESTART", (mid_x, mid_y + 40), (b_w, b_h), self.font_md),
            Button(f"MUSIC: {int(self.music_vol * 100)}%", (mid_x, mid_y + 120), (b_w, b_h), self.font_md),
            Button(f"SOUND: {int(self.sound_vol * 100)}%", (mid_x, mid_y + 200), (b_w, b_h), self.font_md),
            Button("QUIT TO MENU", (mid_x, mid_y + 280), (b_w, b_h), self.font_md)
        ]
        self.mouse_pause_rect = pygame.Rect(self.WIDTH - 80, 35, 50, 50)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        current_btns = self.start_btns if self.state == MENU else self.pause_btns
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.size
                self.init_buttons()

            if self.state in [MENU, PAUSED]:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_w]: self.btn_index = (self.btn_index - 1) % len(current_btns)
                    if event.key in [pygame.K_DOWN, pygame.K_s]: self.btn_index = (self.btn_index + 1) % len(
                        current_btns)
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]: self.activate_button(self.btn_index)
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button in [11, 13]: self.btn_index = (self.btn_index - 1) % len(current_btns)
                    if event.button in [12, 14]: self.btn_index = (self.btn_index + 1) % len(current_btns)
                    if event.button == 0: self.activate_button(self.btn_index)

            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (
                    event.type == pygame.JOYBUTTONDOWN and event.button in [6, 7]):
                if self.state != TRANSITION: self.toggle_pause()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == PLAYING and self.mouse_pause_rect.collidepoint(mouse_pos):
                    self.state = PAUSED
                elif self.state in [MENU, PAUSED]:
                    for i, btn in enumerate(current_btns):
                        if btn.rect.collidepoint(mouse_pos): self.activate_button(i)

        for i, btn in enumerate(current_btns): btn.is_selected = (i == self.btn_index)
        return True

    def activate_button(self, index):
        if self.state == MENU:
            if index == 0:
                self.state = PLAYING
            elif index == 1:
                self.cycle_music_volume()
            elif index == 2:
                self.cycle_sound_volume()
            elif index == 3:
                self.running = False
        elif self.state == PAUSED:
            if index == 0:
                self.state = PLAYING
            elif index == 1:
                self.reset_game(); self.state = PLAYING
            elif index == 2:
                self.cycle_music_volume()
            elif index == 3:
                self.cycle_sound_volume()
            elif index == 4:
                self.reset_game(); self.state = MENU
        self.sync_audio_buttons()

    def cycle_music_volume(self):
        self.music_vol = (self.music_vol + 0.25) if self.music_vol < 1.0 else 0.0
        pygame.mixer.music.set_volume(self.music_vol)

    def cycle_sound_volume(self):
        self.sound_vol = (self.sound_vol + 0.25) if self.sound_vol < 1.0 else 0.0
        self.apply_sound_volumes()
        if self.sound_vol > 0: self.snd_shoot.play()

    def sync_audio_buttons(self):
        m, s = f"MUSIC: {int(self.music_vol * 100)}%", f"SOUND: {int(self.sound_vol * 100)}%"
        for btns in [self.start_btns, self.pause_btns]:
            for b in btns:
                if "MUSIC" in b.text: b.text = m
                if "SOUND" in b.text: b.text = s

    def toggle_pause(self):
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING
        elif self.state == GAMEOVER:
            self.reset_game(); self.state = MENU

    def update(self):
        dt = self.clock.get_time()
        if self.state == TRANSITION:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.state = PLAYING
                self.is_wave = not self.is_wave
                if self.is_wave: self.wave_count += 1
                self.timer_ms = random.randint(50000, 90000)
                self.phase_duration = self.timer_ms
                self.gen_maze()
            return

        self.explosions.update()
        self.ui_elements.update()

        if self.state == DYING:
            self.death_timer -= dt
            if self.death_timer <= 0: self.state = GAMEOVER
            return

        if self.state != PLAYING: return

        # Parallel Boost Management
        for b_type in ["speed", "shield"]:
            if self.boost_timers[b_type] > 0:
                self.boost_timers[b_type] -= dt
            # Trigger next item in stack
            if self.boost_timers[b_type] <= 0 and self.inventory[b_type] > 0:
                self.inventory[b_type] -= 1
                self.boost_timers[b_type] = 10000

        if self.shot_cooldown > 0: self.shot_cooldown -= dt
        self.timer_ms -= dt
        if self.timer_ms <= 0:
            self.state = TRANSITION;
            self.transition_timer = 5000
            self.bullets.empty();
            self.enemies.empty();
            self.items.empty()
            return

        if random.randint(0, 100) < (8 if self.is_wave else 3): self.spawn_enemy()

        # Movement Input
        keys, move = pygame.key.get_pressed(), pygame.Vector2(0, 0)
        if keys[pygame.K_a]: move.x = -1
        if keys[pygame.K_d]: move.x = 1
        if keys[pygame.K_w]: move.y = -1
        if keys[pygame.K_s]: move.y = 1
        if self.joystick:
            if abs(self.joystick.get_axis(0)) > 0.2: move.x = self.joystick.get_axis(0)
            if abs(self.joystick.get_axis(1)) > 0.2: move.y = self.joystick.get_axis(1)

        # Aiming & Firing
        aim_angle = self.player.current_angle
        shot_rate = 60 if self.boost_timers["speed"] > 0 else 180

        if self.joystick:
            rx, ry = self.joystick.get_axis(2), self.joystick.get_axis(3)
            if abs(rx) > 0.3 or abs(ry) > 0.3:
                aim_angle = math.degrees(math.atan2(-ry, rx)) - 90
                if self.shot_cooldown <= 0:
                    self.bullets.add(Bullet(self.player.pos, aim_angle))
                    if self.sound_vol > 0: self.snd_shoot.play(); self.shot_cooldown = shot_rate

        if pygame.mouse.get_pressed()[0] and self.shot_cooldown <= 0:
            aim_angle = get_angle(self.player.pos, pygame.mouse.get_pos())
            if not self.mouse_pause_rect.collidepoint(pygame.mouse.get_pos()):
                self.bullets.add(Bullet(self.player.pos, aim_angle))
                if self.sound_vol > 0: self.snd_shoot.play(); self.shot_cooldown = shot_rate

        self.player.update(move, self.walls, self.WIDTH, self.HEIGHT, aim_angle, self.boost_timers["shield"] > 0)
        self.enemies.update(self.player.pos, self.walls)
        self.bullets.update()
        self.items.update()

        # Item Collection
        for item in pygame.sprite.spritecollide(self.player, self.items, True):
            if self.sound_vol > 0: self.snd_powerup.play()
            if item.type == "heal":
                self.player.hp = min(100, self.player.hp + 20)
                self.ui_elements.add(FloatingText(self.player.rect.center, "HEALED", GREEN, self.font_sm))
            else:
                self.inventory[item.type] += 1
                self.ui_elements.add(
                    FloatingText(self.player.rect.center, f"+1 {item.type.upper()}", item.color, self.font_sm))

        # Combat Results
        for b in self.bullets:
            e = pygame.sprite.spritecollideany(b, self.enemies)
            if e:
                pts = random.randint(10, 50);
                self.score += pts
                self.ui_elements.add(FloatingText(e.rect.center, f"+{pts}", YELLOW, self.font_sm))
                self.explosions.add(Explosion(e.pos, e.color, 12))
                if self.sound_vol > 0: self.snd_explode.play()
                if random.random() < 0.15: self.items.add(Item(e.pos))
                e.kill();
                b.kill();
                self.shake = 10
            elif pygame.sprite.spritecollideany(b, self.walls):
                self.explosions.add(Explosion(b.rect.center, CYAN, 6));
                b.kill()

        # Collision & Damage
        hit_enemy = pygame.sprite.spritecollideany(self.player, self.enemies)
        if hit_enemy:
            if self.boost_timers["shield"] > 0:
                self.explosions.add(Explosion(hit_enemy.pos, hit_enemy.color, 12));
                hit_enemy.kill();
                self.shake = 5
            else:
                dmg = random.randint(10, 20);
                self.player.hp -= dmg
                self.ui_elements.add(FloatingText(self.player.rect.center, f"-{dmg}", RED, self.font_sm))
                hit_enemy.kill();
                self.player.flash = 15;
                self.shake = 20
                if self.sound_vol > 0: self.snd_hit.play()

        if self.player.hp <= 0:
            self.state = DYING;
            self.death_timer = 2000;
            self.shake = 40
            if self.sound_vol > 0: self.snd_explode.play()
            for _ in range(5): self.explosions.add(Explosion(self.player.pos, GREEN, random.randint(5, 15)))
            if self.score > self.high_score: self.high_score = self.score

    def draw(self):
        self.screen.fill(BLACK)
        off = pygame.Vector2(random.randint(-self.shake, self.shake),
                             random.randint(-self.shake, self.shake)) if self.shake > 0 else (0, 0)
        if self.shake > 0: self.shake -= 1

        if self.state != TRANSITION:
            for g in [self.walls, self.bullets, self.enemies, self.items]:
                for s in g: self.screen.blit(s.image, s.rect.move(off))
            if self.state != DYING: self.screen.blit(self.player.image, self.player.rect.move(off))
            for ex in self.explosions: ex.draw(self.screen, off)
            for ui in self.ui_elements: self.screen.blit(ui.image, ui.rect.move(off))

            # UI Header
            pygame.draw.rect(self.screen, (15, 15, 25), (0, 0, self.WIDTH, HEADER_HEIGHT))
            pygame.draw.line(self.screen, GREEN, (0, HEADER_HEIGHT), (self.WIDTH, HEADER_HEIGHT), 2)
            px, py = 40, 30
            pygame.draw.rect(self.screen, RED, (px, py, 200, 20))
            pygame.draw.rect(self.screen, GREEN, (px, py, max(0, self.player.hp * 2), 20))
            self.screen.blit(self.font_md.render(f"SCORE: {self.score}", True, YELLOW), (px, py + 30))

            # Phase Progress Bar
            bar_w, cx = 400, (self.WIDTH // 2) - 200
            ratio = (1 - (self.timer_ms / self.phase_duration))
            c = (min(255, int(255 * ratio)), max(0, int(255 * (1 - ratio))), 50) if self.is_wave else CYAN
            pygame.draw.rect(self.screen, GRAY, (cx, py + 10, bar_w, 20))
            pygame.draw.rect(self.screen, c, (cx, py + 10, ratio * bar_w, 20))

            w_text = f"Enemy Wave {self.wave_count} coming" if not self.is_wave else f"Wave {self.wave_count - 1} active!"
            w_surf = self.font_sm.render(w_text, True, WHITE)
            self.screen.blit(w_surf, w_surf.get_rect(center=(self.WIDTH // 2, py + 46)))

            # Centered Inventory (Bottom)
            inv_items = [("speed", YELLOW), ("shield", CYAN)]
            spacing = 160
            start_x = self.WIDTH // 2 - ((len(inv_items) - 1) * spacing) // 2
            for i, (b_type, color) in enumerate(inv_items):
                cx, cy = start_x + (i * spacing), self.HEIGHT - 50
                pygame.draw.circle(self.screen, color, (cx - 40, cy), 18, 2)
                txt = self.font_sm.render(f"{b_type} x{self.inventory[b_type]}", True, WHITE)
                self.screen.blit(txt, (cx - 11, cy - 14))
                if self.boost_timers[b_type] > 0:
                    pygame.draw.circle(self.screen, WHITE, (cx - 40, cy), 22, 2)
                    b_width = (self.boost_timers[b_type] / 10000) * 50
                    pygame.draw.rect(self.screen, WHITE, (cx - 6, cy + 12, 50, 6))
                    pygame.draw.rect(self.screen, color, (cx - 6, cy + 12, b_width, 5))

            # Pause Toggle Button
            self.mouse_pause_rect.x = self.WIDTH - 80
            pc = GREEN if self.mouse_pause_rect.collidepoint(pygame.mouse.get_pos()) else WHITE
            pygame.draw.rect(self.screen, pc, self.mouse_pause_rect, 2, border_radius=5)
            self.screen.blit(self.font_md.render("||", True, pc),
                             (self.mouse_pause_rect.centerx - 8, self.mouse_pause_rect.centery - 15))
        else:
            # Transition Messaging
            msg = "ENEMIES WAVE COMING!" if not self.is_wave else "WAVE OVER!"
            sub = f"RECONFIGURING IN {int(self.transition_timer / 1000) + 1}..."
            t, st = self.font_lg.render(msg, True, GREEN), self.font_md.render(sub, True, WHITE)
            t.set_alpha(int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255))
            self.screen.blit(t, (self.WIDTH // 2 - t.get_width() // 2, self.HEIGHT // 2 - 50))
            self.screen.blit(st, (self.WIDTH // 2 - st.get_width() // 2, self.HEIGHT // 2 + 80))

        if self.state in [MENU, PAUSED]:
            ov = pygame.Surface((self.WIDTH, self.HEIGHT));
            ov.set_alpha(180)
            ov.fill(BLACK)
            self.screen.blit(ov, (0, 0))
            title = "NEON STRIKER" if self.state == MENU else "PAUSE"
            ts = self.font_lg.render(title, True, GREEN if self.state == MENU else WHITE)
            self.screen.blit(ts, (self.WIDTH // 2 - ts.get_width() // 2, self.HEIGHT // 2 - 250))
            for b in (self.start_btns if self.state == MENU else self.pause_btns): b.draw(self.screen,
                                                                                          pygame.mouse.get_pos())
        elif self.state == GAMEOVER:
            ov = pygame.Surface((self.WIDTH, self.HEIGHT));
            ov.set_alpha(200);
            ov.fill(BLACK);
            self.screen.blit(ov, (0, 0))
            go, sc = self.font_lg.render("GAME OVER", True, RED), self.font_md.render(
                f"SCORE: {self.score} | HIGH: {self.high_score}", True, WHITE)
            self.screen.blit(go, (self.WIDTH // 2 - go.get_width() // 2, 150))
            self.screen.blit(sc, (self.WIDTH // 2 - sc.get_width() // 2, 280))
            pt = self.font_md.render("PRESS ESC OR START TO RESTART", True, GREEN)
            pt.set_alpha(int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255))
            self.screen.blit(pt, (self.WIDTH // 2 - pt.get_width() // 2, 500))

        pygame.display.flip()

    def reset_game(self):
        self.player = Player(self.WIDTH // 2, self.HEIGHT // 2 + 100)
        self.enemies, self.bullets, self.explosions, self.walls, self.items, self.ui_elements = [pygame.sprite.Group()
                                                                                                 for _ in range(6)]
        self.score, self.shake, self.is_wave, self.wave_count = 0, 0, False, 1
        self.timer_ms = self.phase_duration
        self.shot_cooldown = 0
        self.boost_timers = {"speed": 0, "shield": 0}
        self.inventory = {"speed": 0, "shield": 0}
        self.gen_maze()

    def gen_maze(self):
        self.walls.empty()
        for _ in range(random.randint(10, 16)):
            w = Wall(random.randint(100, self.WIDTH - 100), random.randint(HEADER_HEIGHT + 100, self.HEIGHT - 100))
            if not w.rect.colliderect(self.player.rect.inflate(300, 300)): self.walls.add(w)

    def spawn_enemy(self):
        for _ in range(5):
            x, y = random.randint(50, self.WIDTH - 50), random.randint(HEADER_HEIGHT + 50, self.HEIGHT - 50)
            if not any(w.rect.collidepoint(x, y) for w in self.walls):
                self.enemies.add(Enemy(x, y, self.is_wave));
                break


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.orig = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.polygon(self.orig, GREEN, [(20, 0), (40, 60), (0, 60)])
        self.image, self.rect = self.orig, self.orig.get_rect(center=(x, y))
        self.pos, self.hp, self.flash, self.current_angle = pygame.Vector2(self.rect.center), 100, 0, 0

    def update(self, move, walls, w, h, angle, shielded):
        if move.length() > 0:
            target = self.pos + move.normalize() * 7
            old_rect = self.rect.copy()
            self.rect.center = target
            if pygame.sprite.spritecollideany(self, walls) or not (20 < self.rect.centerx < w - 20) or not (
                    HEADER_HEIGHT + 30 < self.rect.centery < h - 30):
                self.rect = old_rect
            else:
                self.pos = pygame.Vector2(self.rect.center)
        self.current_angle = angle
        self.image = pygame.transform.rotate(self.orig, self.current_angle)
        if shielded:
            s_surf = self.image.copy()
            pygame.draw.circle(s_surf, CYAN, (s_surf.get_width() // 2, s_surf.get_height() // 2), 25, 2)
            self.image = s_surf
        self.rect = self.image.get_rect(center=self.pos)
        if self.flash > 0: self.flash -= 1; self.image.fill(WHITE, special_flags=pygame.BLEND_RGB_ADD)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, wave):
        super().__init__()
        self.wave = wave
        self.shape = random.choice(["sq", "tri", "hex"])
        self.color = (random.randint(100, 255), 100, 255)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        if self.shape == "sq":
            pygame.draw.rect(self.image, self.color, (5, 5, 30, 30), 2)
        elif self.shape == "tri":
            pygame.draw.polygon(self.image, self.color, [(20, 5), (35, 35), (5, 35)], 2)
        else:
            pygame.draw.polygon(self.image, self.color, [(20, 0), (38, 10), (38, 30), (20, 40), (2, 30), (2, 10)], 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.speed = (2.0 if self.wave else 1.5)

    def update(self, p_pos, walls):
        direction = (p_pos - self.pos).normalize()
        self.pos += direction * self.speed
        self.rect.center = self.pos

        if pygame.sprite.spritecollideany(self, walls):
            deviation = random.uniform(-20, 20)
            bounce_dir = (-direction).rotate(deviation)
            self.pos += bounce_dir * self.speed * (8 if self.wave else 15)
            self.rect.center = self.pos


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7, 7), 7)
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.Vector2(0, -18).rotate(-angle)

    def update(self):
        self.rect.center += self.vel
        if not pygame.display.get_surface().get_rect().inflate(100, 100).contains(self.rect): self.kill()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((random.randint(40, 180), random.randint(40, 180)))
        self.image.fill((random.randint(40, 70), 60, random.randint(70, 100)))
        self.rect = self.image.get_rect(center=(x, y))


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, color, speed):
        super().__init__()
        self.pos, self.color, self.rad, self.alpha, self.speed = pos, color, 2, 255, speed

    def update(self):
        self.rad += self.speed;
        self.alpha -= 10
        if self.alpha <= 0: self.kill()

    def draw(self, surf, off):
        if self.alpha <= 0: return
        s = pygame.Surface((self.rad * 2, self.rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, list(self.color) + [max(0, self.alpha)], (self.rad, self.rad), self.rad)
        surf.blit(s, self.pos - pygame.Vector2(self.rad) + off)


g = Game()
g.running = True
while g.running:
    if not g.handle_input(): g.running = False
    g.update()
    g.draw()
    g.clock.tick(60)
pygame.quit()