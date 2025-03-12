import pygame
from constants import *
import numpy as np

BASE_TILE_WIDTH = 16
BASE_TILE_HEIGHT = 16

class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("spritesheet.png").convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASE_TILE_WIDTH * TILE_WIDTH)
        height = int(self.sheet.get_height() / BASE_TILE_HEIGHT * TILE_HEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))
        
        
    def get_image(self, x, y, width, height):
        x *= TILE_WIDTH
        y *= TILE_HEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())
    
    
class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity
        self.entity.image = self.get_start_image()
        
    def get_start_image(self):
        return self.get_image(8, 0)
    
    def get_image(self, x, y):
        return super().get_image(x, y, 2 * TILE_WIDTH, 2 * TILE_HEIGHT)
    
    
class GhostSprites(Spritesheet):
    def __init__(self, entity):
        super().__init__()
        self.x = {BLINKY: 0, PINKY: 2, INKY: 4, CLYDE:6}
        self.entity = entity
        self.entity.image = self.get_start_image()
        
    def get_start_image(self):
        return self.get_image(self.x[self.entity.name], 4)
    
    def get_image(self, x, y):
        return super().get_image(x, y, 2 * TILE_WIDTH, 2 * TILE_HEIGHT)
        
        
class FruitSprites(Spritesheet):
    def __init__(self, entity):
        super().__init__()
        self.entity = entity
        self.entity.image = self.get_start_image()
        
    def get_start_image(self):
        return self.get_image(16, 8)
    
    def get_image(self, x, y):
        return super().get_image(x, y, 2 * TILE_WIDTH, 2 * TILE_HEIGHT)
        
        
class LifeSprites(Spritesheet):
    def __init__(self, num_lives):
        super().__init__()
        self.reset_lives(num_lives)
        
    def remove_image(self):
        if len(self.images) > 0:
            self.images.pop(0)
            
    def reset_lives(self, num_lives):
        self.images = []
        for i in range(num_lives):
            self.images.append(self.get_image(0,0))
            
    def get_image(self, x, y):
        return super().get_image(x, y, 2 * TILE_WIDTH, 2 * TILE_HEIGHT)
    
    
class MazeSprites(Spritesheet):
    def __init__(self, maze_file, rot_file):
        super().__init__()
        self.data = self.read_maze_file(maze_file)
        self.rot_data = self.read_maze_file(rot_file)
        
    def get_image(self, x, y):
        return super().get_image(x, y, TILE_WIDTH, TILE_HEIGHT)
    
    def read_maze_file(self, maze_file):
        return np.loadtxt(maze_file, dtype="<U1")
    
    def construct_background(self, background, y):
        for row_idx, row_data in enumerate(self.data):
            for col_idx, tile_value in enumerate(row_data):
                position = (col_idx * TILE_WIDTH, row_idx * TILE_HEIGHT)
                
                if tile_value.isdigit():
                    x = int(tile_value) + 12
                    sprite = self.get_image(x, y)
                    
                    # Get rotation value and rotate sprite
                    rotval = int(self.rot_data[row_idx][col_idx])
                    sprite = self.rotate(sprite, rotval)
                        
                    background.blit(sprite, position)
                    
                elif tile_value == '=':
                    sprite = self.get_image(10, 8)
                    background.blit(sprite, position)
        
        return background
    
    def rotate(self, sprite, value):
        return pygame.transform.rotate(sprite, value * 90)