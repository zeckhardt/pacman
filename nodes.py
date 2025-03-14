import pygame
from vector import Vector2
from constants import *
import numpy as np

class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {UP:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       DOWN:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       LEFT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
                       RIGHT:[PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT]}
        
    def deny_access(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)
            
    def allow_access(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)
    
    def render(self, screen):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.as_tuple()
                line_end = self.neighbors[n].position.as_tuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)
                

class NodeGroup(object):
    def __init__(self, level):
        self.node_list = []
        self.level = level
        self.nodes_LUT = {}
        self.node_symbols = ['+', 'P', 'n']
        self.path_symbols = ['.', '-', '|', 'p']
        data = self.read_maze_file(level)
        self.create_node_table(data)
        self.connect_horizontally(data)
        self.connect_vertically(data)
        self.homekey = None
    
    def render(self, screen):
        for node in self.nodes_LUT.values():
            node.render(screen)
            
    def read_maze_file(self, textfile):
        """
        Read a new maze text file.
        The maze has four symbols:
        - "X": empty space
        - "+": Node
        - ".": Vertical/Horizontal path
        """
        return np.loadtxt(textfile, dtype='<U1')
    
    def create_node_table(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    x, y = self.construct_key(col + xoffset, row + yoffset)
                    self.nodes_LUT[(x,y)] = Node(x,y)
                    
    def construct_key(self, x, y):
        return x * TILE_WIDTH, y * TILE_HEIGHT
    
    def connect_horizontally(self, data, xoffset=0, yoffset=0):
        for row_idx, row in enumerate(data):
            key = None
            for col_idx, value in enumerate(row):
                if value in self.node_symbols:
                    if key is None:
                        key = self.construct_key(col_idx + xoffset, row_idx + yoffset)
                    else:
                        other_key = self.construct_key(col_idx + xoffset, row_idx + yoffset)
                        self.nodes_LUT[key].neighbors[RIGHT] = self.nodes_LUT[other_key]
                        self.nodes_LUT[other_key].neighbors[LEFT] = self.nodes_LUT[key]
                        key = other_key  # Update key to continue chain
                elif value not in self.path_symbols:
                    key = None  # Reset if an invalid symbol is encountered

                    
    def connect_vertically(self, data, xoffset=0, yoffset=0):
        for col_idx, col in enumerate(zip(*data)):  # Transpose by iterating over columns
            key = None
            for row_idx, value in enumerate(col):
                if value in self.node_symbols:
                    if key is None:
                        key = self.construct_key(col_idx + xoffset, row_idx + yoffset)
                    else:
                        other_key = self.construct_key(col_idx + xoffset, row_idx + yoffset)
                        self.nodes_LUT[key].neighbors[DOWN] = self.nodes_LUT[other_key]
                        self.nodes_LUT[other_key].neighbors[UP] = self.nodes_LUT[key]
                        key = other_key  # Continue chain
                elif value not in self.path_symbols:
                    key = None  # Reset connection
                    
    def get_node_from_pixels(self, xpixel, ypixel):
        if(xpixel, ypixel) in self.nodes_LUT.keys():
            return self.nodes_LUT[(xpixel, ypixel)]
        return None
    
    def get_node_from_tiles(self, col, row):
        x, y = self.construct_key(col, row)
        if (x, y) in self.nodes_LUT.keys():
            return self.nodes_LUT[(x, y)]
        return None
    
    def get_start_node_temp(self):
        return list(self.nodes_LUT.values())[0]
    
    def set_portal_pair(self, pair1, pair2):
        key1 = self.construct_key(*pair1)
        key2 = self.construct_key(*pair2)
        if key1 in self.nodes_LUT.keys() and key2 in self.nodes_LUT.keys():
            self.nodes_LUT[key1].neighbors[PORTAL] = self.nodes_LUT[key2]
            self.nodes_LUT[key2].neighbors[PORTAL] = self.nodes_LUT[key1]
            
    def create_home_nodes(self, xoffset, yoffset):
        homedata = np.array([
            ['X','X','+','X','X'],
            ['X','X','.','X','X'],
            ['+','X','.','X','+'],
            ['+','.','+','.','+'],
            ['+','X','X','X','+']
        ])
        self.create_node_table(homedata, xoffset, yoffset)
        self.connect_horizontally(homedata, xoffset, yoffset)
        self.connect_vertically(homedata, xoffset, yoffset)
        self.homekey = self.construct_key(xoffset+2, yoffset)
        return self.homekey
    
    def connect_home_nodes(self, homekey, otherkey, direction):
        key = self.construct_key(*otherkey)
        self.nodes_LUT[homekey].neighbors[direction] = self.nodes_LUT[key]
        self.nodes_LUT[key].neighbors[direction*-1] = self.nodes_LUT[homekey]
        
    def deny_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.deny_access(direction, entity)
    
    def allow_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.allow_access(direction, entity)
            
    def deny_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.deny_access(col, row, direction, entity)
            
    def allow_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.allow_access(col, row, direction, entity)
            
    def deny_home_access(self, entity):
        self.nodes_LUT[self.homekey].deny_access(DOWN, entity)
        
    def allow_home_access(self, entity):
        self.nodes_LUT[self.homekey].allow_access(DOWN, entity)
        
    def deny_home_access_list(self, entities):
        for entity in entities:
            self.deny_home_access(entity)
            
    def allow_home_access_list(self, entities):
        for entity in entities:
            self.allow_home_access(entity)