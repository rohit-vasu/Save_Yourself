import pygame
import os
import time
import random
from pygame import mixer

pygame.init()
pygame.font.init()

# WINDOW SIZE

WIDTH, HEIGHT = 750, 640
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# WINDOW NAME AND ICON

pygame.display.set_caption("Save Yourself")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

# BACKGROUND MUSIC AND SOUNDS FX

BGMUSIC = mixer.music.load('Background music.mp3')
mixer.music.play(-1)
PISTOL = mixer.Sound('pistol gun.mp3')
GAME_OVER = mixer.Sound('game over.mp3')

# LOADING IMAGES

# PLAYER

PLAYER = pygame.image.load('player.png')

# ENEMY

ENEMY_1 = pygame.image.load('enemy.png')
ENEMY_2 = pygame.image.load('enemy2.png')
ENEMY_3 = pygame.image.load('enemy3.png')


# BULLETS

BULLET = pygame.image.load('bullet.png')
BULLET_SEMI = pygame.image.load('bullet (1).png')
BULLET_DUAL = pygame.image.load('bullet (2).png')

# BACKGROUND

BG = pygame.transform.scale(pygame.image.load('background.png'), (WIDTH, HEIGHT))
MM = pygame.transform.scale(pygame.image.load('mainmenu.png'), (WIDTH, HEIGHT))



# BULLET CLASS

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


# GENERAL PEOPLE CLASS

class People:
    CHILL = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = 100
        self.people_img = None
        self.bullet_img = None
        self.bullets = []
        self.chill_counter = 0

    def draw(self, window):
        window.blit(self.people_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    # BULLET MOVEMENTS

    def move_bullets(self, vel, obj):
        self.chill()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    # CHILLING COUNTER

    def chill(self):
        if self.chill_counter >= self.CHILL:
            self.chill_counter = 0
        if self.chill_counter > 0:
            self.chill_counter += 1

    # SHOOTING

    def shoot(self):
        if self.chill_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.chill_counter = 1

    def get_width(self):
        return self.people_img.get_width()

    def get_height(self):
        return self.people_img.get_height()


# PLAYER FROM PEOPLE CLASS

class Player(People):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.people_img = PLAYER
        self.bullet_img = BULLET
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.people_img)

    # PLAYER SHOOT

    def shoot(self):
        if self.chill_counter == 0:
            bullet = Bullet(self.x + 40, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.chill_counter = 1

    # PLAYER BULLET MOVEMENTS

    def move_bullets(self, vel, objs):
        self.chill()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    # HEALTH BAR FOR PLAYER

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x,
                          self.y + self.people_img.get_height() + 10, self.people_img.get_width(),
                          10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.people_img.get_height() + 10,
                          (self.people_img.get_width() * (self.health / 100)), 10))

# ENEMY CLASS

class Enemy(People):
    COLOR_MAP = {
        "enemy_1": (ENEMY_1, BULLET_SEMI),
        "enemy_2": (ENEMY_2, BULLET_DUAL),
        "enemy_3": (ENEMY_3, BULLET_SEMI)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.people_img, self.bullet_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.people_img)

    # ENEMY MOVEMENT

    def move(self, vel):
        self.y += vel

    # ENEMY SHOOT

    def shoot(self):
        if self.chill_counter == 0:
            bullet = Bullet(self.x + 5, self.y + 70, self.bullet_img)
            self.bullets.append(bullet)
            self.chill_counter = 1


# BULLET COLLISION

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None



# MAIN
def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1.2
    player_vel = 5

    player = Player(300, 575, 0)
    bullet_vel = 4

    lost = False

    lost_count = 0

    def redraw_window():

        # FONT IN GAME

        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"LIVES: {lives}", True, (255, 0, 0))
        level_label = main_font.render(f"LVL: {level}", True, (255, 0, 0))
        health_bar = main_font.render(f"CAN YOU LIVE:{player.health}", True, (255, 0, 0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(health_bar, (200, 275))
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("YOU LOST YOURSELF", True, (255, 0, 0))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))





        pygame.display.update()


    # RUNNING IN GAME SCREEN

    while run:
        clock.tick(FPS)
        redraw_window()

        # print(lives)
        # print(player.health)
        # print(lost)
        if lives <= 0 or player.health <= 0:
            GAME_OVER.play()
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # ENEMY WAVES

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(35, WIDTH - 65),
                              random.randrange(-1000 * level, -100),
                              random.choice(["enemy_1", "enemy_2", "enemy_3"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # KEYS PRESSED EVENTS

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            print("pressed A")
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            print("pressed d")
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            print("pressed w")
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 10 < HEIGHT:  # down
            print("pressed s")
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            PISTOL.play()
            player.shoot()

        # player_health = 100

        # BULLET SETTINGS WITH ENEMIES

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)
            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_bullets(-bullet_vel, enemies)

# MAIN MENU

def main_menu():
    name_font = pygame.font.SysFont("comicsans", 75)
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        WIN.blit(MM, (0, 0))
        title_label = title_font.render("PRESS MOUSEBUTTON TO TRY AND SAVE YOURSELF", 1, (255, 50, 0))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        name_label = name_font.render("SAVE YOURSELF", 1, (0, 0, 0))
        WIN.blit(name_label, (WIDTH / 2 - name_label.get_width() / 2, 150))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

main()
