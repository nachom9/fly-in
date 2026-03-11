import pygame


class TerminalOutput:

    def __init__(self, map):
        pass


class Screen:

    def __init__(self, map):
        self.width = map.width * 20 + 10
        self.heigth = map.heigth * 20 + 10
    
    def loop(self):
        pygame.init()
        window = pygame.display.set_mode(self.width, self.heigth)
        run = True
        while run:
            for event in pygame.event.get():
                if event.type() == pygame.QUIT:
                    run = False
        pygame.quit()
