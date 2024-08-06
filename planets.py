from __future__ import annotations

import pygame as pg

from typing import *
from pygame.gfxdraw import filled_polygon
from math import sqrt
from random import randint
from time import time

# color constants
BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (24, 43, 102)

# height of the bloc on the planet (the width is automatically calculated accordingly)
BLOCK_SIZE = 90

# dimensions of the screen
SCREENWIDTH, SCREENHEIGHT = 1500, 800
# length of the diagonal of the screen
SCREEN_DIAGONAL_LENGTH = sqrt(SCREENWIDTH**2 + SCREENHEIGHT**2)

# vector which coordinates are the screen's dimensions
SCREEN_VECTOR = pg.Vector2(SCREENWIDTH, SCREENHEIGHT)
# same as screen vector but pointing to the middle of the screen (= half the screen vector)
HALF_SCREEN_VECTOR = pg.Vector2(SCREENWIDTH//2, SCREENHEIGHT//2)
# this vector is used to position the final image correctly when it is rotated as it is bigger than the screen to be able to render everything onto it
# so you need to add this vector to anything being shown on screen except the player and UI
# don't bother with it unless you modify the camera and if you need help ask on discord
CALIBRATION_VECTOR = pg.Vector2((SCREEN_DIAGONAL_LENGTH-SCREENWIDTH)/2, (SCREEN_DIAGONAL_LENGTH-SCREENHEIGHT)/2) + HALF_SCREEN_VECTOR


class Block:
    def __init__(self, x:int, y:int, points:Union[float, float, float, float], block_type:pg.Surface) -> None:
        """ Class for handling blocks

        (0, 0) -- · · · -- d ----- a (x, y)
                           | block |
                           |       |
                           c ----- b

        Args:
            x (int): x position of the block in planet coordinates
            y (int): y position of the block in planet coordinates
            points (Union[float, float, float, float]): corners of the block
            block_type (pg.Surface): type of the block
        """
        self.x = x
        self.y = y

        self.points = points

        min_point = pg.Vector2(min(points[0].x, points[1].x, points[2].x, points[3].x), min(points[0].y, points[1].y, points[2].y, points[3].y))
        max_point = pg.Vector2(max(points[0].x, points[1].x, points[2].x, points[3].x), max(points[0].y, points[1].y, points[2].y, points[3].y))

        self.bounding_box = pg.Rect(min_point, max_point - min_point)

        self.longest_side = (points[1] - points[0]).length()

        self.block_type = block_type
       # TODO Pour l'instant le block_type est juste une image mais il faudrait changer ça en un dictionnaire pour que ce soit plus pratique
    
    def get_coords(self) -> Tuple[int, int]:
        """ Get the coordinate of the block in planet coordinates

        Returns:
            Tuple[int, int]: the coordinates of the block
        """
        return (self.x, self.y)


class Planet:
    def __init__(self, name:str, position:tuple[int, int], mass:float, num_layers:int, num_blocks_per_layer:int=-1, center_size:float=-1) -> None:
        """Class for generating planets

        Args:
            name (str): name of the planet
            position (tuple[int, int]): position of the center of the planet
            mass (float): mass of the planet (used for gravity)
            num_layers (int): number of layers
            num_blocks_per_layer (int): number of blocks per layer, leave -1 for automatic values
            center_size (float): size of the center of the planet, leave -1 for automatic values
        """
        self.name = name
        
        self.position = pg.Vector2(position)
        self.mass = mass    # used to calculate gravity

        self.num_layers = num_layers
        self.block_height = BLOCK_SIZE

        # auto
        if num_blocks_per_layer == -1:
            self.num_blocks_per_layer = num_layers * 5
        # manual
        else:
            if type(num_blocks_per_layer) != int:
                raise TypeError(f"value num_blocks_per_layer must be an integer and not : {type(num_blocks_per_layer)}")
            if num_blocks_per_layer < -1:
                raise ValueError("value num_blocks_per_layer must be positive")
            self.num_blocks_per_layer = num_blocks_per_layer

        # auto
        if center_size == -1:
            self.center_size = round(BLOCK_SIZE * num_layers / 2.7)
        # manual
        else:
            if type(center_size) != int:
                raise TypeError(f"value center_size must be an integer and not : {type(center_size)}")
            if center_size < -1:
                raise ValueError("value center_size must be positive")
            self.center_size = center_size
        
        # maximum x and y coordinates of the planet in planet coordinates
        self.max_x = self.num_blocks_per_layer
        self.max_y = self.num_layers

        # surface to render each block individually before showing it on screen
        self.block_rendering_surf = pg.Surface((sqrt(self.block_height**2 + self.block_height**2), sqrt(self.block_height**2 + self.block_height**2)))
        self.block_rendering_surf.set_colorkey(BLACK)

        self.air_image = pg.image.load(r"graphics\blocks\air\air.png").convert_alpha()
        self.grass_image = pg.image.load(r"graphics\blocks\grass\grass.png").convert_alpha()
        self.dirt_image = pg.image.load(r"graphics\blocks\dirt\dirt.png").convert_alpha()
        self.stone_image = pg.image.load(r"graphics\blocks\stone\stone.png").convert_alpha()
        
        # procedural generation of the planet
        self.blocks = self.generate_blocks()

    def generate_block(self, x:int, y:int, block_type:pg.Surface) -> Block:
        """Generate block object for coordinates (x, y) on a planet.

        Use this to generate new block objects that don't already exist.
        To change blocks in the planet (ex: player placing block) use set_block function.

        Args:
            x (int): x location on the planet coordinate system
            y (int): y location on the planet coordinate system
            block_type (pg.Surface): image surf of the block type

        Returns:
            Block: list of the four points making the block
        """

        if y == 0:
            raise(ValueError("Cannot generate block at the center of the planet"))
        
        # used to get the position of each point we start with a vector pointing up
        # and then rotate it to get the position of each blocks
        pointer = pg.Vector2(0, -1) * self.block_height
        
        # first we calculate point a (top left) and d (bottom left)
        pointer = pointer.rotate(360*x/self.max_x)
        a = pointer*y
        d = pointer*y - pointer

        # then we calculate point c (top right) and c (bottom right)
        pointer = pointer.rotate(360/self.max_x)
        b = pointer*y
        c = pointer*y - pointer

        # offset the points to be on the planet
        a, b, c, d = a + self.position, b + self.position, c + self.position, d + self.position

        # block object
        block = Block(x, y, [a, b, c, d], block_type)
        return block

    def generate_blocks(self) -> List[Block]:
        """ Procedurally generates the blocks of the planet.
        Blocks generate clockwise starting up.

        Returns:
            List[Block]: generated blocks
        """
        blocks = []
        
        # start generating blocks after the center
        start_layer = self.center_size // self.block_height

        for y in range(self.max_y):
            for x in range(self.max_x):
                if y >= 1:
                    
                    # stone
                    if start_layer < y < self.max_y - 14:
                        block = self.generate_block(x, y, self.stone_image)

                    # dirt
                    elif self.max_y - 14 <= y < self.max_y - 11:
                        block = self.generate_block(x, y, self.dirt_image)
                    
                    # grass
                    elif self.max_y - 11 <= y < self.max_y - 10:
                        block = self.generate_block(x, y, self.grass_image)

                    # air
                    elif self.max_y - 10 <= y <= self.max_y:
                        block = self.generate_block(x, y, self.air_image)
                    
                    else:
                        block = None

                    blocks.append(block)

        return blocks

    def regenerate(self) -> None:
        """Regenerate the planet procedurally (=reset the planet)
        """
        self.blocks = self.generate_blocks(self)

    def set_block(self, coords:tuple[int, int], block_type:pg.Surface) -> None:
        """Changes block type at coordinates.

        Use this the change already existing block.
        To create new blocks in the planet (ex: planet generation) use generate_block function.

        Args:
            coords (tuple[int, int]): coordinates of the block in planet coordinates
            block_type (pg.Surface): block type to change to
        """
        self.blocks[coords[0] + (coords[1]-1)*self.num_blocks_per_layer].block_type = block_type

    def get_block(self, coords:tuple[int, int]) -> Block:
        """ Get the block type at coordinates on the planet

        Args:
            coords (tuple[int, int]): coordinate of the block to change

        Returns:
            Block: returns the block that was removed
        """
        block_type = self.blocks[coords[0] + (coords[1]-1)*self.num_blocks_per_layer].block_type
        return block_type

    def render_block(self, screen:pg.Surface, block:Block, player_pos:pg.Vector2) -> None:
        """Renders a specific block on the screen

        Args:
            screen (pg.Surface): screen to render the block on
            block (Block): block to render
            player_pos (pg.Vector2): position of the player
        """
        # don't render air as it is invisible
        if block.block_type == self.air_image:
            return
        
        self.block_rendering_surf.fill(BLACK)

        # calculate the angle of the block
        angle = -360*(block.x+0.5)/self.max_x # we add 0.5 to get the angle of the middle of the block not the left of it

        # render the block
        filled_polygon(self.block_rendering_surf, [point - block.bounding_box.topleft for point in block.points], WHITE) # first draw a white block on the temporary surf
        scaled_surf = pg.transform.scale(block.block_type, (block.longest_side, self.block_height)) # scale the block image to be the right size
        rotated_surf = pg.transform.rotate(scaled_surf, angle) # then rotate it to be aligned with the planet
        self.block_rendering_surf.blit(rotated_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT) # finally render it on the temporary surf with a blending mode so that the block appears only where there is white

        # blit the block on the screen with offset
        screen.blit(self.block_rendering_surf, block.bounding_box.topleft - player_pos + CALIBRATION_VECTOR)

    def update(self) -> None:
        pass
        
    def draw(self, screen:pg.Surface, player:Player) -> None:
        """ Draw the planet on the screen based on player position

        Args:
            screen (pg.Surface): screen to draw the planet on
            player (Player): player position
        """
        num_blocks_being_displayed = 0

        player_pos = pg.Vector2(player.rect.center)

        # temporary planet center
        pg.draw.circle(screen, BLUE, self.position - player_pos + CALIBRATION_VECTOR, self.center_size)
        pg.draw.circle(screen, RED, self.position - player_pos + CALIBRATION_VECTOR, 10)

        for block in self.blocks:
            if block != None:
                # render boundaries
                left_boundary = player_pos.x - player.render_distance.x
                right_boundary = player_pos.x + player.render_distance.x
                upper_boundary = player_pos.y - player.render_distance.y
                lower_boundary = player_pos.y + player.render_distance.y

                # check if the block is inside the rotated screen and render it
                rotated_bounding_box = (pg.Vector2(block.bounding_box.center) - player_pos).rotate(360 - player.get_angle_to_planet()) + player_pos
                
                if (left_boundary <= rotated_bounding_box.x <= right_boundary and upper_boundary <= rotated_bounding_box.y <= lower_boundary):
                    
                    num_blocks_being_displayed += 1

                    self.render_block(screen, block, player_pos)
                    
        return num_blocks_being_displayed


class Player(pg.sprite.Sprite):
    def __init__(self, position:tuple[float, float]) -> None:
        """ Player class

        Args:
            position (tuple[float, float]): start position of the player
        """
        pg.sprite.Sprite.__init__(self)

        # vectors
        self.velocity = pg.Vector2(0, 0)

        # properties
        self.speed = 2
        self.jump_force = 20
        self.drag = 0.9
        self.max_velocity = 80

        self.closest_planet = None
        
        # render distance for the x and y directions
        self.render_distance = pg.Vector2(SCREENWIDTH/2 + BLOCK_SIZE, SCREENHEIGHT/2 + BLOCK_SIZE)

        # sprite
        self.image = pg.image.load(r"graphics\player\idle\player_down_idle\player_down_idle1.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (200, 200))

        self.rect = self.image.get_rect(center = position)
        self.hitbox = self.rect.inflate(5, 5)

    def get_angle_to_planet(self) -> float:
        """ Get the clockwise angle to the closest planet from the player where 0° is up

        Returns:
            float: angle in degrees
        """
        return -(self.rect.center-self.closest_planet.position).angle_to(pg.Vector2(0, -1))

    def check_collision(self) -> None:
        #TODO add collisions
        pass

    def gravity(self, planets:List[Planet]) -> None:
        """Applies force from planets surrounding the player

        Args:
            planets (List[Planet]): List of planets in the world
        """

        # variable used to check which planet is closest
        max_force = -1

        # apply force for each planet
        for planet in planets:
            # vector towards planet
            planet_dir = planet.position - self.rect.center

            l = planet_dir.length_squared()

            if planet_dir != pg.Vector2(0, 0):
                planet_dir = planet_dir.normalize()

            force = 6.67*10**-11 * planet.mass / max(l, 0.00001) # F = G*m/d^2
            planet_dir *= force

            # update closest planet variable
            if force > max_force:
                max_force = force
                self.closest_planet = planet

            # update velocity
            self.velocity += planet_dir

    def input(self) -> None:
        """Handle player input
        """
        input_dir = pg.Vector2(0, 0)

        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            input_dir.x = 1
        if keys[pg.K_q]:
            input_dir.x = -1
        if keys[pg.K_s]:
            input_dir.y = 1
        if keys[pg.K_z]:
            input_dir.y = -1

        if input_dir.length_squared() >= 1:
            input_dir = input_dir.normalize() * self.speed
        
        # align movement axis with rotation of the screen
        input_dir = input_dir.rotate(self.get_angle_to_planet())

        self.velocity += input_dir

    def jump(self) -> None:
        """ add vertical force to player
        """
        self.velocity += pg.Vector2(0, -1).rotate(self.get_angle_to_planet()) * self.jump_force

    def move(self, delta_time:float) -> None:
        """ Move the player by the velocity

        Args:
            delta_time (float): time between two frames
        """
        # apply drag
        self.velocity *= self.drag

        if self.velocity.length_squared() != 0:
            self.velocity = self.velocity.clamp_magnitude(self.max_speed)

        # move player rect
        self.rect.center += self.velocity * delta_time * 50

    def update(self, planets:List[Planet], delta_time) -> None:
        """ Update the player

        Args:
            planets (List[Planet]): list of all planets
            delta_time (_type_): delta time
        """

        self.gravity(planets) # apply gravity
        self.input() # handle inputs
        self.move(delta_time) # move the player

        self.check_collision()

    def draw(self, screen) -> None:
        """ Draw the player sprite on the screen

        Args:
            screen (_type_): screen to draw the player on
        """
        # player is drawn on the center of the screen
        screen.blit(self.image, (SCREENWIDTH//2 - self.image.get_width()//2, SCREENHEIGHT//2 - self.image.get_height()//2))


def blitRotate(surf:pg.Surface, image:pg.Surface, pivot_start:tuple[int, int], pivot_end:tuple[int, int], angle:float) -> None:
    """Rotates an image around a pivot and then blits it on the surf

    Args:
        surf (pg.Surface): target surface
        image (pg.Surface): image to rotate
        pivot_start (tuple[int, int]): pivot point
        pivot_end (tuple[int, int]): where the pivot point will be on the rotated image
        angle (float): angle of the rotation
    """
    image_rect = image.get_rect(topleft = (pivot_end[0] - pivot_start[0], pivot_end[1]-pivot_start[1]))
    offset_center_to_pivot = pg.math.Vector2(pivot_end) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pivot_end[0] - rotated_offset.x, pivot_end[1] - rotated_offset.y)
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)

def get_closest_block_on_planet(coords:pg.Vector2, planet:Planet) -> None:
    """ Get the closest block from given coordinates on a planet.

    Args:
        coords (pg.Vector2): coordinates to check the closest block from
        planet (Planet): planet to check for closest block
    """
    min_dst = float("inf")
    closest_block = None

    for block in planet.blocks:
        if block != None:
            distance = pg.Vector2(block.bounding_box.center).distance_squared_to(coords)
            if distance < min_dst:
                closest_block = block
                min_dst = distance

    return closest_block


class Main_game:
    def __init__(self) -> None:
        """ Main game class
        """
        # initialize pygame
        pg.init()
        pg.font.init()

        # initialize font
        self.font = pg.font.SysFont('freesansbold', 30)

        self.screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.internal_screen = pg.Surface((SCREEN_DIAGONAL_LENGTH, SCREEN_DIAGONAL_LENGTH))
        
        pg.display.set_caption("Planet Game")

        # initialize time
        self.clock = pg.time.Clock()
        self.current_time = time()

        self.running = True

        # angle of the screen
        self.current_angle = 0
        self.target_angle = 0

        self.player = Player((1000, -3110))

        # list of all planets
        self.planets = [Planet("Planet 1", (1000, 500), 6*10**15, 50)]

    def update(self) -> None:
        """ Update the game
        """
        # calculate deltaTime to make the game move at the same rate regardless of FPS
        self.delta_time = time() - self.current_time
        self.current_time = time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False
                if event.key == pg.K_SPACE:
                    self.player.jump()

            if event.type == pg.MOUSEBUTTONDOWN:
                # place block
                if event.button == 1:
                    corrected_pos = (pg.Vector2(pg.mouse.get_pos()) - HALF_SCREEN_VECTOR).rotate(self.player.get_angle_to_planet()) + self.player.rect.center
                    touched_block = get_closest_block_on_planet(corrected_pos, self.player.closest_planet)
                    self.player.closest_planet.set_block(touched_block.get_coords(), self.player.closest_planet.stone_image)

                # break block
                if event.button == 3:
                    corrected_pos = (pg.Vector2(pg.mouse.get_pos()) - HALF_SCREEN_VECTOR).rotate(self.player.get_angle_to_planet()) + self.player.rect.center
                    touched_block = get_closest_block_on_planet(corrected_pos, self.player.closest_planet)
                    self.player.closest_planet.set_block(touched_block.get_coords(), self.player.closest_planet.air_image)
        
        # update player
        self.player.update(self.planets, self.delta_time)

        # update planets
        for planet in self.planets:
            planet.update()

    def draw(self) -> None:
        """ Draw everything on the screen
        """
        self.internal_screen.fill(DARKBLUE) # background
        
        num_blocks_being_displayed = 0

        # draw planets
        for planet in self.planets:
            num_blocks_being_displayed += planet.draw(self.internal_screen, self.player)

        # rotate the screen so that the closest planet is always down
        self.target_angle = self.player.get_angle_to_planet()

        # update target_angle to avoid sudden jumps in the rotation
        if abs(self.target_angle - self.current_angle) > abs(self.target_angle - self.current_angle - 360):
            self.target_angle = self.target_angle-360
        if abs(self.target_angle - self.current_angle) > abs(self.target_angle - self.current_angle + 360):
            self.target_angle = self.target_angle+360

        angle_diff = (abs(self.current_angle - self.target_angle) % 360)/360

        # lerp to target angle based on angle difference
        self.current_angle = (pg.math.lerp(self.current_angle, self.target_angle, 1/(angle_diff+1)-0.5)+90)%360-90

        # rotate screen
        blitRotate(self.screen, self.internal_screen, 
                   CALIBRATION_VECTOR,
                   HALF_SCREEN_VECTOR, 
                   self.current_angle)

        # draw player
        self.player.draw(self.screen)
        
        # UI
        if round(self.clock.get_fps()) <= 30:
            self.screen.blit(self.font.render(f"FPS : {round(self.clock.get_fps())} (il faudrait optimiser ça)", False, RED), (20, 20))
        else:
            self.screen.blit(self.font.render(f"FPS : {round(self.clock.get_fps())}", False, GREEN), (20, 20))

        self.screen.blit(self.font.render(f"Number of blocks rendered : {num_blocks_being_displayed}", False, WHITE), (20, 50))
        self.screen.blit(self.font.render(f"Coordinates : {self.player.rect.center}  Orientation : {round(self.player.get_angle_to_planet())}°", False, WHITE), (20, 70))

        closest_block = get_closest_block_on_planet(self.player.rect.center, self.player.closest_planet)
        
        if closest_block != None:
            self.screen.blit(self.font.render(f"Coordinates on planet : {closest_block.get_coords()}", False, WHITE), (20, 90))
        
        pg.display.flip()

    def run(self) -> None:
        """Main game loop
        """
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()


if __name__ == "__main__":
    game = Main_game()
    game.run()
