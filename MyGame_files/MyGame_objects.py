__author__ = 'ElectroNick'

import pygame
import random
import MyGame_game_play as GPlay


# Game object classes


class Animal(pygame.sprite.Sprite):
    """
    Parent class for all moving entities
    """
    def __init__(self, image_files, start_pos=(0, 0), speed=3):
        """
        Initializes the sprite
        :param image_files: list of file paths for images facing each direction starting from the current working
            directory
        :param start_pos: list specifying the initial position when the game starts
        :param speed: how fast it can move initially
        """
        pygame.sprite.Sprite.__init__(self)
        self.__rotate = 0  # for rotating the image with the key presses
        self.__position = list(start_pos)  # the initial position
        self.__background_position = [0, 0]
        self.__actual_position = [0, 0]
        self.__walk_speed = speed  # the base speed
        self.__speed = self.__walk_speed
        self.__run_speed = speed * 2
        self.__keys = [False, False, False, False]
        self.health = GPlay.Health()  # the separate Health class keeps vital variables private

        self.__guy_up, self.__guy_up_rect = GPlay.load_image(image_files['up'], -1)
        self.__guy_right, self.__guy_right_rect = GPlay.load_image(image_files['right'], -1)
        self.__guy_left, self.__guy_left_rect = GPlay.load_image(image_files['left'], -1)
        self.__guy_down, self.__guy_down_rect = GPlay.load_image(image_files['down'], -1)
        self.image = self.__guy_up  # the initial image before movement
        self.rect = self.__guy_up_rect

    def get_position(self):
        """This function is returned every second/60 in the update function"""
        return self.__position

    def set_position(self, x, y):
        """
        Sets the internal position variables for the object
        :param x: x axis
        :param y: y axis
        """
        self.__position[0] = x  # left and right movement
        self.__position[1] = y  # up and down movement

    def get_background_position(self):
        """

        :return:  a list of x and y coordinates
        """
        return self.__background_position

    def set_background_position(self, position):
        """
        Updated every second/60 so the sprite moves with the background
        :param position: a list of x and y coordinates of the background
        """
        self.__background_position[0] = position[0]  # left and right movement
        self.__background_position[1] = position[1]  # up and down movement

    def get_speed(self):
        """
        :return: The current speed integer
        """
        return self.__speed

    def set_speed(self, speed):
        """
        Sets the speed for walking and running as well as the current speed.
        The running speed is twice the walking speed.
        :param speed: between 0 and 15
        """
        if 0 <= speed <= 15:  # max speed
            self.__speed = speed  # changes the speed variable below
            self.__walk_speed = speed
            self.__run_speed = speed * 2

    def get_keys(self):
        """
        :return: list of booleans representing key presses in each cardinal direction
        """
        return self.__keys

    def set_keys(self, keys):
        """
        :param keys: list of booleans representing key presses in each cardinal direction
        """
        self.__keys = keys

    def change_direction(self, keys):
        """
        Updates the sprite direction and changes the image to point towards it.
        :param keys: A list of key presses for each ordinal direction.
        """
        self.set_keys(keys)

        # change the direction of the image
        keys = self.get_keys()
        if keys[0] is True:
            self.image = self.__guy_up  # up
            self.rect = self.__guy_up_rect
        if keys[3] is True:
            self.image = self.__guy_right  # right
            self.rect = self.__guy_right_rect
        if keys[2] is True:
            self.image = self.__guy_down  # down
            self.rect = self.__guy_down_rect
        if keys[1] is True:
            self.image = self.__guy_left  # left
            self.rect = self.__guy_left_rect

    def update(self, keys, background_position=None, stopped=False, running=False):
        """
        Moves the sprite's position with the keys at walking or running speed except when stopped is True
        Can be set to move with the background.
        :param keys: A list of key presses for each ordinal direction.
        """
        if background_position is None:
            background_position = [0, 0]

        self.change_direction(keys)
        self.set_background_position(background_position)
        x, y = self.get_position()
        cx, cy = x, y
        keys = self.get_keys()

        if running is True:
            self.__speed = self.__run_speed
        else:
            self.__speed = self.__walk_speed

        # changes position
        if keys[0]:    # up
            y -= self.__speed
        elif keys[2]:  # down
            y += self.__speed
        if keys[1]:    # left
            x -= self.__speed
        elif keys[3]:  # right
            x += self.__speed
        self.set_position(x, y)

        if stopped is True:
            self.set_position(cx, cy)  # if stopped then does not change the position

        self.__actual_position = [self.get_position()[0] + self.get_background_position()[0],
                                  self.get_position()[1] + self.get_background_position()[1]]
        self.rect.center = self.__actual_position

    def __str__(self):
        """
        String representation for the object
        :return: the current position of the object as a unique identifier
        """
        return str(self.__actual_position)


class MainCharacter(Animal):
    """The main character"""
    def __init__(self, image_files, start_pos=(0, 0), speed=3):
        """
        Initializes the sprite
        :param image_files: list of file paths for images facing each direction starting from the current working
            directory
        :param start_pos: list specifying the initial position when the game starts
        :param speed: how fast it can move initially
        """
        Animal.__init__(self, image_files, start_pos=start_pos, speed=speed)

    def __str__(self):
        """
        Identifies its self as the Main Character
        :return: the words "Main Character" and its current position
        """
        return 'Main Character: ' + Animal.__str__(self)


class Foe(Animal):
    """
    Class for every sprite that moves and does damage to the player
    """
    def __init__(self, image_files, start_pos=(0, 0), speed=3):
        """
        Initializes the sprite
        :param image_files: list of file paths for images facing each direction starting from the current working
            directory
        :param start_pos: tuple specifying the initial position when the game starts
        :param speed: how fast it can move initially
        """
        Animal.__init__(self, image_files, start_pos=start_pos, speed=speed)
        self.keys = [False, False, False, False]
        self.count = 0
        self.turn = 0
        self.min_damage = 2  # absolute value
        self.max_damage = 6

    def __str__(self):
        """
        Identifies its self as a foe
        :return: the words "Foe" and its current position
        """
        return 'Foe: ' + Animal.__str__(self)

    def move(self, background_pos, sec=60):
        """
        Moves the sprite against the background
        :param background_pos: current background position coordinates so can move with it
        :param sec: how long it should take the sprite to complete one loop of movement
        """
        if sec < 0:  # if negative
            sec = 0
        if self.turn >= sec:  # seconds/60  # the bigger, the wider the path
            self.turn = 0
        if self.count > 3:
            self.count = 0

        self.update(self.keys, background_position=background_pos)  # moves with the background

        if self.turn == 1:
            self.count += 1
        self.turn += 1

    def stand_still(self, background_position):
        """
        No movement
        :param background_position: coordinates to make it move with the background
        """
        self.move(background_position)
        self.keys = [False, False, False, False]

    def shape_square(self, background_position, sec=60):
        """
        Moves the sprite Clockwise in a square
        :param background_position: coordinates to make it move with the background
        :param sec: how long it should take the sprite to complete one loop of movement
        """
        self.move(background_position, sec=sec)
        if self.count == 0:
            self.up()
        elif self.count == 1:
            self.right()
        elif self.count == 2:
            self.down()
        elif self.count == 3:
            self.left()

    def shape_diamond(self, background_position, sec=60):
        """
        Moves the sprite Clockwise in a diamond
        :param background_position: coordinates to make it move with the background
        :param sec: how long it should take the sprite to complete one loop of movement
        """
        self.move(background_position, sec=sec)
        if self.count == 0:
            self.up_right()
        elif self.count == 1:
            self.down_right()
        elif self.count == 2:
            self.down_left()
        elif self.count == 3:
            self.up_left()

    def shape_pace_horizontal(self, background_position, sec=60):
        """
        Moves the sprite back and forth horizontally
        :param background_position: coordinates to make it move with the background
        :param sec: how long it should take the sprite to complete one loop of movement
        """
        self.move(background_position, sec=sec)
        if self.count == 0:
            self.right()
        elif self.count == 2:
            self.left()

    def shape_pace_vertical(self, background_position, sec=60):
        """
        Moves the sprite back and forth vertically
        :param background_position: coordinates to make it move with the background
        :param sec: how long it should take the sprite to complete one loop of movement
        """
        self.move(background_position, sec=sec)
        if self.count == 0:
            self.up()
        elif self.count == 2:
            self.down()

    def up(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [True, False, False, False]

    def left(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [False, True, False, False]

    def down(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [False, False, True, False]

    def right(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [False, False, False, True]

    def up_left(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [True, True, False, False]

    def down_left(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [False, True, True, False]

    def down_right(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [False, False, True, True]

    def up_right(self):
        """
        sets the internal key list to move the specified direction
        """
        self.keys = [True, False, False, True]

    @staticmethod
    def __choose_damage(damage, damage_amount, body_segment=-1):
        """
        Sets the damage list
        :param damage: Takes the current damage list
        :param damage_amount: amount of damage to be done
        :param body_segment: specifies which body segment to damage
        :return: the damage list
        """
        # remember, damage is negative!
        if body_segment == -1:  # if random
            r = random.randint(0, 4)  # inclusive
            choose = r
        else:
            choose = body_segment

        if choose == 0:
            damage[0] = damage_amount
        if choose == 1:
            damage[1] = damage_amount
        if choose == 2:
            damage[2] = damage_amount
        if choose == 3:
            damage[3] = damage_amount
        if choose == 4:
            damage[4] = damage_amount
        return damage

    def damage_low_random(self, damage):
        """
        Preset damage type
        :param damage: Takes the current damage list
        :return: the new damage list reflecting the changes
        """
        d = random.randint(1, self.min_damage)
        d = -d
        return self.__choose_damage(damage, d)

    def damage_high_random(self, damage):
        """
        Preset damage type
        :param damage: Takes the current damage list
        :return: the new damage list reflecting the changes
        """
        d = random.randint(self.min_damage, self.max_damage)
        d = -d
        return self.__choose_damage(damage, d)

    def damage_low_accurate(self, damage, body_segment):
        """
        Preset damage type
        :param damage: Takes the current damage list
        :param body_segment: the number of the body segment to be damaged
        :return: the new damage list reflecting the changes
        """
        d = random.randint(1, self.min_damage)
        d = -d
        return self.__choose_damage(damage, d, body_segment=body_segment)

    def damage_high_accurate(self, damage, body_segment):
        """
        Preset damage type
        :param damage: Takes the current damage list
        :param body_segment: the number of the body segment to be damaged
        :return: the new damage list reflecting the changes
        """
        d = random.randint(self.min_damage, self.max_damage)
        d = -d
        return self.__choose_damage(damage, d, body_segment=body_segment)

    @staticmethod
    def poison_damage(strength=1):
        """
        Sets the poison variable to true in the damage list
        :param strength: the strength of the poison from 1 to 64
        :return: the new damage list reflecting the changes
        """
        damage = [0, 0, 0, 0, 0, True]
        timer = 0
        return damage, strength, timer


class Item(pygame.sprite.Sprite):
    """
    General class for sprite objects that stay stationary with the background
    """
    def __init__(self, name, image_file, start_pos):
        """
        Initializing the sprite
        :param name: String to identify the sprite when it is in a group
        :param image_file: Path to the image
        :param start_pos: Initial starting coordinates list
        """
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = GPlay.load_image(image_file, -1)
        self.__position = [0, 0]  # current position as it moves with the background
        self.__start_pos = start_pos
        self.__name = name

    def update(self, background_pos):
        """
        Moves the item with the background
        :param background_pos: Coordinates of the background
        """
        if self.__start_pos >= 0:
            pos = [self.__start_pos[0] + background_pos[0], self.__start_pos[1] + background_pos[1]]
            self.set_position(pos)
        self.rect.center = self.get_position()

    def get_position(self):
        """
        :return: List of coordinates for current position
        """
        return self.__position

    def set_position(self, pos):
        """
        Sets the internal position coordinate
        :param pos: list of x, y coordinates
        """
        self.__position = pos

    def get_start_position(self):
        """
        :return: List of coordinates for initial position
        """
        return self.__start_pos

    def set_start_position(self, pos):
        """
        Sets the initial internal position coordinate
        :param pos: list of x, y coordinates
        """
        self.__start_pos = pos

    def __str__(self):
        """
        :return: String of object's name and its position
        """
        return self.__name + " " + str(self.get_position())


class Food(Item):
    """
    General class for sprites that can be eaten
    """
    def __init__(self, name, kind, image_file, start_pos, deviation=70):
        """
        Initializes the sprite in a random position around the start position
        :param name: string name of the object
        :param kind: integer specifying what kind of food it is
        :param image_file: Path to the image file
        :param start_pos: List of start position coordinates
        :param deviation: Standard Deviation of the random position around the start_pos
        """
        Item.__init__(self, name, image_file, [0, 0])
        self.__set_rand_position(start_pos, deviation=deviation)
        self.eat = Eating()
        self.__kind = ""
        self.__set_kind(kind)

    def __set_rand_position(self, position, deviation=70):
        """
        Models the location of plants to each other in nature using a normal distribution from the given position.
        Designed so all sprites of a given kind are given the same seed position.
        :param position: list of x, y
        :param deviation: size of one standard deviation
        """
        stdev = 1
        if deviation >= 0:
            stdev = deviation
        rx = random.normalvariate(position[0], stdev)
        ry = random.normalvariate(position[1], stdev)
        self.set_start_position([rx, ry])

    def get_kind(self):
        """
        :return: string representing what kind of food it is
        """
        return self.__kind

    def __set_kind(self, kind):
        """
        :param kind: a string that must be an official kind of food for the game
        :return: None or "Error: not an official kind of food"
        """
        if kind in self.eat.kinds_of_food():
            self.__kind = kind
        else:
            return "Error: not an official kind of food"

    def __str__(self):
        """
        :return: String of object's name and its position
        """
        return self.get_kind() + " " + Item.__str__(self)


class Group(pygame.sprite.Group):
    """
    Provides a shorthand notation for the Group object which can hold many sprites
    """
    def __init__(self):
        """
        initializes the Group object
        """
        pygame.sprite.Group.__init__(self)


class Eating(object):
    """
    General class for the logic of what food does to health when it is eaten
    """
    def __init__(self):
        """
        initializes the internal variables
        """
        self.min_heal = 1
        self.max_heal = 3

    @staticmethod
    def kinds_of_food():
        """
        Sets the names of the kinds of food available
        :return: List of strings
        """
        return ['fruit', 'root', 'grain', 'vegetable', 'meat']

    def fruit(self, subject):
        """
        Heals the subject's legs and head
        :param subject: usually the main character
        """
        subject.health.heal_legs(self.max_heal)
        subject.health.heal_head(self.min_heal)

    def root(self, subject):
        """
        Heals the subject's head and both arms
        :param subject: usually the main character
        """
        subject.health.heal_head(self.max_heal)
        subject.health.heal_both_arms(self.min_heal)

    def grain(self, subject):
        """
        Heals the subject's both arms and legs
        :param subject: usually the main character
        """
        subject.health.heal_both_arms(self.max_heal)
        subject.health.heal_legs(self.min_heal)

    def vegetable(self, subject):
        """
        Heals the subject's a random body segment and the torso
        :param subject: usually the main character
        """
        subject.health.heal_torso(self.min_heal)

        # random benefit
        benefit = random.randint(0, 5)
        if benefit == 0:
            subject.health.heal_legs(self.max_heal)
        elif benefit == 1:
            subject.health.heal_head(self.max_heal)
        elif benefit == 2:
            subject.health.heal_right_arm(self.max_heal)
        elif benefit == 3:
            subject.health.heal_left_arm(self.max_heal)
        elif benefit == 4 or benefit == 5:
            subject.health.heal_torso(self.max_heal)

    def meat(self, subject):  # not currently used
        """
        Heals the subject's torso
        :param subject: usually the main character
        """
        subject.health.heal_torso(self.max_heal)