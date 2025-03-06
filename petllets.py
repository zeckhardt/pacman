import pygame
from vector import Vector2
from constants import *
import numpy as np

class Pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector2(column * TILE_WIDTH, row * TILE_HEIGHT)
        self.color = WHITE
        self.radius = int(4 * TILE_WIDTH / 16)
        self.collide_radius = int(4 * TILE_WIDTH / 16)
        self.points = 10
        self.visible = True
        
    def render(self, screen):
        if self.visible:
            p = self.position.as_int()
            pygame.draw.circle(screen, self.color, p, self.radius)
            
            
class PowerPellet(Pellet):
    def __init__(self, row, column):
        super().__init__(row, column)
        self.name = POWER_PELLET
        self.radius = int(8 * TILE_WIDTH / 16)
        self.points = 50
        self.flash_time = 0.2
        self.timer = 0
    
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flash_time:
            self.visible = not self.visible
            self.timer = 0
            
class PelletGroup(object):
    def __init__(self, pelletfile):
        self.pellet_list = []
        self.powerpellets = []
        self.create_pellet_list(pelletfile)
        self.num_eaten = 0
        
    def update(self, dt):
        for powerpellet in self.powerpellets:
            powerpellet.update(dt)
    
    def create_pellet_list(self, pelletfile):
        data = self.read_pelletfile(pelletfile)
        for row_idx, row in enumerate(data):
            for col_idx, cell in enumerate(row):
                if cell in {'.', '+'}:
                    self.pellet_list.append(Pellet(row_idx, col_idx))
                elif cell in {'P', 'p'}:
                    pp = PowerPellet(row_idx, col_idx)
                    self.pellet_list.append(pp)
                    self.powerpellets.append(pp)
                    
    def read_pelletfile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1')

    def is_empty(self):
        if len(self.pellet_list) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pellet_list:
            pellet.render(screen)