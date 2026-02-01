import pygame
import random
import math
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Isometric Settings
TILE_SIZE = 50   
TILE_HEIGHT = 28 
Z_SCALE = 3.2    

# Colors
COLOR_BG = (135, 206, 235) 
COLOR_GRASS_LIGHT = (110, 205, 55)
COLOR_GRASS_DARK = (95, 190, 45)
COLOR_ROAD = (85, 90, 100)
COLOR_WATER = (80, 180, 240)
COLOR_RAIL = (80, 80, 80) # Gravel color
COLOR_RAIL_WOOD = (90, 60, 30)
COLOR_RAIL_METAL = (160, 160, 170)

COLOR_COIN = (255, 215, 0)
COLOR_CHICKEN = (255, 255, 255)
COLOR_CHICKEN_BEAK = (255, 160, 0)
COLOR_CHICKEN_COMB = (255, 40, 40)
COLOR_SHADOW = (0, 0, 0, 70) 
COLOR_STONE = (160, 160, 160)

# Train Colors
COLOR_TRAIN_BODY = (70, 130, 180) # Steel Blue
COLOR_TRAIN_ROOF = (200, 200, 220)
COLOR_SIGNAL_POLE = (50, 50, 50)
COLOR_SIGNAL_LIGHT_OFF = (80, 0, 0)
COLOR_SIGNAL_LIGHT_ON = (255, 0, 0)

# --- 3D Rendering Engine ---

def to_screen(gx, gy, z=0):
    screen_x = (gx - gy) * TILE_SIZE
    screen_y = (gx + gy) * TILE_HEIGHT / 2
    return screen_x, screen_y - (z * Z_SCALE)

def draw_block(surface, x_grid, y_grid, z_grid, size_x, size_y, size_z, color, cam_x, cam_y):
    p1 = to_screen(x_grid, y_grid, z_grid + size_z)
    p2 = to_screen(x_grid + size_x, y_grid, z_grid + size_z)
    p3 = to_screen(x_grid + size_x, y_grid + size_y, z_grid + size_z)
    p4 = to_screen(x_grid, y_grid + size_y, z_grid + size_z)
    p5 = to_screen(x_grid + size_x, y_grid + size_y, z_grid) 
    p6 = to_screen(x_grid + size_x, y_grid, z_grid)          
    p7 = to_screen(x_grid, y_grid + size_y, z_grid)          

    pts = [(px + cam_x, py + cam_y) for px, py in [p1, p2, p3, p4, p5, p6, p7]]
    
    c_top = color
    c_right = [max(0, int(c * 0.70)) for c in color] 
    c_left = [max(0, int(c * 0.85)) for c in color]  

    pygame.draw.polygon(surface, c_right, [pts[1], pts[2], pts[4], pts[5]])
    pygame.draw.polygon(surface, c_left, [pts[3], pts[2], pts[4], pts[6]])
    pygame.draw.polygon(surface, c_top, [pts[0], pts[1], pts[2], pts[3]])

# --- Game Objects ---

class Coin:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.active = True
        self.rot = 0

    def draw(self, surface, cam_x, cam_y):
        self.rot += 0.1
        bounce = math.sin(self.rot) * 2 + 5
        draw_block(surface, self.x + 0.35, self.y + 0.2, bounce, 0.3, 0.6, 1.5, COLOR_COIN, cam_x, cam_y)
        draw_block(surface, self.x + 0.2, self.y + 0.35, bounce, 0.6, 0.3, 1.5, COLOR_COIN, cam_x, cam_y)
        draw_block(surface, self.x + 0.4, self.y + 0.4, bounce + 0.5, 0.2, 0.2, 1, (200, 0, 0), cam_x, cam_y)

class Object:
    def __init__(self, x, lane_y, speed, type_name):
        self.x, self.lane_y, self.speed, self.type = x, lane_y, speed, type_name
        self.active = True
        
    def update(self):
        self.x += self.speed
        if abs(self.x) > 60: self.active = False

    def draw(self, surface, cam_x, cam_y):
        if self.type == "tree":
            draw_block(surface, self.x + 0.3, self.lane_y + 0.3, 0, 0.4, 0.4, 6, (90, 60, 30), cam_x, cam_y)
            draw_block(surface, self.x + 0.1, self.lane_y + 0.1, 6, 0.8, 0.8, 12, (100, 180, 40), cam_x, cam_y)
        elif self.type == "stone":
            draw_block(surface, self.x + 0.1, self.lane_y + 0.1, 0, 0.8, 0.8, 6, COLOR_STONE, cam_x, cam_y)
            draw_block(surface, self.x + 0.2, self.lane_y + 0.2, 6, 0.6, 0.6, 3, (180, 180, 180), cam_x, cam_y)
        elif self.type == "car":
            color = (230, 80, 80) if abs(self.lane_y) % 2 == 0 else (120, 175, 55)
            for ox, oy in [(0.2, 0.1), (1.1, 0.1), (0.2, 0.7), (1.1, 0.7)]:
                draw_block(surface, self.x + ox, self.lane_y + oy, 0, 0.3, 0.2, 4, (30,30,30), cam_x, cam_y)
            draw_block(surface, self.x, self.lane_y + 0.1, 3, 1.6, 0.8, 7, color, cam_x, cam_y)
            draw_block(surface, self.x + 0.3, self.lane_y + 0.15, 10, 1.0, 0.7, 6, (240, 245, 255), cam_x, cam_y)
        elif self.type == "log":
            draw_block(surface, self.x, self.lane_y + 0.1, -2, 3.5, 0.8, 4, (110, 70, 40), cam_x, cam_y)
        elif self.type == "train":
            # Train Body
            draw_block(surface, self.x, self.lane_y, 0, 15, 1, 14, COLOR_TRAIN_BODY, cam_x, cam_y)
            # Roof
            draw_block(surface, self.x, self.lane_y + 0.05, 14, 15, 0.9, 2, COLOR_TRAIN_ROOF, cam_x, cam_y)
            # Windows/Stripe
            draw_block(surface, self.x, self.lane_y - 0.05, 10, 15, 1.1, 3, (220, 220, 255), cam_x, cam_y)

class Lane:
    def __init__(self, y_index, type_id):
        self.y, self.type, self.objects = y_index, type_id, []
        self.direction = 1 if random.random() > 0.5 else -1
        self.speed = random.uniform(0.06, 0.14)
        self.timer = 0
        self.coin = None
        self.train_warning = False
        self.train_timer = 0
        
        if self.type == 'grass':
            for x in range(-12, 13):
                if random.random() < 0.2 and abs(x) > 1:
                    obj_type = "stone" if random.random() > 0.6 else "tree"
                    self.objects.append(Object(x, self.y, 0, obj_type))
            if random.random() < 0.1: self.coin = Coin(random.randint(-5, 5), self.y)
        elif self.type == 'road' or self.type == 'water':
            if random.random() < 0.1: self.coin = Coin(random.randint(-5, 5), self.y)
        elif self.type == 'rail':
             self.train_timer = random.randint(0, 200) # Offset start times

    def update(self):
        for obj in self.objects: obj.update()
        self.objects = [o for o in self.objects if o.active]
        
        self.timer += 1
        
        if self.type == 'road' and self.timer > 140:
            self.objects.append(Object(-25 if self.direction == 1 else 25, self.y, self.speed * self.direction, "car"))
            self.timer = 0
        elif self.type == 'water' and self.timer > 90: # Wooden blocks come more often (was 180)
            self.objects.append(Object(-30 if self.direction == 1 else 30, self.y, self.speed * self.direction, "log"))
            self.timer = 0
        elif self.type == 'rail':
            self.train_timer += 1
            # Warning Phase
            if self.train_timer > 400:
                self.train_warning = True
            # Spawn Phase
            if self.train_timer > 460:
                self.objects.append(Object(-50, self.y, 1.8, "train")) # Fast speed
                self.train_timer = 0
                self.train_warning = False

    def draw_terrain(self, surface, cam_x, cam_y):
        p1, p2, p3, p4 = to_screen(-35, self.y), to_screen(35, self.y), to_screen(35, self.y + 1), to_screen(-35, self.y + 1)
        poly = [(px + cam_x, py + cam_y) for px, py in [p1, p2, p3, p4]]
        
        color = COLOR_ROAD if self.type == 'road' else COLOR_WATER if self.type == 'water' else COLOR_RAIL if self.type == 'rail' else \
                (COLOR_GRASS_DARK if self.y % 2 == 0 else COLOR_GRASS_LIGHT)
        pygame.draw.polygon(surface, color, poly)
        
        if self.type == 'rail':
            # Draw Sleepers (Wood)
            for x in range(-15, 16, 2):
                draw_block(surface, x, self.y + 0.1, 0, 0.6, 0.8, 1, COLOR_RAIL_WOOD, cam_x, cam_y)
            # Draw Rails (Metal lines)
            # Use draw_block for rails to match depth style, just very long blocks
            draw_block(surface, -35, self.y + 0.2, 1, 70, 0.1, 1, COLOR_RAIL_METAL, cam_x, cam_y)
            draw_block(surface, -35, self.y + 0.7, 1, 70, 0.1, 1, COLOR_RAIL_METAL, cam_x, cam_y)
            
            # Warning Signal Light
            if self.train_warning:
                # Flashing logic
                is_on = (pygame.time.get_ticks() // 150) % 2 == 0
                light_c = COLOR_SIGNAL_LIGHT_ON if is_on else COLOR_SIGNAL_LIGHT_OFF
                
                # Pole
                draw_block(surface, -5, self.y - 0.2, 0, 0.2, 0.2, 10, COLOR_SIGNAL_POLE, cam_x, cam_y)
                # Box
                draw_block(surface, -5.1, self.y - 0.3, 10, 0.4, 0.4, 2, COLOR_SIGNAL_POLE, cam_x, cam_y)
                # Light
                draw_block(surface, -5.15, self.y - 0.35, 10.5, 0.5, 0.1, 1, light_c, cam_x, cam_y)

# --- Main Game Engine ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 48, bold=True)
        self.reset()

    def reset(self):
        self.lanes = {i: Lane(i, 'grass' if i < 3 else random.choice(['grass', 'road', 'water', 'rail'])) for i in range(-5, 30)}
        self.px, self.py, self.pz = 0, 0, 0
        self.tx, self.ty = 0, 0
        self.is_moving, self.jump_anim = False, 0
        self.score = 0
        self.coins_collected = 0
        self.cam_x, self.cam_y = SCREEN_WIDTH//2, SCREEN_HEIGHT//4
        self.game_over = False

    def draw_pixel_text(self, text, color, x, y, align="left"):
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
        surf = self.font.render(text, True, (0, 0, 0))
        rect = surf.get_rect()
        if align == "right": rect.topright = (x, y)
        else: rect.topleft = (x, y)
        
        for off in offsets:
            self.screen.blit(surf, (rect.x + off[0], rect.y + off[1]))
        
        main_surf = self.font.render(text, True, color)
        self.screen.blit(main_surf, rect)
        return rect

    def update(self):
        if self.game_over:
            if pygame.key.get_pressed()[pygame.K_SPACE]: self.reset()
            return

        keys = pygame.key.get_pressed()
        
        if not self.is_moving:
            dx, dy = 0, 0
            if keys[pygame.K_RIGHT]: dx = 1
            elif keys[pygame.K_LEFT]: dx = -1
            elif keys[pygame.K_UP]: dy = 1
            elif keys[pygame.K_DOWN]: dy = -1
            
            if dx != 0 or dy != 0:
                target_lane = self.lanes.get(self.py + dy)
                blocked = False
                if target_lane:
                    for obj in target_lane.objects:
                        if obj.type in ["tree", "stone"] and round(obj.x) == round(self.px + dx):
                            blocked = True
                if not blocked:
                    self.tx, self.ty, self.is_moving = self.px + dx, self.py + dy, True

        else:
            self.jump_anim += 0.2
            if self.jump_anim >= 1:
                self.px, self.py, self.is_moving, self.jump_anim = self.tx, self.ty, False, 0
                if self.py > self.score: self.score = self.py
            self.pz = math.sin(self.jump_anim * math.pi) * 10

        current_lane = self.lanes.get(self.py)
        if current_lane and current_lane.type == 'water' and not self.is_moving:
            on_log = False
            for obj in current_lane.objects:
                if obj.type == "log" and obj.x <= self.px <= obj.x + 3.5:
                    self.px += obj.speed 
                    on_log = True
                    break
            if not on_log or abs(self.px) > 15: self.game_over = True

        if current_lane and not self.is_moving:
            for obj in current_lane.objects:
                # Car collision
                if obj.type == "car" and obj.x - 0.5 <= self.px <= obj.x + 1.5:
                    self.game_over = True
                # Train collision (Longer hitbox)
                if obj.type == "train" and obj.x - 0.5 <= self.px <= obj.x + 15:
                    self.game_over = True

        if current_lane and current_lane.coin and not self.is_moving:
            if abs(current_lane.coin.x - self.px) < 0.8:
                self.coins_collected += 1
                current_lane.coin = None

        for i in range(int(self.py) - 10, int(self.py) + 20):
            if i not in self.lanes: 
                self.lanes[i] = Lane(i, random.choice(['grass', 'road', 'water', 'rail']))
            self.lanes[i].update()
        
        vpx = self.px + (self.tx-self.px)*self.jump_anim if self.is_moving else self.px
        vpy = self.py + (self.ty-self.py)*self.jump_anim if self.is_moving else self.py
        spx, spy = to_screen(vpx, vpy)
        self.cam_x += (SCREEN_WIDTH//2 - spx - self.cam_x) * 0.1
        self.cam_y += (SCREEN_HEIGHT//2 - spy + 150 - self.cam_y) * 0.1

    def draw(self):
        self.screen.fill(COLOR_BG)
        render_list = []
        vpx = self.px + (self.tx-self.px)*self.jump_anim if self.is_moving else self.px
        vpy = self.py + (self.ty-self.py)*self.jump_anim if self.is_moving else self.py
        
        for y in range(int(self.py) - 12, int(self.py) + 15):
            if y in self.lanes:
                lane = self.lanes[y]
                lane.draw_terrain(self.screen, self.cam_x, self.cam_y)
                if lane.coin: render_list.append(lane.coin)
                for obj in lane.objects: render_list.append(obj)

        render_list.append("PLAYER")
        def get_depth(item):
            if item == "PLAYER": return vpx + vpy
            return item.x + (item.lane_y if hasattr(item, 'lane_y') else item.y)
        render_list.sort(key=get_depth)

        for item in render_list:
            if item == "PLAYER": self.draw_player(vpx, vpy)
            else: item.draw(self.screen, self.cam_x, self.cam_y)
                
        self.draw_pixel_text(str(self.score), (255, 255, 255), 20, 20)
        coin_rect = self.draw_pixel_text(str(self.coins_collected), (255, 220, 0), SCREEN_WIDTH - 80, 20, align="right")
        ui_coin_x = coin_rect.right + 15
        ui_coin_y = coin_rect.centery
        pygame.draw.circle(self.screen, (0, 0, 0), (ui_coin_x, ui_coin_y), 18)
        pygame.draw.circle(self.screen, COLOR_COIN, (ui_coin_x, ui_coin_y), 15)
        c_font = pygame.font.SysFont("Courier", 20, bold=True)
        c_surf = c_font.render("C", True, (200, 0, 0))
        self.screen.blit(c_surf, c_surf.get_rect(center=(ui_coin_x, ui_coin_y)))

        if self.game_over:
            over_rect = self.draw_pixel_text("GAME OVER", (255, 50, 50), SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)
            over_rect.centerx = SCREEN_WIDTH//2

        pygame.display.flip()

    def draw_player(self, vpx, vpy):
        sx, sy = to_screen(vpx, vpy)
        shadow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, COLOR_SHADOW, (sx + self.cam_x - 15, sy + self.cam_y - 5, 30, 15))
        self.screen.blit(shadow, (0,0))
        draw_block(self.screen, vpx+0.2, vpy+0.2, self.pz, 0.6, 0.6, 12, COLOR_CHICKEN, self.cam_x, self.cam_y)
        draw_block(self.screen, vpx+0.4, vpy+0.35, self.pz+12, 0.2, 0.3, 4, COLOR_CHICKEN_COMB, self.cam_x, self.cam_y)
        draw_block(self.screen, vpx+0.75, vpy+0.4, self.pz+8, 0.15, 0.2, 3, COLOR_CHICKEN_BEAK, self.cam_x, self.cam_y)

if __name__ == "__main__":
    game = Game()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        game.update(); game.draw(); game.clock.tick(FPS)