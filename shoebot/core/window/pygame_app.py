import pygame

from shoebot.core.window.app import ShoebotApp
from shoebot.core.window.pygame_window import PyGameWindow


class PyGameApp(ShoebotApp):
    """
    The pygame app uses the PyGameWindow for rendering.

    In pygame the window is updated in the main loop, which is
    handled by the run method here.
    """
    name = "pygame"

    def __init__(self):
        self.window = PyGameWindow()
        super().__init__(self.window.runner)
    def run(self):
        # TODO run the main loop from here.
        pygame.init()

        window = PyGameWindow(self.runner)

        ## scene_manager = RevertableSceneManager() # TODO

        clock = pygame.time.Clock()
        running = True
        fps = 60
        frame = 0
        while running:
            frame += 1
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            window.update()
            # draw_scene(window, scene_manager, frame)
            # if frame == 4:
            #    running = False