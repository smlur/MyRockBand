import pygame
import cv2

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

pygame.init()
window = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

gifFrameList = loadGIF(r"images/hero_walk.gif")
currentFrame = 0

run = True
while run:
    clock.tick(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill(0)

    rect = gifFrameList[currentFrame].get_rect(center = (250, 250))
    window.blit(gifFrameList[currentFrame], rect)
    currentFrame = (currentFrame + 1) % len(gifFrameList)

    pygame.display.flip()