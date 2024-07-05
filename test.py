import pygame
import random
import sqlite3

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eva_test")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Класс игрока (платформа)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

# Класс мяча
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.speed_x = random.choice([-3, 3])
        self.speed_y = -3

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y

# Класс блока
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((75, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс для работы с базой данных
class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            score INTEGER)''')
        self.conn.commit()

    def insert_score(self, name, score):
        self.cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
        self.conn.commit()

    def get_top_scores(self, limit=5):
        self.cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()

# Функция для отображения текста на экране
def draw_text(text, font_size, color, x, y):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    screen.blit(text_surface, text_rect)

# Функция для запроса имени пользователя
def get_player_name():
    name = ""
    font = pygame.font.Font(None, 36)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        screen.fill(BLACK)
        draw_text("Enter your name:", 36, WHITE, WIDTH // 2, HEIGHT // 2 - 50)
        text_surface = font.render(name, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT // 2)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()

# Инициализация игровых объектов
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
player = Player()
ball = Ball()
all_sprites.add(player, ball)

# Создание блоков
for i in range(10):
    for j in range(5):
        block = Block(i * 80, j * 30)
        all_sprites.add(block)
        blocks.add(block)

# Инициализация базы данных
db = Database("scores.db")

# Запрос имени пользователя
player_name = get_player_name()

# Игровой цикл
running = True
clock = pygame.time.Clock()
score = 0

while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление игровых объектов
    all_sprites.update()

    # Проверка столкновений мяча с платформой
    if pygame.sprite.collide_rect(ball, player):
        ball.speed_y = -ball.speed_y

    # Проверка столкновений мяча с блоками
    collided_blocks = pygame.sprite.spritecollide(ball, blocks, True)
    for block in collided_blocks:
        ball.speed_y = -ball.speed_y
        score += 1

    # Отрисовка
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(f"Score: {score}", 36, WHITE, WIDTH // 2, 10)
    pygame.display.flip()

    # Условие проигрыша
    if ball.rect.bottom >= HEIGHT:
        running = False

    clock.tick(60)

# Сохранение результата в базу данных
db.insert_score(player_name, score)

# Отображение топ-5 игроков
top_scores = db.get_top_scores()
screen.fill(BLACK)
draw_text("Game Over!", 48, WHITE, WIDTH // 2, HEIGHT // 2 - 100)
draw_text(f"Your Score: {score}", 36, WHITE, WIDTH // 2, HEIGHT // 2 - 50)
draw_text("Top 5 Players:", 36, WHITE, WIDTH // 2, HEIGHT // 2)
for i, (name, score) in enumerate(top_scores, start=1):
    draw_text(f"{i}. {name}: {score}", 24, WHITE, WIDTH // 2, HEIGHT // 2 + 30 * i)
pygame.display.flip()

# Ожидание закрытия окна
pygame.time.wait(5000)

# Завершение игры
pygame.quit()