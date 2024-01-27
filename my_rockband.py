# Устанавливаем необходимые библиотеки
import pygame
import sys
import threading
import time
import cv2
import sqlite3
from random import randint

# Инициализируем pygame и основной экран
pygame.init()
pygame.display.set_caption('My Rockband')
size = 900, 750
screen = pygame.display.set_mode(size)
hero_sprites = pygame.sprite.Group()

# Устанавливаем шрифты
name_font = pygame.font.Font('plot/font.otf', 20)
text_font = pygame.font.Font('plot/font.otf', 16)
font = pygame.font.Font('plot/font.otf', 30)

# Инициализируем переменную отвечающую за номер сцены
number_scene = 0

# Переменная отвечающая за работу второго потока
stop_thread = False

# Функция для получения последней сцены из бд
def select():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    res = cur.execute('SELECT save_scene FROM scenes').fetchall()[-1][0]
    con.close()
    return res

# Функция для сохранения последней сцены
def insert(number):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute(f'INSERT INTO scenes VALUES ({number})')
    con.commit()
    con.close()

# Карта аркадной зоны
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

# Второй поток
def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper

# Функции для подключение gif изображений
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


# Класс Гитарной игры
class Guitar:
    def __init__(self):
        # Устанавливаем счет
        self.score = 0

        # Переменные ответственные за прохождение игры
        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False

        # Таймер
        self.clock = pygame.time.Clock()

        # Группы спрайтов
        self.move_circles = pygame.sprite.Group()
        self.main_sprites = pygame.sprite.Group()

        # Песни на каждый уровень
        self.MUSIC_1 = [(0, 13.65)] + [(1, .35), (2, 0.35), (1, .35), (2, 0.35), (1, .35), (2, 0.35), (1, .35),
                        (2, 0.35),
                        (2, .35), (3, 0.35), (2, .35), (3, 0.35),
                        (1, 0.35), (3, .17), (1, .17), (2, .17), (1, .17), (3, .17), (1, .17), (3, .17),
                        ] * 5 + [(1, 11.2), (2, 1.6), (3, 1.6), (4, 1.6)] + [(0, 12.65)] + [(1, .35), (2, 0.35), (1, .35),
                        (2, 0.35), (1, .35), (2, 0.35), (1, .35), (2, 0.35),
                        (2, .35), (3, 0.35), (2, .35), (3, 0.35),
                        (1, 0.35), (3, .17), (1, .17), (2, .17), (1, .17), (3, .17), (1, .17), (3, .17),
                        ] * 3

        self.MUSIC_2 = [(0, 6.3)] + [(1, .35), (2, .35), (3, .6), (1, .83), (2, .55), (4, .35), (3, .35),
                        (1, .83), (2, .55), (3, .6), (1, .75), (2, .5), (0, 1.3)] * 4 + [(1, .35), (2, .35),
                        (3, .6), (1, .83), (2, .55), (4, .35), (3, .35),
                        (1, .83), (2, .55), (3, .6), (1, .75), (2, .5), (0, 1.5)]
        
        self.MUSIC_3 = [(0, 6.5)] + ([(1, .4)] * 2 + [(1, .4), (1, .8), (1, .2),
                        (1, .2), (2, .2), (1, .2), (2, .2), (0, .8)]) * 5 + ([(3, .2), (3, .2), (3, .3), (4, .2), (2, .2), (2, .2),
                        (3, .2)] + [(3, .2), (3, .2), (3, .3), (4, .2), (2, .2), (3, .2)]) * 2 + [(0, 1.7)] + ([(1, .4)] * 2 + [(1, .4),
                        (1, .8), (1, .2), (1, .2), (2, .2), (1, .2), (2, .2), (0, .83)]) * 3 + [(3, .4), (3, .2), (3, .3), (4, .2), (2, .2), (2, .2),
                        (3, .2)] + [(3, .2), (3, .2), (3, .3), (4, .2), (2, .2), (3, .2), (0, .7)]
        
        self.MUSIC_4 = ([(1, 0)] + [(3, 0.3), (3, 0.3), (4, 0.2), (2, .5), (2, .5), (2, .5), (2, .5), (4, .5), (1, 1)] * 3 + [(3, 0.3),
                        (3, 0.3), (4, 0.2), (2, .5),]) * 2
        
        self.MUSIC_5 = [(0, 5)] + ([(1, 1), (2, .5), (3, .5), (4, .5), (4, .5), (3, .5), (2, .5)] + [(1, .5),
                         (1, .3), (2, .2), (3, .2), (4, .2)] * 2) * 6 + [(0, 4)] + [(1, 1), (2, 2), (3, 2), (4, 2)] * 2
        
        # Список со всеми песнями
        self.MUSICS = [self.MUSIC_1, self.MUSIC_2, self.MUSIC_3, self.MUSIC_4, self.MUSIC_5]


    # Функция для определения объектов классов основных кнопок(кружков)
    def set_main_circles(self):
        self.red = Main_red_circles()
        self.yellow = Main_yellow_circles()
        self.blue = Main_blue_circles()
        self.green = Main_green_circles()

    # Появление движущихся кружков во втором потоке
    @run_in_thread
    def new_circle(self, music):
        pygame.mixer.music.play(-1)
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
        pygame.mixer.music.stop()

        # Определение выигрыша
        self.win = self.stop = self.score >= len(music) * 60

    # Функция отрисовку элементов
    def draw(self, scene):
        # Отрисовываем задний фон
        background = pygame.image.load(scene)
        background = pygame.transform.scale(background, (900, 750))
        background.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
        background_rect = background.get_rect()
        screen.blit(background, background_rect)

        # Отрисовываем счет игры
        text = font.render(str(self.score), True, (255, 255, 255))
        screen.blit(text, (10, 10, 200, 200))

        # Отрисовываем линии
        pygame.draw.line(screen, (255, 255, 255), [self.red.rect.center[0] - 3, 0], [self.red.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.yellow.rect.center[0] - 3, 0], [self.yellow.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.blue.rect.center[0] - 3, 0], [self.blue.rect.center[0] - 3, 750], 3)
        pygame.draw.line(screen, (255, 255, 255), [self.green.rect.center[0] - 3, 0], [self.green.rect.center[0] - 3, 750], 3)

        # Проверка отрисовки кнопки перезапуска
        if not self.win:
            self.restart = Restart()
            self.button_restart = True
            self.win = True

        # Отрисовка спрайтов
        self.main_sprites.draw(screen)
        self.move_circles.draw(screen)

    # Функция проверки нажатия кнопки
    def keydown(self, event):
        for sprite in self.move_circles:
            # В случае если кнопка нажата вовремя удаляется спрайт и увеличивается счет
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

    # Основная функция класса
    def main(self, scene): 
        global number_scene

        # Сброс изначальных значений
        self.score = 0
        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False

        # Загрузка необходимой музыки
        pygame.mixer.music.load(scene[2])

        # Появление новых кружков
        self.new_circle(self.MUSICS[int(scene[3])])
        while not self.stop:
            for event in pygame.event.get():
                # Выход из игры
                if event.type == pygame.QUIT:
                    insert(number_scene - 1)
                    pygame.quit()
                    sys.exit()

                # Обработка нажатой кнопки
                if event.type == pygame.KEYDOWN:
                    self.keydown(event)

                # Обработка перезапуска уровня
                if event.type == pygame.MOUSEBUTTONDOWN and self.button_restart:
                    pygame.mixer.music.stop()
                    if self.restart.rect.collidepoint(event.pos):
                        self.score = 0
                        self.new_circle(self.MUSICS[int(scene[3])])
                        self.restart.kill()
                        self.button_restart = False

            # Вызов функции отрисовки элементов
            self.draw(scene[1])

            # Движение кружков вверх и удаление при уходе за экран
            for circle in self.move_circles:
                circle.rect.y -= 10
                if circle.rect.y < -100:
                    circle.kill()
            
            # FPS и обновление экрана
            self.clock.tick(30)
            pygame.display.flip()

# Классы для кружков с позициями и картинками
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


# Класс кнопки restart'а
class Restart(pygame.sprite.Sprite):
    def __init__(self):
        global guitar, size
        super().__init__()
        self.image = pygame.image.load('images/restart.png')
        self.image = pygame.transform.scale(self.image, (200, 150))
        self.rect = self.image.get_rect()
        self.rect.center = (size[0] // 2, size[1] // 2)
        guitar.main_sprites.add(self)


# Основной класс игры
class Novels:
    def __init__(self):
        # Загрузка всех сцен из файла
        self.scenes = []

        arr = []
        for scene in open('plot/novels.txt', 'r', encoding='utf-8').readlines():
            if scene.strip() != '_':
                arr.append(scene.strip())
            else:
                self.scenes.append(arr)
                arr = []

    # Функция затемнения экрана
    def darkness(self, scene):
        for color in range(200, 50, -20):
            background = pygame.image.load(scene)
            background = pygame.transform.scale(background, (900, 750))
            background.fill((color, color, color), special_flags=pygame.BLEND_RGBA_MULT)
            background_rect = background.get_rect()
            screen.blit(background, background_rect)
            pygame.display.flip()
            time.sleep(.1)
        
    # Функция отрисовки элементов
    def draw(self, scene):
        # Отрисовка заднего фона
        background = pygame.image.load(scene[1])
        background = pygame.transform.scale(background, (900, 750))
        background_rect = background.get_rect()
        screen.blit(background, background_rect)

        # Отрисовка персонажа при необходимости
        if scene[5] != 'False':
            hero_img = pygame.image.load(scene[5])
            hero_img = pygame.transform.scale(hero_img, tuple(map(int, scene[7].split())))
            hero_rect = hero_img.get_rect()
            hero_rect.x = int(scene[6].split()[0])
            hero_rect.y = int(scene[6].split()[1])
            screen.blit(hero_img, hero_rect)

        # Отрисовка поля для текста
        rect = pygame.Surface((900, 150))
        rect.set_alpha(220)
        rect.fill((32, 32, 32))
        screen.blit(rect, (0, 600))

        # Отрисовка текста (Имя героя и его реплика)
        name_hero = name_font.render(scene[2], True, tuple(map(int, scene[4].split())))
        text_hero = text_font.render(scene[3], True, tuple(map(int, scene[4].split())))
        screen.blit(text_hero, (30, 650))
        screen.blit(name_hero, (20, 610))

    # Опредение типа сцены
    def set_scene(self, scene):
        global guitar, number_scene
        match scene[0]:
            case 'novel':
                self.draw(scene)
            case 'guitar':
                guitar.main(scene)
                pygame.mixer.music.load('musics/novel.mp3')
                pygame.mixer.music.play(0)
                number_scene += 1
            case 'drum':
                drumers.main()
                pygame.mixer.music.load('musics/novel.mp3')
                pygame.mixer.music.play(0)
                number_scene += 1
            case 'arcade':
                self.arcade = Arcade(scene)
                self.arcade.main()
                number_scene += 1
            case 'darkness':
                self.darkness(scene[1])
                number_scene += 1
            case 'end':
                screen.fill((0, 0, 0))
                end_font = pygame.font.Font('plot/font.otf', 50)
                end_text = end_font.render('Конец', True, (255, 255, 255))
                avtors = name_font.render('Авторы:', True, (255, 255, 255))
                name_1 = name_font.render('Семенова Саша', True, (255, 255, 255))
                name_2 = name_font.render('Гусев Влад', True, (255, 255, 255))
                screen.blit(end_text, (size[0] // 2 - 90, size[1] // 2 - 50))
                screen.blit(avtors, (size[0] // 2 - 50, size[1] // 2 + 20))
                screen.blit(name_1, (size[0] // 2 - 90, size[1] // 2 + 50))
                screen.blit(name_2, (size[0] // 2 - 90, size[1] // 2 + 80))


    # Основная функиция класса
    def main(self):
        global number_scene

        pygame.mixer.music.load('musics/novel.mp3')
        pygame.mixer.music.play(0)
        while True:
            # Выход из игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    insert(number_scene)
                    pygame.quit()
                    return -1
                
                # Переключение сцены
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        number_scene += 1
                    elif event.key == pygame.K_RIGHT:
                        number_scene += 1
                    elif event.key == pygame.K_LEFT:
                        number_scene -= 1
            
            # Вызов функции с обработкой вида сцены
            if 0 <= number_scene <= len(self.scenes) - 1:
                self.set_scene(self.scenes[number_scene])
            elif number_scene > len(self.scenes) - 1:
                pygame.quit()
                return -1
            pygame.display.flip()



# Классы Аркады
class Arcade:
    def __init__(self, scene):
        self.scene = scene

        # Будущая переменная со спрайтом с которым ведется диалог
        self.dialog_sprite = None

        # Таймер
        self.clock = pygame.time.Clock()

        # Задний фон
        self.background = pygame.image.load(scene[1])
        self.background_rect = self.background.get_rect()

        # Кнопка диалога
        self.used_button = pygame.image.load('images/used_button.png')
        self.used_button = pygame.transform.scale(self.used_button, (30, 30))
        self.button_rect = self.used_button.get_rect()

        # Спрайт персонажей
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
        # Позиция героя относительно таблицы
        self.hero.pos[1] = (self.hero.abs_x + self.hero.speed_x) // 66
        self.hero.pos[0] = (self.hero.abs_y + self.hero.speed_y + 60) // 66

        # Отрисовка фона
        screen.blit(self.background, self.background_rect)

        # Перемещенние персонажа при отсутсвие препятствий и границ экрана
        if not TABLE_REP_ZONE[self.hero.pos[0]][self.hero.pos[1]] and 33 <= self.hero.abs_x + self.hero.speed_x <= 1651 and 1 <= self.hero.abs_y + self.hero.speed_y <= 630:
            # Перемещение экрана относительно всего поля локации
            self.hero.abs_x += self.hero.speed_x
            self.hero.abs_y += self.hero.speed_y
            if 33 < self.hero.x_pos + self.hero.speed_x < 801 and 0 <= self.hero.y_pos + self.hero.speed_y <= 630:
                # Перемещение персонажа относительно экрана
                self.hero.x_pos += self.hero.speed_x
                self.hero.y_pos += self.hero.speed_y
            else:
                # Сдвиг локации и персонажей в случае движения героя близ края экрана
                if -800 < self.background_rect.x - self.hero.speed_x < 0:
                    self.background_rect.x -= self.hero.speed_x  
                    self.drumers.rect.x -= self.hero.speed_x 
                    self.basser.rect.x -= self.hero.speed_x  
                    self.friend.rect.x -= self.hero.speed_x

        # Отрисовка спрайтов
        hero_sprites.draw(screen)

        # Обработка столкновений со спрайтами
        if 5 <= self.hero.pos[0] <= 7 and 1 <= self.hero.pos[1] <= 3:
            self.button_rect.x = self.hero.x_pos + 17
            self.button_rect.y = self.hero.y_pos - 23
            screen.blit(self.used_button, self.button_rect)
            self.dialog_sprite = self.friend
        elif 4 <= self.hero.pos[0] <= 6 and 12 <= self.hero.pos[1] <= 14:
            self.button_rect.x = self.hero.x_pos + 17
            self.button_rect.y = self.hero.y_pos - 23
            screen.blit(self.used_button, self.button_rect)
            self.dialog_sprite = self.drumers
        elif 3 <= self.hero.pos[0] <= 5 and 16 <= self.hero.pos[1] <= 18:
            self.button_rect.x = self.hero.x_pos + 17
            self.button_rect.y = self.hero.y_pos - 23
            screen.blit(self.used_button, self.button_rect)
            self.dialog_sprite = self.basser
        else:
            self.dialog_sprite = None

        # Отрисовка героя
        try:
            img = self.hero.image[self.hero.currentFrame]
        except:
            img = self.hero.image[0]
        if img:
            img.set_colorkey((255, 255, 255))
            img = pygame.transform.scale(img, (66, 120))
            screen.blit(img, img.get_rect(top=self.hero.y_pos, left=self.hero.x_pos))

    # Диалог с персонажами
    def dialog(self, sprite):
        global number_scene

        # Управление диалогом
        number = 0
        scene = list(filter(lambda x: x[0] == self.scene[8], sprite.scenes))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    insert(number_scene)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        number += 1
                    elif event.key == pygame.K_RIGHT:
                        number += 1
                    elif event.key == pygame.K_LEFT:
                        number -= 1
            # Отрисовка элементов
            self.draw()

            # Отрисовка диалога
            if 0 <= number <= len(scene) - 1:
                rect = pygame.Surface((900, 150))
                rect.set_alpha(220)
                rect.fill((32, 32, 32))
                screen.blit(rect, (0, 600))

                name_hero = name_font.render(scene[number][1], True, tuple(map(int, scene[number][3].split())))
                text_hero = text_font.render(scene[number][2], True, tuple(map(int, scene[number][3].split())))
                screen.blit(text_hero, (30, 650))
                screen.blit(name_hero, (20, 610))
            elif number > len(scene) - 1:
                sprite.need = False
                return -1
            pygame.display.flip()

    # Основная функция класса
    def main(self):
        # pygame.mixer.music.play(0)
        global stop_thread, number_scene

        stop_thread = False

        # Объект класса основного персонажа
        self.hero = Hero()
        self.hero.animate()
        while self.drumers.need or self.friend.need or self.basser.need:
            # Выход из игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_thread = True
                    insert(number_scene)
                    pygame.quit()
                    sys.exit()

                # Перемещения герой
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and self.dialog_sprite:
                        self.dialog(self.dialog_sprite)
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

            # Отрисовка элементов FPS и обновление экрана
            self.draw()
            self.clock.tick(30)
            pygame.display.flip()
        stop_thread = True
        for sprite in hero_sprites:
            sprite.kill()


# Классы с персонажами
class Drumers(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/drumers.png')
        self.image = pygame.transform.scale(self.image, (66, 100))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None

        self.scenes = []

        arr = []
        for scene in open('plot/drumers.txt', 'r', encoding='utf-8').readlines():
            if scene.strip() != '_':
                arr.append(scene.strip())
            else:
                self.scenes.append(arr)
                arr = []


class Basser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/basser.png')
        self.image = pygame.transform.scale(self.image, (50, 90))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None

        self.scenes = []

        arr = []
        for scene in open('plot/basser.txt', 'r', encoding='utf-8').readlines():
            if scene.strip() != '_':
                arr.append(scene.strip())
            else:
                self.scenes.append(arr)
                arr = []


class Friend(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('images/friend.png')
        self.image = pygame.transform.scale(self.image, (70, 120))
        self.rect = self.image.get_rect()
        hero_sprites.add(self)
        self.need = None

        self.scenes = []

        arr = []
        for scene in open('plot/friend.txt', 'r', encoding='utf-8').readlines():
            if scene.strip() != '_':
                arr.append(scene.strip())
            else:
                self.scenes.append(arr)
                arr = []


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
        global stop_thread
        while not stop_thread:
            if self.speed_x != 0:
                time.sleep(0.25)
                self.currentFrame = (self.currentFrame + 1) % len(self.image)

# Класс стартового экрана
class Start:
    def __init__(self):
        # Задний фон и кнопки
        self.background = pygame.image.load('images/start.png')
        self.background_rect = self.background.get_rect()

        self.start_button = pygame.image.load('images/start_button.png')
        self.start_button = pygame.transform.scale(self.start_button, (350, 100))
        self.start_button_rect = self.start_button.get_rect()
        self.start_button_rect.center = (630, 450)

        self.continue_button = pygame.image.load('images/continue.png')
        self.continue_button = pygame.transform.scale(self.continue_button, (350, 100))
        self.continue_button_rect = self.continue_button.get_rect()
        self.continue_button_rect.center = (630, 550)

    # Отрисовка
    def draw(self):
        screen.blit(self.background, self.background_rect)
        screen.blit(self.start_button, self.start_button_rect)
        screen.blit(self.continue_button, self.continue_button_rect)

    def main(self):
        global number_scene
        while True:
            for event in pygame.event.get():
                # Выход
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return -1
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Новая игра
                    if self.start_button_rect.collidepoint(event.pos):
                        number_scene = 0
                        Novels().main()
                        return -1
                    # Продолжить игру
                    if self.continue_button_rect.collidepoint(event.pos):
                        number_scene = select()
                        Novels().main()
                        return -1
            self.draw()
            pygame.display.flip()

# Класс кружков для барабанов
class Circle(pygame.sprite.Sprite):
    def __init__(self, number):
        # инициализация спрайта
        global drumers
        super().__init__()
        self.image = pygame.image.load('images/purple.png')
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        self.number = number
        self.radius = 150
        self.iteration = 0

        # Появление кружков
        while True:
            self.rect.topleft = (
                (randint(0, 900 - self.rect.width),
                 randint(0, 750 - self.rect.height))
            )
            if not pygame.sprite.spritecollideany(self, drumers.circles):
                drumers.circles.add(self)
                break

    # изменение радиуса и итераций
    def change_iteration(self):
        self.iteration += 1
        return self.iteration

    def change_radius(self, radius):
        self.radius = radius
        return self.radius

    def get_rect_center(self):
        return self.rect.center

    def get_number(self):
        return self.number

    # отрисовка
    def draw_circle(self, center, radius):
        pygame.draw.circle(screen, pygame.Color(155, 1, 189), center, radius, 5)

    # отрисовка порядкового номера кружка
    def create_text(self, number, rect):
        font = pygame.font.Font(None, 54)
        text = font.render(str(number), True, (255, 255, 255))
        text_rect = rect
        text_rect.center = rect.center
        screen.blit(text, text_rect.center)

    # обработка нажатия
    def clicked(self, event):
        if self.rect.collidepoint(event.pos):
            return True
        return False


# класс барабанов
class Drum:
    def __init__(self):
        self.background = pygame.image.load('images/drumm.png')
        self.background_rect = self.background.get_rect()
        self.screen = screen
        self.stop = False

        self.clock = pygame.time.Clock()

        self.circles = pygame.sprite.Group()

        self.BEATS = [11] + [.1, .3,] * 6 + [.6] * 3 + [.8] * 43 + [.5] * 37 +  [.8] * 10

        self.score = 0

        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False
        self.restart = Drum_restart()

    # Отрисовка
    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        for i, circle in enumerate(self.circles):
            self.screen.blit(circle.image, circle.rect)
            circle.draw_circle(circle.get_rect_center(), circle.change_radius(150 - circle.change_iteration()))
            circle.create_text(circle.get_number(), circle.rect)
        font = pygame.font.Font('plot/font.otf', 30)
        text = font.render(str(self.score), True, (255, 255, 255))
        screen.blit(text, (10, 10, 200, 200))
        if not self.win:
            screen.blit(self.restart.image, self.restart.rect)
            self.button_restart = True
            
    # Появление кружков
    @run_in_thread
    def new_circle(self, music):
        pygame.mixer.music.load("musics/engel.mp3")
        pygame.mixer.music.play(-1)
        for i in range(len(music)):
            time.sleep(music[i])
            Circle(i + 1)
        while self.circles:
            time.sleep(0.1)
        pygame.mixer.music.stop()
        self.win = self.stop = self.score >= len(music) * 60

    def main(self):
        self.restart = None
        self.win = True
        self.stop = False
        self.button_restart = False
        self.new_circle(self.BEATS)
        while not self.stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for circle in self.circles:
                        if circle.rect.collidepoint(event.pos) and circle.change_radius(150 - circle.change_iteration()) > 0:
                            # print(circle.change_radius(150 - circle.change_iteration()))
                            self.score += 100
                            circle.kill()
                    if self.button_restart and self.restart.rect.collidepoint(event.pos):
                        self.win = True
                        self.button_restart = False
                        self.new_circle(self.BEATS)
                        

            self.clock.tick(30)
            for circle in self.circles:
                if circle.change_radius(150 - circle.change_iteration()) <= 0:
                    circle.kill()

            self.draw()
            pygame.display.flip()
            
class Drum_restart(pygame.sprite.Sprite):
    def __init__(self):
        global drumers, size
        super().__init__()
        self.image = pygame.image.load('images/restart.png')
        self.image = pygame.transform.scale(self.image, (200, 150))
        self.rect = self.image.get_rect()
        self.rect.center = (size[0] // 2, size[1] // 2)


# Запуск
if __name__ == '__main__':
    drumers = Drum()
    guitar = Guitar()
    guitar.set_main_circles()
    game = Start()
    sys.exit(game.main())


