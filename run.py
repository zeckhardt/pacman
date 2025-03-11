import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from petllets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.text_group = TextGroup()
        
    def next_level(self):
        self.show_entities()
        self.level += 1
        self.pause.paused = True
        self.start_game()
        self.text_group.update_level(self.level)

    def restart_game(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.start_game()
        self.score = 0
        self.text_group.update_score(self.score)
        self.text_group.update_level(self.level)
        self.text_group.setup_text(READY_TXT)
        
    def reset_level(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.text_group.show_text(READY_TXT)

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
        self.pacman = Pacman(self.nodes.get_node_from_tiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.get_start_node_temp(), self.pacman)
        self.ghosts.blinky.set_start_node(self.nodes.get_node_from_tiles(2+11.5, 0+14))
        self.ghosts.pinky.set_start_node(self.nodes.get_node_from_tiles(2+11.5, 3+14))
        self.ghosts.inky.set_start_node(self.nodes.get_node_from_tiles(0+11.5, 3+14))
        self.ghosts.clyde.set_start_node(self.nodes.get_node_from_tiles(4+11.5, 3+14))
        self.ghosts.set_spawn_node(self.nodes.get_node_from_tiles(2+11.5, 3+14))
        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.nodes.deny_access_list(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.deny_access_list(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.start_node.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.start_node.deny_access(LEFT, self.ghosts.clyde)
        self.nodes.deny_access_list(12, 14, UP, self.ghosts)
        self.nodes.deny_access_list(15, 14, UP, self.ghosts)
        self.nodes.deny_access_list(12, 26, UP, self.ghosts)
        self.nodes.deny_access_list(15, 26, UP, self.ghosts)
    
    def update(self):
        # amount of time since last update() call
        dt = self.clock.tick(30) / 1000.0
        self.text_group.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.pacman.update(dt)
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.check_pellet_events()
            self.check_ghost_events()
            self.check_fruit_events()
        after_pause_method = self.pause.update(dt)
        if after_pause_method is not None:
            after_pause_method()
        self.check_events()
        self.render()
        
        
    def update_score(self, points):
        self.score += points
        self.text_group.update_score(self.score)

    def check_events(self):
        # exit the game
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()    
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.set_pause(player_paused=True)
                        if not self.pause.paused:
                            self.text_group.hide_text()
                            self.show_entities()
                        else:
                            self.text_group.show_text(PAUSE_TXT)
                            self.hide_entities()    
    
    def check_fruit_events(self):
        if self.pellets.num_eaten == 50 or self.pellets.num_eaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(9,20))
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.update_score(self.fruit.points)
                self.text_group.add_text(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None
    
    def check_ghost_events(self):
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.update_score(ghost.points)
                    self.text_group.add_text(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.update_points()
                    self.pause.set_pause(pause_time=1, func=self.show_entities)
                    ghost.start_spawn()
                    self.nodes.allow_home_access(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.text_group.show_text(GAME_OVER_TXT)
                            self.pause.set_pause(pause_time=3, func=self.restart_game)
                        else:
                            self.pause.set_pause(pause_time=3, func=self.reset_level)
                
    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            self.update_score(pellet.points)
            if self.pellets.num_eaten == 30:
                self.ghosts.inky.start_node.allow_access(RIGHT, self.ghosts.inky)
            if self.pellets.num_eaten == 70:
                self.ghosts.clyde.start_node.allow_access(LEFT, self.ghosts.clyde)
            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWER_PELLET:
                self.ghosts.start_freight()
            if self.pellets.is_empty():
                self.hide_entities()
                self.pause.set_pause(pause_time=3, func=self.next_level)
                
    def show_entities(self):
        self.pacman.visible = True
        self.ghosts.show()
        
    def hide_entities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def render(self):
        self.screen.blit(self.background, (0,0))
        self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.text_group.render(self.screen)
        pygame.display.update()


if __name__ == '__main__':
    game = GameController()
    game.start_game()
    while True:
        game.update()