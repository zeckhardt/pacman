import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from petllets import PelletGroup
from ghosts import Ghost

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()

    def set_background(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)
        
    def start_game(self):
        self.set_background()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.set_portal_pair((0,17), (27,17))
        homekey = self.nodes.create_home_nodes(11.5, 14)
        self.nodes.connect_home_nodes(homekey, (12,14), LEFT)
        self.nodes.connect_home_nodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.get_start_node_temp())
        self.pellets = PelletGroup("maze1.txt")
        self.ghost = Ghost(self.nodes.get_start_node_temp(), self.pacman)
        self.ghost.set_spawn_node(self.nodes.get_node_from_tiles(2+11.5, 3+14))
    
    def update(self):
        # amount of time since last update() call
        dt = self.clock.tick(30) / 1000.0
        self.pacman.update(dt)
        self.ghost.update(dt)
        self.pellets.update(dt)
        self.check_pellet_events()
        self.check_ghost_events()
        self.check_events()
        self.render()

    def check_events(self):
        # exit the game
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
    
    def check_ghost_events(self):
        if self.pacman.collide_ghost(self.ghost):
            if self.ghost.mode.current is FREIGHT:
                self.ghost.start_spawn()
                
    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWER_PELLET:
                self.ghost.start_freight()

    def render(self):
        self.screen.blit(self.background, (0,0))
        self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        self.pacman.render(self.screen)
        self.ghost.render(self.screen)
        pygame.display.update()


if __name__ == '__main__':
    game = GameController()
    game.start_game()
    while True:
        game.update()