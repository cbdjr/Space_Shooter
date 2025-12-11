import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter with Power-Ups")

clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 20)
PURPLE = (200, 50, 200)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
BLUE = (0, 100, 255)

font = pygame.font.SysFont("Arial", 30)

PLAYER_LIVES = 3
BOSS_TRIGGER_SCORE = 20
BOSS_HEALTH = 20


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("ufo.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.speed = 5
        self.lives = PLAYER_LIVES

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=-8, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), -40))
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 60))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.speed = 4
        self.health = BOSS_HEALTH
        self.direction = 1
        self.shoot_timer = 0

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

        self.shoot_timer += 1
        if self.shoot_timer >= 60:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, speed=6, color=YELLOW)
            boss_bullets.add(bullet)
            self.shoot_timer = 0


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, pos):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        color = {'rapid': BLUE, 'shield': GREEN, 'triple': ORANGE}[kind]
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


def draw_text(text, x, y, color=WHITE):
    screen.blit(font.render(text, True, color), (x, y))


def reset_game():
    global player, player_group, bullets, enemies, boss, boss_spawned, score
    global shoot_timer, win, game_over, boss_bullets, powerups
    global powerup_timer, shield_active
    global boss_group

    player = Player()
    player_group = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    powerup_timer = {'rapid': 0, 'triple': 0}
    shield_active = False

    score = 0
    shoot_timer = 0
    boss_spawned = False
    win = False
    game_over = False
    boss = None


reset_game()

running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over and not win:
        player.update(keys)

        now = pygame.time.get_ticks()
        for key in ['rapid', 'triple']:
            if powerup_timer[key] and now - powerup_timer[key] > 8000:
                powerup_timer[key] = 0

        fire_delay = 5 if powerup_timer['rapid'] > 0 else 15
        shoot_timer += 1
        if shoot_timer >= fire_delay:
            shoot_timer = 0
            if powerup_timer['triple'] > 0:
                bullets.add(Bullet(player.rect.centerx, player.rect.top))
                bullets.add(Bullet(player.rect.centerx - 15, player.rect.top))
                bullets.add(Bullet(player.rect.centerx + 15, player.rect.top))
            else:
                bullets.add(Bullet(player.rect.centerx, player.rect.top))

        if not boss_spawned and random.randint(1, 40) == 1:
            enemies.add(Enemy())

        if random.randint(1, 400) == 1 and not boss_spawned:
            kind = random.choice(['rapid', 'shield', 'triple'])
            powerups.add(PowerUp(kind, (random.randint(30, WIDTH - 30), 0)))

        bullets.update()
        enemies.update()
        boss_bullets.update()
        powerups.update()

        for pu in pygame.sprite.spritecollide(player, powerups, True):
            if pu.kind == 'shield':
                shield_active = True
            else:
                powerup_timer[pu.kind] = pygame.time.get_ticks()

        if pygame.sprite.spritecollideany(player, enemies):
            if shield_active:
                shield_active = False
            else:
                player.lives -= 1
                enemies.empty()
                if player.lives <= 0:
                    game_over = True

        if boss_spawned:
            boss_group.update()
            if pygame.sprite.spritecollideany(player, boss_bullets):
                if shield_active:
                    shield_active = False
                else:
                    player.lives -= 1
                    boss_bullets.empty()
                    if player.lives <= 0:
                        game_over = True

            if boss.rect.colliderect(player.rect):
                if shield_active:
                    shield_active = False
                else:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True

            for bullet in bullets:
                if boss.rect.colliderect(bullet.rect):
                    bullet.kill()
                    boss.health -= 1
                    if boss.health <= 0:
                        win = True
                        boss.kill()

        if score >= BOSS_TRIGGER_SCORE and not boss_spawned:
            boss = Boss()
            boss_group.add(boss)
            enemies.empty()
            boss_spawned = True

        score += len(pygame.sprite.groupcollide(enemies, bullets, True, True))

        player_group.draw(screen)
        bullets.draw(screen)
        enemies.draw(screen)
        boss_group.draw(screen)
        boss_bullets.draw(screen)
        powerups.draw(screen)

        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"Lives: {player.lives}", 10, 40)
        if boss_spawned:
            draw_text(f"Boss HP: {boss.health}", 10, 70)
        if shield_active:
            pygame.draw.circle(screen, GREEN, player.rect.center, 40, 2)

    else:
        msg = "You Win!" if win else "Game Over"
        draw_text(msg, WIDTH // 2 - 80, HEIGHT // 2 - 40, GREEN if win else RED)
        draw_text("Press R to Restart", WIDTH // 2 - 120, HEIGHT // 2 + 10)
        if keys[pygame.K_r]:
            reset_game()

    pygame.display.flip()

pygame.quit()
sys.exit()



