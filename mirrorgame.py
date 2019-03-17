import os
import pygame
import sys

from random import Random
from pygame.locals import *
from typing import *

# Globals
SCREENRECT = Rect(0, 0, 1024, 768)  # Screen position and resolution
TILESIZE = 64  # The size of each tile.
combat = False  # When this is True, use the combat loop.
MAIN_DISPLAY = pygame.Surface(SCREENRECT.size)
SNOW_TILES = os.path.join('tilesets', 'snow_tiles.png')
ANNA_OVERWORLD = os.path.join('sprites', 'anna_basic_overworld.png')
FRAMEDELAY = 3
ENTITIES = pygame.sprite.RenderUpdates()  # Sprite group for Entities (Player, Statics, Mobs, etc.).
COLLISIONS: List[Rect] = list()


# Collects data from a sprite sheet.
class SpriteSheet:
    def __init__(self, filename: str, surface: pygame.Surface):
        self.sheet = pygame.image.load(os.path.join('data', filename)).convert()
        self.screen = surface

    def imgat(self, rect, colorkey=None):
        rect = Rect(rect)
        image = pygame.Surface(rect.size).convert(self.screen)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    def imgsat(self, rects, colorkey=None):
        imgs = []
        for rect in rects:
            imgs.append(self.imgat(rect, colorkey))
        return imgs


class PlayerSprite(pygame.sprite.Sprite):
    """This sprite represents the player party in the overworld and exploration modes."""
    collisionrect: Rect  # The rectangle to be used for collisions. This should be slightly smaller than the sprite.
    image: pygame.Surface  # The sprite's currently active image.
    idles: List[pygame.Surface]  # Images to use as this sprite's idles.
    walk_south: List[pygame.Surface]  # The animation cycle to use when walking South.
    walk_north: List[pygame.Surface]  # The animation cycle to use when walking North.
    walk_east: List[pygame.Surface]  # The animation cycle to use when walking East.
    walk_west: List[pygame.Surface]  # The animation cycle to use when walking West.
    MOVERATE: int  # The number of pixels to move each frame when walking.
    del_x: int  # The number of pixels to move the sprite left or right.
    del_y: int  # The number of pixels to move the sprite up or down.
    facing: int  # The direction the sprite is facing. 0 = South, 1 = North, 2 = West, 3 = East
    anim_count: int  # The current animation frame.
    anim_delay: int  # How many cycles have passed since the last animation frame change.

    def __init__(self, location: Tuple[int, int], facing: int):
        # name: The name of the currently active party member.
        # location: The location to create the sprite at. When entering a new map, this will be the spawn point the
        #   party entered from. When re-initializing with a new active party member, this will be the prior
        #   location of the PlayerSprite object.
        pygame.sprite.Sprite.__init__(self, ENTITIES)  # Call the superclass constructor, passing it the ENTITIES group.
        self.rect = Rect(location[0], location[1], 64, 64)
        self.collisionrect = Rect(location[0] + 4, location[1] + 4, 60, 60)
        self.MOVERATE = 2

        # For now, default the spritesheet to Anna's sheet.
        # TODO: code to support Clara, Carter, and Wilhelm as active characters.
        sheet = SpriteSheet(os.path.join('sprites', 'anna_basic.png'), MAIN_DISPLAY)

        # Get the idle frames.
        self.idles = sheet.imgsat([Rect(0, 0, 32, 32),
                                   Rect(0, 32, 32, 32),
                                   Rect(0, 64, 32, 32),
                                   Rect(0, 96, 32, 32)], (0, 255, 255))

        # Get the frames for walking south.
        self.walk_south = sheet.imgsat([Rect(32, 0, 32, 32),
                                        Rect(64, 0, 32, 32),
                                        Rect(96, 0, 32, 32),
                                        Rect(128, 0, 32, 32),
                                        Rect(160, 0, 32, 32),
                                        Rect(192, 0, 32, 32)], (0, 255, 255))

        # Get the frames for walking north.
        self.walk_north = sheet.imgsat([Rect(32, 32, 32, 32),
                                        Rect(64, 32, 32, 32),
                                        Rect(96, 32, 32, 32),
                                        Rect(128, 32, 32, 32),
                                        Rect(160, 32, 32, 32),
                                        Rect(192, 32, 32, 32)], (0, 255, 255))

        # Get the frames for walking west.
        self.walk_west = sheet.imgsat([Rect(32, 64, 32, 32),
                                       Rect(64, 64, 32, 32),
                                       Rect(96, 64, 32, 32),
                                       Rect(128, 64, 32, 32),
                                       Rect(160, 64, 32, 32),
                                       Rect(192, 64, 32, 32)], (0, 255, 255))

        # Get the frames for walking east.
        self.walk_east = sheet.imgsat([Rect(32, 96, 32, 32),
                                       Rect(64, 96, 32, 32),
                                       Rect(96, 96, 32, 32),
                                       Rect(128, 96, 32, 32),
                                       Rect(160, 96, 32, 32),
                                       Rect(192, 96, 32, 32)], (0, 255, 255))

        self.facing = facing
        self.image = pygame.transform.scale2x(self.idles[self.facing])
        self.anim_count = 0
        self.anim_delay = 0
        self.del_x = 0
        self.del_y = 0

    def check_collision(self) -> bool:
        # Create a theoretical collision rectangle, based on facing.
        if self.del_y < 0:
            rect = Rect(self.rect.x + 4, self.rect.y, 60, 60 + 4)
        elif self.del_y > 0:
            rect = Rect(self.rect.x + 4, self.rect.y + 8, 60, 60 + 4)
        elif self.del_x < 0:
            rect = Rect(self.rect.x, self.rect.y + 4, 60 + 4, 60)
        elif self.del_x > 0:
            rect = Rect(self.rect.x + 8, self.rect.y + 4, 60 + 4, 60)
        else:
            rect = self.collisionrect

        for x in COLLISIONS:
            if rect.colliderect(x):
                return True

        return False

    def update(self):
        if not self.check_collision():
            self.rect.x += self.del_x
            self.rect.y += self.del_y
            self.collisionrect = Rect(self.rect.x + 4, self.rect.y + 4, 60, 60)
        if self.del_x == 0 and self.del_y == 0:
            self.image = pygame.transform.scale2x(self.idles[self.facing])
        elif self.del_y < 0:
            self.facing = 1
            if self.anim_delay < FRAMEDELAY:
                self.anim_delay += 1
            else:
                self.anim_delay = 0
                if self.anim_count < 5:
                    self.anim_count += 1
                else:
                    self.anim_count = 0

            self.image = pygame.transform.scale2x(self.walk_north[self.anim_count])
        elif self.del_y > 0:
            self.facing = 0
            if self.anim_delay < FRAMEDELAY:
                self.anim_delay += 1
            else:
                self.anim_delay = 0
                if self.anim_count < 5:
                    self.anim_count += 1
                else:
                    self.anim_count = 0

            self.image = pygame.transform.scale2x(self.walk_south[self.anim_count])
        elif self.del_x < 0:
            self.facing = 2
            if self.anim_delay < FRAMEDELAY:
                self.anim_delay += 1
            else:
                self.anim_delay = 0
                if self.anim_count < 5:
                    self.anim_count += 1
                else:
                    self.anim_count = 0

            self.image = pygame.transform.scale2x(self.walk_west[self.anim_count])
        elif self.del_x > 0:
            self.facing = 3
            if self.anim_delay < FRAMEDELAY:
                self.anim_delay += 1
            else:
                self.anim_delay = 0
                if self.anim_count < 5:
                    self.anim_count += 1
                else:
                    self.anim_count = 0

            self.image = pygame.transform.scale2x(self.walk_east[self.anim_count])


# Contains data for background tiles
class Tile:
    idcode: str  # A string ID representing the tile's tileset position, passability, type, and tileset.
    image: pygame.Surface  # A Surface object representing the tile's sprite.
    passable: bool  # Whether the tile can be traversed.

    def __init__(self, id: str):
        self.id = id
        tilerect = Rect(int(id[0:2]) * 32, int(id[2:4]) * 32, 32, 32)

        # Attempt to get an image for the tile. If it fails for any reason, call the invalidate() function.
        try:
            # TODO: Support for additional tilesets.
            tileset = SpriteSheet(SNOW_TILES, MAIN_DISPLAY)  # Get the sprite sheet for the Tile's tileset.
            self.image = tileset.imgat(tilerect, (0, 255, 255))
        except:
            self.invalidate()

        # Scale the tile image
        self.image = pygame.transform.scale2x(self.image)

        # Get whether the tile is passable
        if id[4] is 'f':
            self.passable = False
        else:
            self.passable = True

    # invalidate() re-initializes the tile as an impassable black square.
    def invalidate(self):
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((255, 255, 255))
        self.passable = False


class Map:
    """Data and methods for drawing the background and foreground layers. Map contains two 2D lists of Tile objects,
    as well as background and foreground surfaces to draw them to.

    TODO: Foreground Layer
    TODO: Map Scrolling"""
    background: pygame.Surface  # The background layer to be drawn to the game display.
    foreground: pygame.Surface  # The foreground layer to be drawn to the game display.
    backtiles: List[List]  # A two-dimensional list of Tile objects representing the background.
    foretiles: List[List]  # A two-dimensional list of Tile objects representing the foreground.
    encounter_rate: int  # The number of enemy encounters to spawn when entering this map.
    encounter_set: Set  # The set of encounters to draw from for this map.
    zone: str  # The zone that this map belongs to. Zones are collections of maps that represent towns, dungeons, etc.
    name: str  # The name of this map, if any.
    spawns: Dict  # The available spawn points for the player.

    def __init__(self, filename: str = None):
        self.background = pygame.Surface(SCREENRECT.size)
        self.background.fill((0, 0, 0))
        self.foreground = pygame.Surface(SCREENRECT.size)
        self.foreground.set_colorkey((0, 255, 255))
        self.foreground.fill((0, 255, 255))
        self.backtiles = list()
        self.foretiles = list()

        if filename is None:
            # generate a random assortment of snow and ice tiles, with each tile having a 50% chance of being
            # snow and a 50% chance of being ice.
            SNOW = '0000ts@snow'
            ICE = '0101fs@snow'
            roller = Random()

            for y in range(12):
                row = list()
                for x in range(16):
                    z = roller.randint(1, 100)
                    if z <= 70:
                        row.append(Tile(SNOW))
                    else:
                        row.append(Tile(ICE))
                self.backtiles.append(row)
        else:  # Initialize a map from .ini file
            # Open the map file.
            path = os.path.join('data', 'maps', filename)
            mapdata = open(path)

            # Header
            mapdata.readline()  # Section titles are included in map files for readability. Skip them.
            line = mapdata.readline()  # Get the header.
            splitline = line.split('|')  # Split the header line using pipes.
            self.zone = splitline[0]  # Get the zone name from the header line.

            # If a map name is specified, set self.name. Otherwise, declare that object as None.
            if splitline[1] is not 'none':
                self.name = splitline[1]
            else:
                self.name = None

            self.encounter_rate = int(splitline[2])  # Get the encounter rate from the header line.

            # TODO: When enemy encounters are implemented, get encounter sets from the header line.
            #  Encounter sets are generally universal for all maps within a zone.

            # Background
            mapdata.readline()  # Section titles are included in map files for readability. Skip them.

            # Each map in the game is at most 16 tiles by 12 tiles - the size of the game window.
            for y in range(12):
                line = mapdata.readline()  # Get a row of tile IDs.
                splitline = line.split('|')  # Break up the row using pipes.

                # Create a list representing the row of tiles. Check each line entry; a value of '00000000000' indicates
                # a null tile, while any other value should be passed to the Tile class's constructor.
                row = list()
                for x in range(16):
                    if splitline[x] == '00000000000':
                        row.append(None)
                    else:
                        row.append(Tile(splitline[x]))

                self.backtiles.append(row)

            # Foreground
            mapdata.readline()  # Section titles are included in map files for readability. Skip them.

            # Each map in the game is at most 16 tiles by 12 tiles - the size of the game window.
            for y in range(12):
                line = mapdata.readline()  # Get a row of tile IDs.
                splitline = line.split('|')  # Break up the row using pipes.

                # Create a list representing the row of tiles. Check each line entry; a value of '00000000000' indicates
                # a null tile, while any other value should be passed to the Tile class's constructor.
                row = list()
                for x in range(16):
                    if splitline[x] == '00000000000':
                        row.append(None)
                    else:
                        row.append(Tile(splitline[x]))

                self.foretiles.append(row)

            # Player Spawn Locations
            mapdata.readline()  # Section titles are included in map files for readability. Skip them.
            spawns = dict()
            reading = True
            while reading:
                line = mapdata.readline()
                if line == 'END OF FILE':
                    reading = False
                else:
                    splitline = line.split('|')
                    spawnpoint = (int(splitline[1]), int(splitline[2]))  # Get a tuple representing the spawn point.
                    spawns[splitline[0]] = spawnpoint  # Create a dictionary entry for the spawn point.

    def drawbgtile(self, tile: Tile, x: int, y: int):
        x_pos = x * 64
        y_pos = y * 64
        self.background.blit(tile.image, (x_pos, y_pos))

    def drawfgtile(self, tile: Tile, x: int, y: int):
        x_pos = x * 64
        y_pos = y * 64
        self.foreground.blit(tile.image, (x_pos, y_pos))

    def drawbg(self):
        for y in range(len(self.backtiles)):
            for x in range(len(self.backtiles[y])):
                if self.backtiles[y][x] is not None:
                    self.drawbgtile(self.backtiles[y][x], x, y)

    def drawfg(self):
        for y in range(len(self.foretiles)):
            for x in range(len(self.foretiles[y])):
                if self.foretiles[y][x] is not None:
                    self.drawfgtile(self.foretiles[y][x], x, y)


def compilecollision(map: Map):
    """Compile a set of rectangles representing collision zones."""

    # Clear the COLLISIONS set.
    COLLISIONS.clear()

    # Get rectangles for impassable map tiles.
    for y in range(12):
        for x in range(16):
            bounds = Rect(x * 64, y * 64, 64, 64)
            if map.backtiles[y][x] is None:
                if bounds not in COLLISIONS:
                    COLLISIONS.append(bounds)
            elif map.backtiles[y][x].passable is False:
                if bounds not in COLLISIONS:
                    COLLISIONS.append(bounds)
            if map.foretiles[y][x] is not None:
                if map.foretiles[y][x].passable is False:
                    if bounds not in COLLISIONS:
                        COLLISIONS.append(bounds)

    # TODO: Get collision rectangles for non-player Entities.

# Main game function.
def main():
    pygame.init()  # Initialize pygame
    MAIN_DISPLAY = pygame.display.set_mode(SCREENRECT.size)  # Initialize the game window.
    testmap = Map("northsalkstonmap.ini")  # The map to use for testing.
    player = PlayerSprite((512, 384), 0)
    compilecollision(testmap)  # Compile the initial collision set.
    gameclock = pygame.time.Clock()

    # Game loop
    while True:
        # Event Handling
        for event in pygame.event.get():
            # Quit the game if a QUIT event is read.
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Events fired when a pressed key is released.
            elif event.type == KEYUP:
                # If the escape key is pressed and released, quit the game.
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # If W, UP, S, or DOWN are released, stop the player sprite's vertical movement.
                if event.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN):
                    player.del_y = 0
                # If A, D, LEFT, or RIGHT are released, stop the player sprite's horizontal movement.
                if event.key in (pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT):
                    player.del_x = 0
                # If the SPACE key is released, set player's move speed back to normal.
                if event.key == pygame.K_SPACE:
                    player.MOVERATE = 2
                    if player.del_x < 0:
                        player.del_x = player.MOVERATE * -1
                    if player.del_x > 0:
                        player.del_x = player.MOVERATE
                    if player.del_y < 0:
                        player.del_y = player.MOVERATE * -1
                    if player.del_y > 0:
                        player.del_y = player.MOVERATE
            # Events fired when a key is pressed.
            elif event.type == KEYDOWN:
                # If W or UP are pressed, move the player sprite up and stop horizontal movement.
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.del_y = player.MOVERATE * -1
                    player.del_x = 0
                # If S or DOWN are pressed, move the player sprite down and stop horizontal movement.
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player.del_y = player.MOVERATE
                    player.del_x = 0
                # If A or LEFT are pressed, move the player sprite left and stop vertical movement.
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.del_y = 0
                    player.del_x = player.MOVERATE * -1
                # If S or RIGHT are pressed, move the player sprite right and stop vertical movement.
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.del_y = 0
                    player.del_x = player.MOVERATE
                # If SPACE is pressed, double the player sprite's move speed.
                if event.key == pygame.K_SPACE:
                    player.MOVERATE = 4
                    if player.del_x < 0:
                        player.del_x = player.MOVERATE * -1
                    if player.del_x > 0:
                        player.del_x = player.MOVERATE
                    if player.del_y < 0:
                        player.del_y = player.MOVERATE * -1
                    if player.del_y > 0:
                        player.del_y = player.MOVERATE

        # Update phase.
        testmap.drawbg()  # Update background.
        testmap.drawfg()  # Update foreground.
        compilecollision(testmap)  # Refresh collision rectangles.
        ENTITIES.update()  # Update entities.

        # Draw phase
        MAIN_DISPLAY.blit(testmap.background, (0, 0))  # Layer 0 - Background
        ENTITIES.draw(MAIN_DISPLAY)  # Layer 1 - Entities
        # TODO: Layer 2 - Entity Effects
        MAIN_DISPLAY.blit(testmap.foreground, (0, 0))  # Layer 3 - Foreground
        # TODO: Layer 3 - Foreground Effects
        # TODO: Layer 4 - Masks
        # TODO: Layer 5 - UI Frame
        # TODO: Layer 6 - UI Controls

        # Update the Display
        pygame.display.update()

        # Tick the clock. Standard speed is 60 FPS.
        gameclock.tick(60)


# Run line
main()
