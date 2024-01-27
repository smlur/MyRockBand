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
name_font = pygame.font.Font(None, 40)
text_font = pygame.font.Font(None, 30)

number_scene = 0
scenes = []
arr = []
for scene in open('novels.txt', 'r', encoding='utf-8').readlines():
    if scene.strip() != '_':
        arr.append(scene.strip())
    else:
        scenes.append(arr)
        arr = []

TABLE_REP_ZONE = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                  [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
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


class Novels:
    def __init__(self):
        pass

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
        self.set_scene(scenes[number_scene])
        

    def draw(self, scene):
        if scene[1] != 'False':
            background = pygame.image.load(scene[1])
            background = pygame.transform.scale(background, (900, 750))
            background_rect = background.get_rect()
            screen.blit(background, background_rect)

        if scene[5] != 'False':
            hero_img = pygame.image.load(scene[5])
            hero_img = pygame.transform.scale(hero_img, (200, 200))
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
            # case 'guitar':
            #     guitar.main()
            # case 'arcade':
            #     Arcade(scene).main()
            # case 'darkness':
            #     self.darkness(scene[1])



    def main(self):
        global scenes, number_scene
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
                        number_scene -= 1
            # try:
            self.set_scene(scenes[number_scene])
            # except:
            #     pygame.quit()
            #     return -1
            pygame.display.flip()


if __name__ == '__main__':
    novel = Novels()
    sys.exit(novel.main())

