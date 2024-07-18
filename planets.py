import pygame as pg
from typing import *

from pygame.gfxdraw import filled_polygon
from math import sqrt
from random import randint
from time import time


BLACK = ( 0, 0, 0)
TRANSPARENT_BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255)
TRANSPARENT_WHITE = (255, 255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (24, 43, 102)

BLOCK_SIZE = 90

SCREENWIDTH, SCREENHEIGHT = 1500, 800
SCREEN_DIAGONAL_LENGTH = sqrt(SCREENWIDTH**2 + SCREENHEIGHT**2)+100

SCREEN_VECTOR = pg.Vector2(SCREENWIDTH, SCREENHEIGHT)
HALF_SCREEN_VECTOR = pg.Vector2(SCREENWIDTH//2, SCREENHEIGHT//2)
CALIBRATION_VECTOR = pg.Vector2((SCREEN_DIAGONAL_LENGTH-SCREENWIDTH)/2, (SCREEN_DIAGONAL_LENGTH-SCREENHEIGHT)/2) + HALF_SCREEN_VECTOR #idk why


class Block:
    def __init__(self, x:int, y:int, points:Union[float, float, float, float], block_type:pg.Surface) -> None:
        """ Class for handling blocks

        Args:
            x (int): x position of the block in planet coordinates
            y (int): y position of the block in planet coordinates
            points (Union[float, float, float, float]): corners of the block
            block_type (pg.Surface): type of the block
        """
        self.x = x
        self.y = y

        self.points = points
        self.topleft = pg.Vector2(min(points[0].x, points[1].x, points[2].x, points[3].x),
                                  min(points[0].y, points[1].y, points[2].y, points[3].y))
        self.center = pg.Vector2(points[0] + points[1] + points[2] + points[3])/4
        self.longest_side = (points[1] - points[0]).length()

        self.block_type = block_type
       # TODO Pour l'instant le block_type est juste une image mais il faudrait changer ça en un dictionnaire pour que ce soit plus pratique
    
    def get_coords(self):
        return (self.x, self.y)


class Planet:
    def __init__(self, name:str, position:tuple[int, int], mass:float, num_layers:int, auto_values:bool=True, num_blocks_per_layer:int=-1, center_size:float=-1) -> None:
        """Class for generating planets

        Args:
            name (str): name of the planet
            position (tuple[int, int]): position of the center of the planet
            mass (float): mass of the planet (used for gravity)
            num_blocks_per_layer (int): number of blocks per layer
            num_layers (int): number of layers
            center_size (float): size of the center of the planet
            block_height (float): height of each block on the planet
        """
        self.name = name
        
        self.position = pg.Vector2(position)
        self.mass = mass

        if auto_values:
            self.num_layers = num_layers
            self.block_height = BLOCK_SIZE
            self.num_blocks_per_layer = num_layers * 6
            self.center_size = round(BLOCK_SIZE * num_layers / 2.7)
        else:
            self.num_layers = num_layers
            self.block_height = BLOCK_SIZE
            self.num_blocks_per_layer = num_blocks_per_layer
            self.center_size = center_size
        
        self.max_x = self.num_blocks_per_layer - 1
        self.max_y = self.num_layers - 1

        self.block_rendering_surf = pg.Surface((self.block_height*2, self.block_height*2))
        self.block_rendering_surf.set_colorkey(BLACK)
        
        self.render_distance = pg.Vector2(100, 100) # higher = less blocks rendered

        self.air_image = pg.image.load(r"graphics\blocks\air\air.png").convert_alpha()
        self.grass_image = pg.image.load(r"graphics\blocks\grass\grass.png").convert_alpha()
        self.dirt_image = pg.image.load(r"graphics\blocks\dirt\dirt.png").convert_alpha()
        self.stone_image = pg.image.load(r"graphics\blocks\stone\stone.png").convert_alpha()
        
        self.blocks = self.generate_blocks()

    def generate_block(self, x, y, block_type) -> Block:
        """Returns polygon points for coordinates (x, y) on a planet
        
        (0, 0) -- - - - -- d ---- a (x, y)
                        |      |
                        |      |
                        c ---- b

        Args:
            x (int): x location on the planet coordinate system
            y (int): y location on the planet coordinate system
            planet (Planet): planet the polygon is on

        Returns:
            Union[float, float, float, float]: list of the four points making the block
        """
        if y == 0:
            raise(ValueError("Cannot generate polygon at the center of the planet"))
        
        pointer = pg.Vector2(1, 0) * self.block_height*y
        
        pointer = pointer.rotate(360*x/self.num_blocks_per_layer)
        a = pointer + self.position
        d = pointer - pointer/y + self.position

        pointer = pointer.rotate(360/self.num_blocks_per_layer)
        b = pointer + self.position
        c = pointer - pointer/y + self.position

        block = Block(x, y, [a, b, c, d], block_type)
        return block

    def generate_blocks(self) -> List[Block]:
        blocks = []
        
        start_layer = self.center_size // self.block_height

        for y in range(self.num_layers):
            for x in range(self.num_blocks_per_layer):
                if y >= 1:
                    
                    # stone
                    if start_layer < y < self.num_layers - 14:
                        block = self.generate_block(x, y, self.stone_image)

                    # dirt
                    elif self.num_layers - 14 <= y < self.num_layers - 11:
                        block = self.generate_block(x, y, self.dirt_image)
                    
                    # grass
                    elif self.num_layers - 11 <= y < self.num_layers - 10:
                        block = self.generate_block(x, y, self.grass_image)

                    # air
                    elif self.num_layers - 10 <= y <= self.num_layers:
                        block = self.generate_block(x, y, self.air_image)
                    
                    else:
                        block = None

                    blocks.append(block)

        return blocks

    def regenerate(self):
        self.blocks = self.generate_blocks(self)

    def set_block(self, coords:tuple[int, int], block_type:pg.Surface):
        """Changes block type at coordinates

        Args:
            coords (tuple[int, int]): coordinates of the block in planet coordinates
            block_type (pg.Surface): block type to change to
        """
        self.blocks[coords[0] + (coords[1]-1)*self.num_blocks_per_layer].block_type = block_type

    def remove_block(self, coords:tuple[int, int]) -> Block:
        """ Changes the block at the coordinates to air

        Args:
            coords (tuple[int, int]): coordinate of the block to change

        Returns:
            Block: returns the block that was removed
        """
        block_type = self.blocks[coords[0] + (coords[1]-1)*self.num_blocks_per_layer].block_type
        self.blocks[coords[0] + (coords[1]-1)*self.num_blocks_per_layer].block_type = self.air_image
        return block_type

    def render_block(self, screen, block, player_offset):
        if block.block_type == self.air_image:
            return
        self.block_rendering_surf.fill(BLACK)

        angle = ((-360*block.x/self.num_blocks_per_layer - 90) + (-360*(block.x+1)/self.num_blocks_per_layer - 90))/2

        filled_polygon(self.block_rendering_surf, [point - block.topleft for point in block.points], WHITE)
        self.block_rendering_surf.blit(pg.transform.rotate(pg.transform.scale(block.block_type, (block.longest_side, self.block_height)), angle), (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        screen.blit(self.block_rendering_surf, block.topleft + player_offset + CALIBRATION_VECTOR)

    def update(self):
        pass
        
    def draw(self, screen, player):
        num_blocks_being_displayed = 0

        self.block_rendering_surf.fill(BLACK)

        player_offset = -pg.Vector2(player.rect.center)

        pg.draw.circle(screen, BLUE, player_offset + CALIBRATION_VECTOR + self.position, self.center_size)
        pg.draw.circle(screen, RED, player_offset + CALIBRATION_VECTOR + self.position, 10)

        for block in self.blocks:
            if block != None:
                # check if polygon is inside the screen to prevent crashing
                left_boundary = -player_offset.x+self.render_distance.x - CALIBRATION_VECTOR.x
                right_boundary = SCREEN_DIAGONAL_LENGTH-self.render_distance.x - player_offset.x - CALIBRATION_VECTOR.x
                upper_boundary = -player_offset.y+self.render_distance.y - CALIBRATION_VECTOR.y
                lower_boundary = SCREEN_DIAGONAL_LENGTH-self.render_distance.y - player_offset.y - CALIBRATION_VECTOR.y

                if (left_boundary <= block.center.x <= right_boundary and upper_boundary <= block.center.y <= lower_boundary):
                    
                    num_blocks_being_displayed += 1

                    self.render_block(screen, block, player_offset)


            # if i == self.num_blocks_per_layer:
            #     print("first : ", start_layer+2)
            #     print("other : ", block_at_coords(0, start_layer+2, self))
            # else:
            #     pg.draw.circle(screen, GREEN, self.points[i] + player_offset + CALIBRATION_VECTOR, 2)
                    

        return num_blocks_being_displayed


class Player(pg.sprite.Sprite):
    def __init__(self, position:tuple[float, float]):
        pg.sprite.Sprite.__init__(self)
        self.dir = pg.Vector2(0, 0)
        self.velocity = pg.Vector2(0, 0)

        self.speed = 2
        self.jump_force = 30
        self.drag = 0.9

        self.closest_planet = None

        self.image = pg.image.load(r"graphics\player\idle\player_down_idle\player_down_idle1.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (200, 200))

        self.rect = self.image.get_rect(center = position)
        self.hitbox = self.rect.inflate(5, 5)

    def get_downward_angle(self) -> float:
        """ Get the angle to the closest planet from the player

        Returns:
            float: angle in degrees
        """
        return -(self.rect.center-self.closest_planet.position).angle_to(pg.Vector2(0, -1))

    def check_collision(self):
        #TODO add collisions
        pass

    def gravity(self, planets:List[Planet]):
        """Applies force from planets surrounding the player

        Args:
            planets (List[Planet]): List of planets in the world
        """

        # variable used to check which planet is closest
        max_force = -1

        # apply force for each planet
        for planet in planets:
            # vector towards planet
            self.dir = planet.position - self.rect.center

            l = self.dir.length_squared()

            if self.dir != pg.Vector2(0, 0):
                self.dir = self.dir.normalize()

            force = 6.67*10**-11 * planet.mass / max(l, 0.00001)
            self.dir *= force # F = G*m/d^2

            # update closest planet variable
            if force > max_force:
                max_force = force
                self.closest_planet = planet

            self.velocity += self.dir

    def input(self):
        self.dir.x = 0
        self.dir.y = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.dir.x = 1
        if keys[pg.K_q]:
            self.dir.x = -1
        if keys[pg.K_s]:
            self.dir.y = 1
        if keys[pg.K_z]:
            self.dir.y = -1

        if self.dir.length() >= 1:
            self.dir = self.dir.normalize() * self.speed
        
        # align movement axis with rotation of the screen
        self.dir = self.dir.rotate(self.get_downward_angle())

        self.velocity += self.dir

    def jump(self):
        self.velocity += (self.rect.center - self.closest_planet.position).normalize() * self.jump_force

    def move(self, delta_time):
        self.velocity *= self.drag

        if self.velocity.length_squared() != 0:
            self.velocity = self.velocity.clamp_magnitude(80)
        self.rect.center += self.velocity * delta_time * 50

        # temporary collision
        # if self.rect.bottom >= -500:
        #     self.rect.bottom = -500

    def update(self, planet_centers, delta_time):

        self.gravity(planet_centers)
        self.input()
        self.move(delta_time)

        self.check_collision()

    def draw(self, screen):
        screen.blit(self.image, (SCREENWIDTH//2 - self.image.get_width()//2, SCREENHEIGHT//2 - self.image.get_height()//2))


def blitRotate(surf:pg.Surface, image:pg.Surface, origin:tuple[int, int], pivot:tuple[int, int], angle:float):
    """Rotates an image around a pivot and then blits it on the surf

    Args:
        surf (pg.Surface): target surface
        image (pg.Surface): image to rotate
        origin (tuple[int, int]): where to pivot point will be on the rotated image
        pivot (tuple[int, int]): pivot point
        angle (float): angle of the rotation
    """
    image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pg.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)

def get_closest_block_on_planet(coords:pg.Vector2, planet:Planet):
    min_dst = float("inf")
    closest_block = None
    for block in planet.blocks:
        if block != None:
            if block.center.distance_squared_to(coords) < min_dst:
                closest_block = block
                min_dst = block.center.distance_squared_to(coords)

    return closest_block


class Main_game:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.font = pg.font.SysFont('freesansbold', 30)
        self.screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.internal_screen = pg.Surface((SCREEN_DIAGONAL_LENGTH, SCREEN_DIAGONAL_LENGTH))
        pg.display.set_caption("Game")

        self.clock = pg.time.Clock()
        self.current_time = time()

        self.running = True

        self.current_angle = 0
        self.target_angle = 0

        self.player = Player((1000, -3110))

        # list of all planets
        self.planets = [Planet("Planet 1", (1000, 500), 6*10**15, 50)]

    def update(self):
        # calculate deltaTime to make the speed go at the same rate regardless of FPS
        self.delta_time = time() - self.current_time
        self.current_time = time()

        for event in pg.event.get():  # permet de recuperer les evenements (genre appuit des touches ect)
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
                    corrected_pos = (pg.Vector2(pg.mouse.get_pos()) - HALF_SCREEN_VECTOR).rotate(self.player.get_downward_angle()) + self.player.rect.center
                    touched_block = get_closest_block_on_planet(corrected_pos, self.player.closest_planet)
                    self.player.closest_planet.set_block(touched_block.get_coords(), self.player.closest_planet.stone_image)

                # break block
                if event.button == 3:
                    corrected_pos = (pg.Vector2(pg.mouse.get_pos()) - HALF_SCREEN_VECTOR).rotate(self.player.get_downward_angle()) + self.player.rect.center
                    touched_block = get_closest_block_on_planet(corrected_pos, self.player.closest_planet)
                    self.player.closest_planet.remove_block(touched_block.get_coords())
                
        self.player.update(self.planets, self.delta_time)

        for planet in self.planets:
            planet.update()

    def draw(self):
        self.internal_screen.fill(DARKBLUE)
        
        num_blocks_being_displayed = 0

        for planet in self.planets:
            num_blocks_being_displayed += planet.draw(self.internal_screen, self.player)

        # rotate the screen so that the closest planet is always down
        self.target_angle = self.player.get_downward_angle()

        if abs(self.target_angle - self.current_angle) > abs(self.target_angle - self.current_angle - 360):
            self.target_angle = self.target_angle-360
        if abs(self.target_angle - self.current_angle) > abs(self.target_angle - self.current_angle + 360):
            self.target_angle = self.target_angle+360

        angle_diff = (abs(self.current_angle - self.target_angle) % 360)/360

        # lerp to target angle based on angle difference
        self.current_angle = (pg.math.lerp(self.current_angle, self.target_angle, 1/(angle_diff+1)-0.5)+90)%360-90

        # rotate screen
        blitRotate(self.screen, self.internal_screen, 
                   HALF_SCREEN_VECTOR,
                   CALIBRATION_VECTOR, 
                   self.current_angle)

        self.player.draw(self.screen)
        
        self.screen.blit(self.font.render(f"FPS : {round(self.clock.get_fps())} (il faudrait optimiser ça)", False, GREEN), (20, 20))
        self.screen.blit(self.font.render(f"Number of blocks rendered : {num_blocks_being_displayed}", False, WHITE), (20, 50))
        self.screen.blit(self.font.render(f"Coordinates : {self.player.rect.center}  Orientation : {round(self.player.get_downward_angle())}°", False, WHITE), (20, 70))

        closest_block = get_closest_block_on_planet(self.player.rect.center, self.player.closest_planet)
        
        if closest_block != None:
            self.screen.blit(self.font.render(f"Coordinates on planet : {closest_block.get_coords()}", False, WHITE), (20, 90))
        
        pg.display.flip()

    def run(self):
        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()


if __name__ == "__main__":
    game = Main_game()
    game.run()
