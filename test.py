import pygame
import sys
import threading
import time
import cv2
from random import randint

pygame.init()
pygame.display.set_caption('Garage band')
size = 900, 750
screen = pygame.display.set_mode(size)

def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return wrapper


class Circle(pygame.sprite.Sprite):
    def __init__(self, number):
        global drumers
        super().__init__()
        self.image = pygame.image.load('images/red_circle.png')
        self.image = pygame.transform.scale(self.image, (200, 180))
        self.rect = self.image.get_rect()

        drumers.circles.add(self)

    def draw_circle(self, center, radius):
        pygame.draw.circle(screen, pygame.Color(155, 1, 189), center, radius, 5)

    def create_text(self, number, rect):
        font = pygame.font.Font(None, 54)
        text = font.render(str(number), True, (255, 255, 255))
        text_rect = rect
        text_rect.center = rect.center
        screen.blit(text, text_rect)




class Drumers:
    def __init__(self):
        self.background = pygame.image.load('images/drums.png')
        self.background_rect = self.background.get_rect()
        self.screen = screen
        self.stop = False

        self.circles = pygame.sprite.Group()

        self.BEATS = [2, 1]

    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        for i, circle in enumerate(self.circles):
            self.screen.blit(circle.image, (randint(100, 200), randint(100, 200)))
            circle.create_text(i + 1, circle.rect)
            # circle.draw_circle(circle.get_rect_center(), 200)


    @run_in_thread
    def new_circle(self):
        for i in range(len(self.BEATS)):
            time.sleep(self.BEATS[i])
            Circle(i + 1)

    def main(self):
        self.new_circle()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.draw()
            pygame.display.flip()


if __name__ == '__main__':
    drumers = Drumers()
    # guitar.set_main_circles()
    sys.exit(drumers.main())
