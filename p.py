import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)  # Sky blue
GRAY = (128, 128, 128)  # Sidewalk
DARK_GRAY = (64, 64, 64)  # Buildings
GREEN = (34, 139, 34)  # Trees
PINK = (255, 192, 203)  # Cheryl
ORANGE = (255, 165, 0)  # Cats
BROWN = (139, 69, 19)  # Raccoons
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Hearts

class Player:
    def __init__(self):
        self.x = 100
        self.y = 400
        self.width = 30
        self.height = 40
        self.speed = 5
        self.world_x = 0  # Position in the infinite world
        
        # Try to load cheryl.png, fallback to rectangle if not found
        try:
            self.image = pygame.image.load("cheryl.png")
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.has_image = True
        except:
            self.has_image = False
            print("Could not load cheryl.png, using simple rectangle instead")
        
    def update(self):
        keys = pygame.key.get_pressed()
        old_x = self.x
        
        if keys[pygame.K_LEFT] and self.world_x > 0:
            if self.x > SCREEN_WIDTH // 3:
                self.x -= self.speed
            else:
                self.world_x -= self.speed
        if keys[pygame.K_RIGHT]:
            if self.x < SCREEN_WIDTH * 2 // 3:
                self.x += self.speed
            else:
                self.world_x += self.speed
        if keys[pygame.K_UP] and self.y > 300:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < 450:
            self.y += self.speed
    
    def draw(self, screen):
        if self.has_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback: Draw Cheryl as a pink rectangle
            pygame.draw.rect(screen, PINK, (self.x, self.y, self.width, self.height))
            # Add a simple face
            pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 10), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 20, self.y + 10), 2)
            # Simple expression
            pygame.draw.arc(screen, BLACK, (self.x + 12, self.y + 12, 10, 8), 0, 3.14, 1)

class Cat:
    def __init__(self, world_x, y, on_balcony=False):
        self.world_x = world_x
        self.y = y
        self.width = 20
        self.height = 15
        self.on_balcony = on_balcony
        self.cooldown = 0  # Cooldown after being touched
        
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            
    def get_screen_x(self, camera_x):
        return self.world_x - camera_x
        
    def draw(self, screen, camera_x):
        screen_x = self.get_screen_x(camera_x)
        if -50 < screen_x < SCREEN_WIDTH + 50:  # Only draw if on screen
            # Draw cat as orange rectangle with ears
            color = ORANGE # if self.cooldown == 0 else (255, 200, 150)  # Lighter when in cooldown
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
            # Ears
            pygame.draw.polygon(screen, color, [(screen_x + 3, self.y), (screen_x + 7, self.y - 5), (screen_x + 10, self.y)])
            pygame.draw.polygon(screen, color, [(screen_x + 12, self.y), (screen_x + 15, self.y - 5), (screen_x + 18, self.y)])
            # Eyes
            pygame.draw.circle(screen, BLACK, (screen_x + 6, self.y + 5), 1)
            pygame.draw.circle(screen, BLACK, (screen_x + 14, self.y + 5), 1)

class Raccoon:
    def __init__(self, world_x, y):
        self.world_x = world_x
        self.y = y
        self.width = 25
        self.height = 20
        self.cooldown = 0
        
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            
    def get_screen_x(self, camera_x):
        return self.world_x - camera_x
        
    def draw(self, screen, camera_x):
        screen_x = self.get_screen_x(camera_x)
        if -50 < screen_x < SCREEN_WIDTH + 50:  # Only draw if on screen
            # Draw raccoon as brown rectangle
            color = BROWN if self.cooldown == 0 else (100, 50, 15)  # Darker when in cooldown
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
            # Mask-like face
            pygame.draw.ellipse(screen, BLACK, (screen_x + 5, self.y + 3, 15, 8))
            pygame.draw.ellipse(screen, WHITE, (screen_x + 7, self.y + 5, 4, 3))
            pygame.draw.ellipse(screen, WHITE, (screen_x + 14, self.y + 5, 4, 3))
            # Eyes
            pygame.draw.circle(screen, BLACK, (screen_x + 9, self.y + 6), 1)
            pygame.draw.circle(screen, BLACK, (screen_x + 16, self.y + 6), 1)

class Heart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.lifetime = 60  # Frames to live
        
    def update(self):
        self.y -= 2  # Float upward
        self.lifetime -= 1
        
    def draw(self, screen):
        if self.lifetime > 0:
            # Draw a simple heart shape
            pygame.draw.circle(screen, RED, (self.x - 3, self.y - 2), 4)
            pygame.draw.circle(screen, RED, (self.x + 3, self.y - 2), 4)
            pygame.draw.polygon(screen, RED, [(self.x - 6, self.y), (self.x, self.y + 8), (self.x + 6, self.y)])

class Building:
    def __init__(self, world_x, width, height):
        self.world_x = world_x
        self.width = width
        self.height = height
        self.windows = []
        # Generate random windows - fix window positioning
        ground_y = 380  # Top of sidewalk
        building_y = ground_y - height
        
        rows = max(1, height // 60)  # More realistic window spacing
        cols = max(1, width // 45)
        
        for row in range(rows):
            for col in range(cols):
                if random.random() > 0.3:  # Some windows are dark
                    window_x = world_x + 15 + col * 40
                    window_y = building_y + 20 + row * 50  # Relative to building top
                    # Make sure window is within building bounds
                    if (window_x + 20 < world_x + width - 15 and 
                        window_y + 25 < building_y + height - 15):
                        self.windows.append((window_x, window_y))
    
    def draw(self, screen, camera_x):
        screen_x = self.world_x - camera_x
        if screen_x < SCREEN_WIDTH + 100 and screen_x + self.width > -100:
            # Draw building 
            ground_y = 380  # Top of sidewalk
            building_y = ground_y - self.height
            pygame.draw.rect(screen, DARK_GRAY, (screen_x, building_y, self.width, self.height))
            # Draw windows
            for window_x, window_y in self.windows:
                window_screen_x = window_x - camera_x
                if -50 < window_screen_x < SCREEN_WIDTH + 50:
                    # Adjust window Y position relative to building base
                    adjusted_window_y = building_y + (window_y - 70)
                    color = WHITE if random.random() > 0.1 else (255, 255, 150)
                    pygame.draw.rect(screen, color, (window_screen_x, adjusted_window_y, 20, 25))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cheryl's Cat Adventure")
        self.clock = pygame.time.Clock()
        self.state = "START"  # START, PLAYING, GAME_OVER
        self.start_time = 0  # For animations
        self.floating_cats = []  # Animated cats on start screen
        self.stars = []  # Background stars
        self.reset_game()
        self.init_start_screen_effects()
        
    def reset_game(self):
        self.player = Player()
        self.cats = []
        self.raccoons = []
        self.hearts = []
        self.buildings = []
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.spawn_timer = 0
        self.last_spawn_x = 0
        
        # Generate initial world
        self.generate_world(0, 2000)
    
    def init_start_screen_effects(self):
        # Create floating cats for start screen
        self.floating_cats = []
        for i in range(8):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(200, 500)
            speed = random.uniform(0.5, 2.0)
            direction = random.uniform(0, 6.28)  # Random direction in radians
            self.floating_cats.append({
                'x': x, 'y': y, 'speed': speed, 'direction': direction,
                'bob_offset': random.uniform(0, 6.28), 'size': random.uniform(0.8, 1.5)
            })
        
        # Create background stars
        self.stars = []
        for i in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, 300)
            brightness = random.randint(100, 255)
            twinkle_speed = random.uniform(0.05, 0.15)
            self.stars.append({'x': x, 'y': y, 'brightness': brightness, 'twinkle_speed': twinkle_speed})
    
    def draw_gradient_background(self, color1, color2):
        # Create a vertical gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def generate_world(self, start_x, end_x):
        # Generate buildings
        current_x = start_x
        while current_x < end_x:
            width = random.randint(100, 200)
            height = random.randint(150, 250)
            self.buildings.append(Building(current_x, width, height))
            current_x += width + random.randint(20, 50)
        
        # Generate cats and raccoons
        for x in range(start_x, end_x, 100):
            # Cats on sidewalk
            if random.random() < 0.3:
                y = random.randint(420, 470)
                self.cats.append(Cat(x + random.randint(0, 80), y, False))
            
            # Cats on balconies
            if random.random() < 0.2:
                y = random.randint(250, 320)
                self.cats.append(Cat(x + random.randint(0, 80), y, True))
            
            # Raccoons
            if random.random() < 0.15:
                y = random.randint(410, 460)
                self.raccoons.append(Raccoon(x + random.randint(0, 80), y))
    
    def check_collisions(self):
        player_world_rect = pygame.Rect(self.player.world_x + self.player.x - 100, 
                                       self.player.y, self.player.width, self.player.height)
        
        # Check cat collisions
        for cat in self.cats:
            if cat.cooldown == 0:
                cat_rect = pygame.Rect(cat.world_x, cat.y, cat.width, cat.height)
                if player_world_rect.colliderect(cat_rect):
                    cat.cooldown = 120  # 2 seconds at 60 FPS
                    self.score += 10
                    # Create heart effect
                    heart_x = cat.get_screen_x(self.player.world_x) + cat.width // 2
                    self.hearts.append(Heart(heart_x, cat.y - 10))
        
        # Check raccoon collisions
        for raccoon in self.raccoons:
            if raccoon.cooldown == 0:
                raccoon_rect = pygame.Rect(raccoon.world_x, raccoon.y, raccoon.width, raccoon.height)
                if player_world_rect.colliderect(raccoon_rect):
                    raccoon.cooldown = 120  # 2 seconds at 60 FPS
                    self.score = max(0, self.score - 5)  # Don't go below 0
    
    def draw_background(self, camera_x):
        # Sky
        self.screen.fill(BLUE)
        
        # Draw buildings
        for building in self.buildings:
            building.draw(self.screen, camera_x)
        
        # Sidewalk
        pygame.draw.rect(self.screen, GRAY, (0, 380, SCREEN_WIDTH, 120))
        
        # Road
        pygame.draw.rect(self.screen, BLACK, (0, 500, SCREEN_WIDTH, 100))
        
        # Road lines (moving with camera)
        line_offset = int(camera_x % 60)
        for i in range(-line_offset, SCREEN_WIDTH + 60, 60):
            pygame.draw.rect(self.screen, WHITE, (i, 545, 30, 5))
    
    def draw_start_screen(self):
        # Animated gradient background
        self.start_time += 1
        color_shift = abs(int(20 * pygame.math.Vector2(1, 0).rotate(self.start_time * 2).x))
        sky_color = (135 + color_shift, 206, 235)
        sunset_color = (255, 180 + color_shift // 2, 100)
        self.draw_gradient_background(sky_color, sunset_color)
        
        # Animated twinkling stars
        for star in self.stars:
            brightness_shift = int(50 * abs(pygame.math.Vector2(1, 0).rotate(self.start_time * star['twinkle_speed']).x))
            brightness = min(255, star['brightness'] + brightness_shift)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (star['x'], star['y']), random.randint(1, 2))
        
        # Floating animated cats
        for cat in self.floating_cats:
            # Update cat position
            cat['x'] += pygame.math.Vector2(cat['speed'], 0).rotate(cat['direction']).x * 0.5
            cat['y'] += pygame.math.Vector2(cat['speed'], 0).rotate(cat['direction']).y * 0.3
            
            # Add bobbing motion
            bob = 3 * pygame.math.Vector2(1, 0).rotate(self.start_time * 0.1 + cat['bob_offset']).y
            cat['y'] += bob * 0.1
            
            # Wrap around screen
            if cat['x'] < -30: cat['x'] = SCREEN_WIDTH + 30
            if cat['x'] > SCREEN_WIDTH + 30: cat['x'] = -30
            if cat['y'] < -30: cat['y'] = SCREEN_HEIGHT + 30
            if cat['y'] > SCREEN_HEIGHT + 30: cat['y'] = -30
            
            # Draw floating cat with size variation
            size = int(20 * cat['size'])
            glow_size = int(size * 1.2)
            
            # Glow effect
            glow_color = (255, 200, 100, 50)
            pygame.draw.circle(self.screen, (255, 200, 100), (int(cat['x']), int(cat['y'])), glow_size)
            
            # Cat body
            pygame.draw.rect(self.screen, ORANGE, 
                           (int(cat['x'] - size//2), int(cat['y'] - size//2), size, int(size*0.75)))
            # Ears
            ear_size = size // 3
            pygame.draw.polygon(self.screen, ORANGE, [
                (int(cat['x'] - size//3), int(cat['y'] - size//2)),
                (int(cat['x'] - size//6), int(cat['y'] - size//2 - ear_size)),
                (int(cat['x']), int(cat['y'] - size//2))
            ])
            pygame.draw.polygon(self.screen, ORANGE, [
                (int(cat['x']), int(cat['y'] - size//2)),
                (int(cat['x'] + size//6), int(cat['y'] - size//2 - ear_size)),
                (int(cat['x'] + size//3), int(cat['y'] - size//2))
            ])
        
        # Animated title with glow effect
        title_bounce = 5 * abs(pygame.math.Vector2(1, 0).rotate(self.start_time * 0.05).y)
        title_y = 120 + title_bounce
        
        # Title glow
        for offset in range(5, 0, -1):
            glow_alpha = 255 - offset * 40
            title_glow = self.big_font.render("Cheryl's Cat Adventure", True, (255, 255, 150))
            for dx, dy in [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)]:
                self.screen.blit(title_glow, (SCREEN_WIDTH//2 - title_glow.get_width()//2 + dx, title_y + dy))
        
        # Main title
        title = self.big_font.render("Cheryl's Cat Adventure", True, (50, 50, 150))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title, title_rect)
        
        # Animated instruction panel with transparency effect
        panel_alpha = 200 + int(30 * pygame.math.Vector2(1, 0).rotate(self.start_time * 0.03).x)
        panel_surface = pygame.Surface((600, 350))
        panel_surface.set_alpha(panel_alpha)
        panel_surface.fill((20, 20, 40))
        panel_rect = panel_surface.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(panel_surface, panel_rect)
        
        # Instructions with color animations
        instructions = [
            "Help Cheryl collect cats and avoid raccoons!",
            "",
            "CONTROLS:",
            "Arrow Keys - Move Cheryl",
            "Up/Down - Jump to balconies/return to sidewalk",
            "",
            "SCORING:",
            "Cats: +10 points (hearts will appear!)",
            "Raccoons: -5 points",
            "",
            "Press SPACE to start!",
            "Press ESC to quit"
        ]
        
        y = 250
        for i, instruction in enumerate(instructions):
            if instruction == "":
                y += 15
            else:
                # Color cycling for text
                color_cycle = int(50 * abs(pygame.math.Vector2(1, 0).rotate(self.start_time * 0.02 + i * 0.5).x))
                
                if instruction.startswith("CONTROLS:") or instruction.startswith("SCORING:"):
                    color = (255, 200 + color_cycle, 100)
                    text = self.font.render(instruction, True, color)
                elif instruction == "Press SPACE to start!":
                    # Pulsing start instruction
                    pulse = int(100 * abs(pygame.math.Vector2(1, 0).rotate(self.start_time * 0.1).x))
                    color = (255, 150 + pulse, 150 + pulse)
                    text = self.font.render(instruction, True, color)
                else:
                    color = (200 + color_cycle, 200 + color_cycle, 255)
                    text = self.font.render(instruction, True, color)
                
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
                y += 30
        
        # Floating hearts animation
        for i in range(5):
            heart_x = 100 + i * 200 + 30 * pygame.math.Vector2(1, 0).rotate(self.start_time * 0.02 + i).x
            heart_y = 500 + 20 * pygame.math.Vector2(1, 0).rotate(self.start_time * 0.03 + i * 2).y
            
            # Draw hearts
            pygame.draw.circle(self.screen, RED, (int(heart_x - 3), int(heart_y - 2)), 4)
            pygame.draw.circle(self.screen, RED, (int(heart_x + 3), int(heart_y - 2)), 4)
            pygame.draw.polygon(self.screen, RED, [
                (int(heart_x - 6), int(heart_y)), 
                (int(heart_x), int(heart_y + 8)), 
                (int(heart_x + 6), int(heart_y))
            ])
    
    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        distance_text = self.font.render(f"Distance: {int(self.player.world_x / 10)}m", True, BLACK)
        self.screen.blit(distance_text, (10, 50))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.state == "START":
                        self.state = "PLAYING"
                        self.reset_game()
                    elif event.key == pygame.K_r and self.state == "PLAYING":
                        self.reset_game()
            
            if self.state == "START":
                self.draw_start_screen()
            elif self.state == "PLAYING":
                # Update
                self.player.update()
                
                # Generate more world as player progresses
                if self.player.world_x > self.last_spawn_x - 1000:
                    self.generate_world(self.last_spawn_x, self.last_spawn_x + 2000)
                    self.last_spawn_x += 2000
                
                # Update cats and raccoons
                for cat in self.cats:
                    cat.update()
                for raccoon in self.raccoons:
                    raccoon.update()
                
                # Update hearts
                for heart in self.hearts[:]:
                    heart.update()
                    if heart.lifetime <= 0:
                        self.hearts.remove(heart)
                
                self.check_collisions()
                
                # Draw
                camera_x = self.player.world_x
                self.draw_background(camera_x)
                
                for cat in self.cats:
                    cat.draw(self.screen, camera_x)
                
                for raccoon in self.raccoons:
                    raccoon.draw(self.screen, camera_x)
                
                for heart in self.hearts:
                    heart.draw(self.screen)
                
                self.player.draw(self.screen)
                self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()