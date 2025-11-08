# game.py
import pygame
import random
import sys

# Инициализация
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("InuCatch")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 20)

# Игровые параметры
PLAYER_W, PLAYER_H = 80, 16
PLAYER_SPEED = 6
ITEM_SIZE = 28
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 700)  # появление предметов каждые 700 ms

# Цвета
BG = (30, 30, 40)
PLAYER_COLOR = (200, 200, 255)
TREASURE_COLOR = (255, 215, 0)  # золото
BOMB_COLOR = (200, 50, 50)
TEXT_COLOR = (230, 230, 230)

# Игрок (корзинка)
player_rect = pygame.Rect((WIDTH - PLAYER_W)//2, HEIGHT - 60, PLAYER_W, PLAYER_H)

# Состояние
items = []  # каждый item: dict {rect, type, speed}
score = 0
lives = 3
level = 1
game_over = False

def spawn_item():
    x = random.randint(10, WIDTH - ITEM_SIZE - 10)
    rect = pygame.Rect(x, -ITEM_SIZE, ITEM_SIZE, ITEM_SIZE)
    # вероятности: 75% сокровище, 25% бомба
    t = "treasure" if random.random() < 0.75 else "bomb"
    speed = random.uniform(2 + level*0.3, 4 + level*0.6)
    items.append({"rect": rect, "type": t, "speed": speed})

def draw_text(surf, text, x, y):
    img = FONT.render(text, True, TEXT_COLOR)
    surf.blit(img, (x, y))

def reset_game():
    global items, score, lives, level, game_over
    items = []
    score = 0
    lives = 3
    level = 1
    game_over = False

# Основной цикл
while True:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SPAWN_EVENT and not game_over:
            spawn_item()
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += PLAYER_SPEED
        # Ограничение по экрану
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > WIDTH:
            player_rect.right = WIDTH

    # Обновление предметов
    for it in items[:]:
        it["rect"].y += it["speed"]
        # если упал вниз — удалить
        if it["rect"].top > HEIGHT:
            items.remove(it)

        # Проверка столкновения
        if it["rect"].colliderect(player_rect) and not game_over:
            if it["type"] == "treasure":
                score += 10
            else:
                lives -= 1
            try:
                items.remove(it)
            except ValueError:
                pass

    # Уровни: увеличиваем сложность с ростом очков
    if score >= level * 100:
        level += 1
        # ускоряем генерацию: уменьшаем таймер
        new_interval = max(250, 700 - (level - 1) * 60)
        pygame.time.set_timer(SPAWN_EVENT, new_interval)

    if lives <= 0:
        game_over = True

    # Рендеринг
    screen.fill(BG)
    # игрок
    pygame.draw.rect(screen, PLAYER_COLOR, player_rect, border_radius=6)
    # предметы
    for it in items:
        color = TREASURE_COLOR if it["type"] == "treasure" else BOMB_COLOR
        pygame.draw.rect(screen, color, it["rect"], border_radius=6)
        # маленькая иконка внутри
        inner = it["rect"].inflate(-8, -8)
        if it["type"] == "treasure":
            pygame.draw.circle(screen, (255, 240, 120), inner.center, inner.width//4)
        else:
            pygame.draw.line(screen, (255, 180, 180), inner.topleft, inner.bottomright, 2)
            pygame.draw.line(screen, (255, 180, 180), inner.topright, inner.bottomleft, 2)

    # HUD
    draw_text(screen, f"Score: {score}", 10, 8)
    draw_text(screen, f"Lives: {lives}", 10, 34)
    draw_text(screen, f"Level: {level}", WIDTH - 120, 8)
    draw_text(screen, "Left/Right or A/D — move. R — restart (after death)", 120, HEIGHT - 30)

    if game_over:
        over_font = pygame.font.SysFont("arial", 36)
        ov = over_font.render("GAME OVER", True, (255, 100, 100))
        screen.blit(ov, ((WIDTH - ov.get_width())//2, HEIGHT//2 - 30))
        sub = FONT.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(sub, ((WIDTH - sub.get_width())//2, HEIGHT//2 + 12))

    pygame.display.flip()
