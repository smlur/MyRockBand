import pygame
import sys
import threading
import time
import cv2

pygame.init()
pygame.display.set_caption('Garage band')
size = 900, 750
screen = pygame.display.set_mode(size)
hero_sprites = pygame.sprite.Group()
name_font = pygame.font.Font('font.otf', 20)
text_font = pygame.font.Font('font.otf', 16)
font = pygame.font.Font('font.otf', 30)


TABLE_REP_ZONE = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return wrapper

def cv2ImageToSurface(cv2Image):
    size = cv2Image.shape[1::-1]
    format = 'RGBA' if cv2Image.shape[2] == 4 else 'RGB'
    cv2Image[:, :, [0, 2]] = cv2Image[:, :, [2, 0]]
    surface = pygame.image.frombuffer(cv2Image.flatten(), size, format)
    return surface.convert_alpha() if format == 'RGBA' else surface.convert()

def loadGIF(filename):
    gif = cv2.VideoCapture(filename)
    frames = []
    while True:
        ret, cv2Image = gif.read()
        if not ret:
            break
        pygameImage = cv2ImageToSurface(cv2Image)
        frames.append(pygameImage)
    return frames


class Guitar:
    def __init__(self):
        self.score = 0

        self.red = None
        self.yellow = None
        self.blue = None
        self.green = None

        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False

        self.clock = pygame.time.Clock()

        self.move_circles = pygame.sprite.Group()
        self.main_sprites = pygame.sprite.Group()

        self.MUSIC_1 = [(1, 0)]
        self.MUSICS = [self.MUSIC_1]



    def set_main_circles(self):
        self.red = Main_red_circles()
        self.yellow = Main_yellow_circles()
        self.blue = Main_blue_circles()
        self.green = Main_green_circles()

    @run_in_thread
    def new_circle(self, music):
        for circle in music:
            time.sleep(circle[1])
            match circle[0]:
                case 0:
                    pass
                case 1:
                    Move_red_circles()
                case 2:
                    Move_yellow_circles()
                case 3:
                    Move_blue_circles()
                case 4:
                    Move_green_circles()
        while self.move_circles:
            time.sleep(0.1)
        self.win = self.stop = self.score >= len(music) * 60

    def draw(self, scene):
        screen.fill((0, 0, 0))
        background = pygame.image.load(scene)
        background = pygame.transform.scale(background, (900, 750))
        background.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
        background_rect = background.get_rect()
        screen.blit(background, background_rect)
        text = font.render(str(self.score), True, (255, 255, 255))
        screen.blit(text, (10, 10, 200, 200))
        pygame.draw.line(screen, (255, 255, 255), [self.red.rect.center[0] - 3, 0], [self.red.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.yellow.rect.center[0] - 3, 0], [self.yellow.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.blue.rect.center[0] - 3, 0], [self.blue.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.green.rect.center[0] - 3, 0], [self.green.rect.center[0] - 3, 750], 3)
        if not self.win:
            self.restart = Restart()
            self.button_restart = True
            self.win = True
        self.main_sprites.draw(screen)
        self.move_circles.draw(screen)

    def keydown(self, event):
        for sprite in self.move_circles:
            match event.key:
                case pygame.K_1:
                    if 0 <= abs(self.red.rect.center[1] - sprite.rect.center[1]) <= 20 and self.red.rect.x == sprite.rect.x:
                        self.score += 100
                        sprite.kill()
                case pygame.K_2:
                    if 0 <= abs(self.yellow.rect.center[1] - sprite.rect.center[1]) <= 20 and self.yellow.rect.x == sprite.rect.x:
                        self.score += 100
                        sprite.kill()
                case pygame.K_3:
                    if 0 <= abs(self.blue.rect.center[1] - sprite.rect.center[1]) <= 20 and self.blue.rect.x == sprite.rect.x:
                        self.score += 100
                        sprite.kill()
                case pygame.K_4:
                    if 0 <= abs(self.green.rect.center[1] - sprite.rect.center[1]) <= 20 and self.green.rect.x == sprite.rect.x:
                        self.score += 100
                        sprite.kill()

    def main(self, scene):
        self.score = 0
        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False
        pygame.mixer.music.load(scene[2])
        self.new_circle(self.MUSICS[int(scene[3])])
        pygame.mixer.music.play(-1)
        while not self.stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.keydown(event)
                if event.type == pygame.MOUSEBUTTONDOWN and self.button_restart:
                    pygame.mixer.music.stop()
                    if self.restart.rect.collidepoint(event.pos):
                        self.score = 0
                        self.new_circle(self.MUSICS[int(scene[3])])
                        self.restart.kill()
                        self.button_restart = False
            self.draw(scene[1])
            for circle in self.move_circles:
                circle.rect.y -= 10
                if circle.rect.y < -100:
                    circle.kill()
            self.clock.tick(30)
            pygame.display.flip()
        pygame.mixer.music.stop()


class Main_red_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/dark_red_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 205
        self.rect.y += 10
        guitar.main_sprites.add(self)


class Main_yellow_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/dark_yellow_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 325
        self.rect.y += 10
        guitar.main_sprites.add(self)


class Main_blue_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/dark_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 445
        self.rect.y += 10
        guitar.main_sprites.add(self)


class Main_green_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/dark_green_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 565
        self.rect.y += 10
        guitar.main_sprites.add(self)


class Move_green_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/green_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 565
        self.rect.y += 750
        guitar.move_circles.add(self)


class Move_red_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/red_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 205
        self.rect.y += 750
        guitar.move_circles.add(self)


class Move_blue_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 445
        self.rect.y += 750
        guitar.move_circles.add(self)


class Move_yellow_circles(pygame.sprite.Sprite):
    def __init__(self):
        global guitar
        super().__init__()
        self.image = pygame.image.load('images/yellow_circle.png')
        self.image = pygame.transform.scale(self.image, (120, 100))
        self.rect = self.image.get_rect()
        self.rect.x += 325
        self.rect.y += 750
        guitar.move_circles.add(self)


class Restart(pygame.sprite.Sprite):
    def __init__(self):
        global guitar, size
        super().__init__()
        self.image = pygame.image.load('images/restart.png')
        self.image = pygame.transform.scale(self.image, (200, 150))
        self.rect = self.image.get_rect()
        self.rect.center = (size[0] // 2, size[1] // 2)
        guitar.main_sprites.add(self)


class Novels:
    def __init__(self):
        self.number_scene = 0
        self.scenes = []

        arr = []
        for scene in open('novels.txt', 'r', encoding='utf-8').readlines():
            if scene.strip() != '_':
                arr.append(scene.strip())
            else:
                self.scenes.append(arr)
                arr = []

    def darkness(self, scene):
        for color in range(200, 50, -20):
            background = pygame.image.load(scene)
            background = pygame.transform.scale(background, (900, 750))
            background.fill((color, color, color), special_flags=pygame.BLEND_RGBA_MULT)
            background_rect = background.get_rect()
            screen.blit(background, background_rect)
            pygame.display.flip()
            time.sleep(.1)
        self.number_scene += 1
        

    def draw(self, scene):
        background = pygame.image.load(scene[1])
        background = pygame.transform.scale(background, (900, 750))
        background_rect = background.get_rect()
        screen.blit(background, background_rect)

        if scene[5] != 'False':
            hero_img = pygame.image.load(scene[5])
            hero_img = pygame.transform.scale(hero_img, tuple(map(int, scene[7].split())))
            hero_rect = hero_img.get_rect()
            hero_rect.x = int(scene[6].split()[0])
            hero_rect.y = int(scene[6].split()[1])
            screen.blit(hero_img, hero_rect)

        rect = pygame.Surface((900, 150))
        rect.set_alpha(220)
        rect.fill((32, 32, 32))
        screen.blit(rect, (0, 600))

        name_hero = name_font.render(scene[2], True, tuple(map(int, scene[4].split())))
        text_hero = text_font.render(scene[3], True, tuple(map(int, scene[4].split())))
        screen.blit(text_hero, (30, 650))
        screen.blit(name_hero, (20, 610))

    def set_scene(self, scene):
        global guitar, arcade
        match scene[0]:
            case 'novel':
                self.draw(scene)
            case 'guitar':
                guitar.main(scene)
                self.number_scene += 1
            case 'arcade':
                self.arcade = Arcade(scene)
                self.arcade.main()
                self.number_scene += 1
            case 'darkness':
                self.darkness(scene[1])
            case 'end':
                screen.fill((0, 0, 0))
                end_font = pygame.font.Font('font.otf', 50)
                end_text = end_font.render('Конец', True, (255, 255, 255))
                screen.blit(end_text, (size[0] // 2 - 90, size[1] // 2 - 50))



    def main(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return -1
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.number_scene += 1
                    elif event.key == pygame.K_RIGHT:
                        self.number_scene += 1
                    elif event.key == pygame.K_LEFT:
                        self.number_scene -= 1
            try:
                self.set_scene(self.scenes[self.number_scene])
            except:
                pygame.quit()
                return -1
            pygame.display.flip()



class Arcade:
    def __init__(self, scene):
        self.scene = scene

        self.clock = pygame.time.Clock()

        self.background = pygame.image.load(scene[1])
        self.background_rect = self.background.get_rect()

        self.used_button = pygame.image.load('images/used_button.png')
        self.used_button = pygame.transform.scale(self.used_button, (30, 30))
        self.button_rect = self.used_button.get_rect()

        self.drumers = Drumers()
        self.drumers.rect.x = int(self.scene[2].split()[0])
        self.drumers.rect.y = int(self.scene[2].split()[1])
        self.drumers.need = int(scene[6])

        self.basser = Basser()
        self.basser.rect.x = int(self.scene[3].split()[0])
        self.basser.rect.y = int(self.scene[3].split()[1])
        self.basser.need = int(scene[7])

        self.friend = Friend()
        self.friend.rect.x = int(self.scene[4].split()[0])
        self.friend.rect.y = int(self.scene[4].split()[1])
        self.friend.need = int(scene[5])

    def draw(self):
        self.hero.pos[1] = (self.hero.abs_x + self.hero.speed_x) // 66
        self.hero.pos[0] = (self.hero.abs_y + self.hero.speed_y + 60) // 66
        screen.blit(self.background, self.background_rect)
        # for sprite in hero_sprites:
        if not TABLE_REP_ZONE[self.hero.pos[0]][self.hero.pos[1]] and 33 <= self.hero.abs_x + self.hero.speed_x <= 1651 and 1 <= self.hero.abs_y + self.hero.speed_y <= 630:
            self.hero.abs_x += self.hero.speed_x
            self.hero.abs_y += self.hero.speed_y
            if 33 < self.hero.x_pos + self.hero.speed_x < 801 and 0 <= self.hero.y_pos + self.hero.speed_y <= 630:
                self.hero.x_pos += self.hero.speed_x
                self.hero.y_pos += self.hero.speed_y
            else:
                if -800 < self.background_rect.x - self.hero.speed_x < 0:
                    self.background_rect.x -= self.hero.speed_x  
                    self.drumers.rect.x -= self.hero.speed_x 
                    self.basser.rect.x -= self.hero.speed_x  
                    self.friend.rect.x -= self.hero.speed_x
        for sprite in hero_sprites:
            if sprite.rect.collidepoint((self.hero.abs_x, self.hero.y_pos)):
                print(True)
                self.button_rect.x = self.hero.x_pos + 17
                self.button_rect.y = self.hero.y_pos - 23
                screen.blit(self.used_button, self.button_rect)

        try:
            img = self.hero.image[self.hero.currentFrame]
        except:
            img = self.hero.image[0]
        if img:
            img.set_colorkey((255, 255, 255))
            img = pygame.transform.scale(img, (66, 120))
            hero_sprites.draw(screen)
            screen.blit(img, img.get_rect(top=self.hero.y_pos, left=self.hero.x_pos))

        
        pygame.display.flip()

    def main(self):
        self.hero = Hero()
        self.hero.animate()
        while self.drumers.need or self.friend.need or self.basser.need:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_RIGHT:
                            self.hero.image = loadGIF("images/hero_walk.gif")
                            self.hero.speed_x = 6
                        case pygame.K_LEFT:
                            self.hero.image = loadGIF('images/hero_walk_left.gif')
                            self.hero.speed_x = -6
                        case pygame.K_DOWN:
                            self.hero.currentFrame = 0
                            self.hero.image = loadGIF('images/hero.gif')
                            self.hero.speed_y = 6
                        case pygame.K_UP:
                            self.hero.currentFrame = 0
                            self.hero.image = loadGIF('images/hero.gif')
                            self.hero.speed_y = -6
                if event.type == pygame.KEYUP:
                    self.hero.currentFrame = 0
                    self.hero.image = loadGIF('images/hero.gif')
                    self.hero.speed_y = 0
                    self.hero.speed_x = 0

            self.draw()
            self.clock.tick(30)
            pygame.display.flip()


class Hero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.currentFrame = 0
        self.image = loadGIF('images/hero.gif')
        self.rect = self.image[self.currentFrame].get_rect(center = (250, 250))
        self.pos = [5, 0]
        self.x_pos = 198
        self.y_pos = 600
        self.abs_x = 198
        self.abs_y = 600
        self.speed_y = 0
        self.speed_x = 0
        

    @run_in_thread
    def animate(self):
        global novels
        while novels.arcade.drumers.need or novels.arcade.basser.need or novels.arcade.friend.need:
            if self.speed_x != 0:
                time.sleep(0.25)
                self.currentFrame = (self.currentFrame + 1) % len(self.image)


class Drumers(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/drumers.png')
        self.image = pygame.transform.scale(self.image, (70, 120))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None


class Basser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/basser.png')
        self.image = pygame.transform.scale(self.image, (50, 90))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None


class Friend(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/friend.png')
        self.image = pygame.transform.scale(self.image, (66, 100))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None



if __name__ == '__main__':
    guitar = Guitar()
    guitar.set_main_circles()
    novels = Novels()
    sys.exit(novels.main())


