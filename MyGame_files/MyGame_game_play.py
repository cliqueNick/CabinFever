__author__ = 'ElectroNick'

import os
import pygame
import random
from pygame.locals import *
if not pygame.font:
    print 'Warning, fonts disabled'
if not pygame.mixer:
    print 'Warning, sound disabled'

# Resource handling classes


def load_image(name, color_key=None):
    """
    Taken from http://www.pygame.org/docs/tut/chimp/ChimpLineByLine.html
    :param name: File name. Assumed to be in the data directory.
    :param color_key: sets transparent color. Set to color in upper left corner if set to None
    :return: the image and its rectangular coordinates
    """
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit(message)
    image = image.convert()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, RLEACCEL)
    return image, image.get_rect()


# Basic game play functions
class Buttons(object):
    """
    Sets what each button does
    The default for the set_move_buttons function is the w, a, s, d key format
    """
    def __init__(self):
        """
        Initializes all the keys used in the game with defaults
        """
        self.__up = K_UP
        self.__down = K_DOWN
        self.__right = K_RIGHT
        self.__left = K_LEFT
        self.__run = K_SPACE
        self.__pick_up_R = K_v
        self.__pick_up_L = K_z
        self.__eat_R = self.__pick_up_R
        self.__eat_L = self.__pick_up_L
        self.__save = K_F1
        self.__open = K_F2
        self.__volume_down = pygame.K_LEFTBRACKET
        self.__volume_up = pygame.K_RIGHTBRACKET

    def set_move_buttons(self, up=K_w, down=K_s, right=K_d, left=K_a, run=K_SPACE, pickup_r=K_e, pickup_l=K_q,
                         auto_eat=False):
        """
        This function provides a quick way to change between the two common button layouts.
        When it is used it sets the movement to the a,s,d,w keys and the other buttons around these
        """
        self.__up = up
        self.__down = down
        self.__right = right
        self.__left = left
        self.__run = run
        self.__pick_up_R = pickup_r
        self.__pick_up_L = pickup_l
        self.auto_eat(auto_eat)

    def auto_eat(self, on, eat_r=K_r, eat_l=K_TAB):
        """
        An optional function that sets the picking up and using keys to be the same so only one key stroke is needed
        to pick up and eat for example.
        """
        if on:
            self.__eat_R = self.__pick_up_R
            self.__eat_L = self.__pick_up_L
        if on is False:
            self.__eat_R = eat_r
            self.__eat_L = eat_l

    def get_up(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__up

    def get_down(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__down

    def get_right(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__right

    def get_left(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__left

    def get_run(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__run

    def get_pickup_right(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__pick_up_R

    def get_pickup_left(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__pick_up_L

    def get_eat_right(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__eat_R

    def get_eat_left(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__eat_L

    def get_save(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__save

    def get_open(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__open

    def get_volume_down(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__volume_down

    def get_volume_up(self):
        """
        ":return: the integer representing the key chosen for this function
        """
        return self.__volume_up

    def __str__(self):
        """
        :return: A string providing the integer values for the keys currently being used
        """
        separator = " "
        s = ''
        s += str(self.get_up()) + separator + str(self.get_down()) + separator + str(self.get_right())
        s += separator + str(self.get_left()) + separator + str(self.get_run()) + separator
        s += str(self.get_pickup_right()) + separator + str(self.get_pickup_left())
        s += separator + str(self.get_eat_right()) + separator + str(self.get_eat_left())
        s += separator + str(self.get_save()) + separator
        s += str(self.get_open()) + separator + str(self.get_volume_down()) + separator + str(self.get_volume_up())
        return s


class Viewer(object):
    """
    Limits the movement of the player to what is visible
    """
    def __init__(self, screen_width, screen_height, border=0):
        """
        Initializes the screen
        """
        self.__border = border
        self.__set_screen_size(screen_width, screen_height, border=border)

    def get_border(self):
        """
        :return: The integer amount for the threshold around the border of the screen that the player can't cross
        """
        return self.__border

    def set_border(self, border):
        """
        Sets the integer amount for the threshold around the border of the screen that the player can't cross
        :param border: Must be a positive integer.
        """
        if border >= 0:
            self.__border = border

    def get_screen_size(self):
        """
        :return: A list containing representing the width and height of the window
        """
        return [self.__screen_width, self.__screen_height]

    def __set_screen_size(self, width, height, border=0):
        """
        :param width: sets the window width
        :param height: sets the window height
        :param border: Sets the integer amount for the threshold around the border of the screen that the player can't
            cross
        """
        self.__screen_width = width
        self.__screen_height = height
        self.__border = border


class Health(object):
    """
    Contains functions for damage and healing.
    Damage effects the specified body segment by the amount until reaches 0, then it damages the torso until dead.
    Also, reports when a body segment is critical or broken.
    """
    def __init__(self):
        """
        Initializes the health variables and the HUD pictures
        """
        self.__health_head = 21
        self.__health_torso = 28
        self.__health_right_arm = 14
        self.__health_left_arm = 14
        self.__health_legs = 21
        self.__total_health = self.get_health_total()  # total health: 98
        self.__low_health = 12
        self.__max_damage = -6
        self.__max_healing = 6  # the most healing allowed at once
        self.__max_health = 7*6  # max level of health at any time for each body segment.
        # Total = (max_health * 5) + (5 * max_healing)[for the last healing putting it above the max]
        # Total = 210 to 245 = 3.5 min to 4 min at max poison
        self.__alive = True
        self.__critical = [False, False, False, False, False]
        self.__broken = [False, False, False, False, False]

        self.torso_green = HUD('health_bar/torso_green.png', [19 + 1, 18])  # [19, 18] is against the top right corner
        self.head_green = HUD('health_bar/health_head_green.png', [self.torso_green.get_position()[0] + 5,
                                                                   self.torso_green.get_position()[1] - 18])
        self.right_arm_green = HUD('health_bar/arm_green.png', [self.torso_green.get_position()[0] + 26,
                                                                self.torso_green.get_position()[1] + 2])
        self.left_arm_green = HUD('health_bar/arm_green.png', [self.torso_green.get_position()[0] - 19,
                                                               self.torso_green.get_position()[1] + 2])
        self.legs_green = HUD('health_bar/legs_green.png', [self.torso_green.get_position()[0],
                                                            (self.torso_green.get_position()[1] + 2) * 2])

        self.torso_orange = HUD('health_bar/torso_orange.png', [self.torso_green.get_position()[0],
                                                                self.torso_green.get_position()[1]])
        self.head_orange = HUD('health_bar/health_head_orange.png', [self.head_green.get_position()[0],
                                                                     self.head_green.get_position()[1]])
        self.left_arm_orange = HUD('health_bar/arm_orange.png', [self.left_arm_green.get_position()[0],
                                                                 self.left_arm_green.get_position()[1]])
        self.right_arm_orange = HUD('health_bar/arm_orange.png', [self.right_arm_green.get_position()[0],
                                                                  self.right_arm_green.get_position()[1]])
        self.legs_orange = HUD('health_bar/legs_orange.png', [self.legs_green.get_position()[0],
                                                              self.legs_green.get_position()[1]])

        self.torso_yellow = HUD('health_bar/torso_yellow.png', [self.torso_green.get_position()[0],
                                                                self.torso_green.get_position()[1]])
        self.head_yellow = HUD('health_bar/health_head_yellow.png', [self.head_green.get_position()[0],
                                                                     self.head_green.get_position()[1]])
        self.left_arm_yellow = HUD('health_bar/arm_yellow.png', [self.left_arm_green.get_position()[0],
                                                                 self.left_arm_green.get_position()[1]])
        self.right_arm_yellow = HUD('health_bar/arm_yellow.png', [self.right_arm_green.get_position()[0],
                                                                  self.right_arm_green.get_position()[1]])
        self.legs_yellow = HUD('health_bar/legs_yellow.png', [self.legs_green.get_position()[0],
                                                              self.legs_green.get_position()[1]])

        self.torso_red = HUD('health_bar/torso_red.png', [self.torso_green.get_position()[0],
                                                          self.torso_green.get_position()[1]])
        self.head_red = HUD('health_bar/health_head_red.png', [self.head_green.get_position()[0],
                                                               self.head_green.get_position()[1]])
        self.left_arm_red = HUD('health_bar/arm_red.png', [self.left_arm_green.get_position()[0],
                                                           self.left_arm_green.get_position()[1]])
        self.right_arm_red = HUD('health_bar/arm_red.png', [self.right_arm_green.get_position()[0],
                                                            self.right_arm_green.get_position()[1]])
        self.legs_red = HUD('health_bar/legs_red.png', [self.legs_green.get_position()[0],
                                                        self.legs_green.get_position()[1]])

    def update(self, damage, healing, poison_strength=1):
        """
        Updated every second/60
        :param damage: List of damage done
        :param healing: List of healing done
        :param poison_strength: Integer from 1 to 64 that sets the probability of being poisoned
        """
        if damage[0] < 0:
            self.damage_head_health(damage[0])
        if damage[1] < 0:
            self.damage_torso_health(damage[1])
        if damage[2] < 0:
            self.damage_right_arm_health(damage[2])
        if damage[3] < 0:
            self.damage_left_arm_health(damage[3])
        if damage[4] < 0:
            self.damage_legs_health(damage[4])
        if damage[5] is True:
            self.poison(poison_strength)

        if healing[0] > 0:
            self.heal_head(healing[0])
        if healing[1] > 0:
            self.heal_torso(healing[1])
        if healing[2] > 0:
            self.heal_right_arm(healing[2])
        if healing[3] > 0:
            self.heal_left_arm(healing[3])
        if healing[4] > 0:
            self.heal_legs(healing[4])

    def get_health_total(self):
        """
        Sums up the health of the different body segments to get the total
        :return: integer of the total health
        """
        self.__total_health = self.__health_head + self.__health_torso + self.__health_right_arm
        self.__total_health += self.__health_left_arm + self.__health_legs
        return self.__total_health

    def get_head_health(self):
        """
        :return: The integer representing this body segment
        """
        return self.__health_head

    def get_torso_health(self):
        """
        :return: The integer representing this body segment
        """
        return self.__health_torso

    def get_right_arm_health(self):
        """
        :return: The integer representing this body segment
        """
        return self.__health_right_arm

    def get_left_arm_health(self):
        """
        :return: The integer representing this body segment
        """
        return self.__health_left_arm

    def get_legs_health(self):
        """
        :return: The integer representing this body segment
        """
        return self.__health_legs

    def get_alive(self):
        """
        :return: A boolean representing whether the character is alive
        """
        return self.__alive

    def get_critical(self):
        """
        :return: The list of critical body segments
        """
        return self.__critical

    def get_broken(self):
        """
        :return: The list of broken body segments
        """
        return self.__broken

    def open_health(self, health, use):
        """
        Changes the health when the save is opened
        """
        if use == 227*25:  # this is a simple pass code so not anyone can use this function
            if 0 <= health[0] <= self.__max_health:
                self.__health_head = health[0]
            if 0 <= health[1] <= self.__max_health:
                self.__health_torso = health[1]
            if 0 <= health[2] <= self.__max_health:
                self.__health_right_arm = health[2]
            if 0 <= health[3] <= self.__max_health:
                self.__health_left_arm = health[3]
            if 0 <= health[4] <= self.__max_health:
                self.__health_legs = health[4]
            else:
                print 'open error'

    def damage_head_health(self, amount):
        """
        This function causes the health to decrease for this body segment with the damage amount provided
        :param amount: Negative integer above the max possible damage
        """
        if self.__max_damage <= amount <= 0:  # if negative
            remaining = self.get_head_health() + amount  # adding a negative is subtracting
            self.__health_head = remaining
            self.__critical[0] = True
            if remaining <= 0:
                self.__broken[0] = True
                self.__health_head = 0
                self.damage_torso_health(0 + remaining)  # adding a negative is subtracting
        else:
            print "damage needs to be a negative number"

    def damage_torso_health(self, amount):
        """
        This function causes the health to decrease for this body segment with the damage amount provided
        :param amount: Negative integer above the max possible damage
        """
        if self.__max_damage <= amount <= 0:  # if negative
            remaining = self.get_torso_health() + amount
            self.__health_torso = remaining
            self.__critical[1] = True
            if self.get_torso_health() <= 0:
                self.__broken[1] = True
                self.__health_torso = 0
                self.__alive = False

    def damage_right_arm_health(self, amount):
        """
        This function causes the health to decrease for this body segment with the damage amount provided
        :param amount: Negative integer above the max possible damage
        """
        if self.__max_damage <= amount <= 0:  # if negative
            remaining = self.get_right_arm_health() + amount
            self.__health_right_arm = remaining
            self.__critical[2] = True
            if remaining <= 0:
                self.__broken[2] = True
                self.__health_right_arm = 0
                self.damage_torso_health(0 + remaining)

    def damage_left_arm_health(self, amount):
        """
        This function causes the health to decrease for this body segment with the damage amount provided
        :param amount: Negative integer above the max possible damage
        """
        if self.__max_damage <= amount <= 0:  # if negative
            remaining = self.get_left_arm_health() + amount
            self.__health_left_arm = remaining
            self.__critical[3] = True
            if remaining <= 0:
                self.__broken[3] = True
                self.__health_left_arm = 0
                self.damage_torso_health(0 + remaining)

    def damage_legs_health(self, amount):
        """
        This function causes the health to decrease for this body segment with the damage amount provided
        :param amount: Negative integer above the max possible damage
        """
        if self.__max_damage <= amount <= 0:  # if negative
            remaining = self.get_legs_health() + amount
            self.__health_legs = remaining
            self.__critical[4] = True
            if remaining <= 0:
                self.__broken[4] = True
                self.__health_legs = 0
                self.damage_torso_health(0 + remaining)

    def heal_head(self, amount):
        """
        This function causes the health to increase for this body segment with the healing amount provided
        :param amount: positive integer below the max possible healing at one time
        """
        if 0 <= amount <= self.__max_healing:  # if positive
            if self.__health_head <= self.__max_health:
                self.__health_head += amount
            if self.get_head_health() > 0:
                self.__broken[0] = False
        else:
            print "healing needs to be a positive number below " + str(self.__max_healing)

    def heal_torso(self, amount):
        """
        This function causes the health to increase for this body segment with the healing amount provided
        :param amount: positive integer below the max possible healing at one time
        """
        if 0 <= amount <= self.__max_healing:  # if positive
            if self.__health_torso <= self.__max_health:
                self.__health_torso += amount
            if self.get_torso_health() > 0:
                self.__broken[1] = False

    def heal_right_arm(self, amount):
        """
        This function causes the health to increase for this body segment with the healing amount provided
        :param amount: positive integer below the max possible healing at one time
        """
        if 0 <= amount <= self.__max_healing:  # if positive
            if self.__health_right_arm <= self.__max_health:
                self.__health_right_arm += amount
            if self.get_right_arm_health() > 0:
                self.__broken[2] = False

    def heal_left_arm(self, amount):
        """
        This function causes the health to increase for this body segment with the healing amount provided
        :param amount: positive integer below the max possible healing at one time
        """
        if 0 <= amount <= self.__max_healing:  # if positive
            if self.__health_left_arm <= self.__max_health:
                self.__health_left_arm += amount
            if self.get_left_arm_health() > 0:
                self.__broken[3] = False

    def heal_both_arms(self, amount):
        """
        This function passes the amount to heal to both the arms, so both are healed this amount
        :param amount: positive integer for the amount healed below the max possible healing at one time
        """
        self.heal_right_arm(amount)
        self.heal_left_arm(amount)

    def heal_legs(self, amount):
        """
        This function causes the health to increase for this body segment with the healing amount provided
        :param amount: positive integer below the max possible healing at one time
        """
        if 0 <= amount <= self.__max_healing:  # if positive
            if self.__health_legs <= self.__max_health:
                self.__health_legs += amount
            if self.get_legs_health() > 0:
                self.__broken[4] = False

    # TODO change poison to be an attribute that can be applied to any damage?
    def poison(self, strength=1):
        """
        while on is True, randomly damages body segments until death.
        The higher the strength the more likely it will cause damage.
        Probability is approximately exponential and ranges 0.08695 to 1
        It is suggested to stick with numbers divisible by 10 for round probabilities
        With poison_damage set to -1: (divide these by 6 for current values)
            At starting health takes about 3 min to kill with max strength
            At max health takes about 6.5 min to 7.4 min to kill with max strength

        :param on: boolean for whether to cause poison damage
        :param strength: Integer from 1 to 64 specifying the probability the poison will cause damage at any one time
        """
        poison_damage = self.__max_damage  # -6

        __s_max = 70 - 6  # = 64
        if strength < 1 or strength > __s_max:  # outer bounds inclusive
            strength = 1  # reset to lowest strength
            print 'poison strength out of bounds'
        strength = __s_max - strength  # the higher the strength the more powerful

        rand = random.randint(0, (5 + strength))  # 6/7 to 6/70 chance of doing damage
        if rand == 0:
            self.damage_head_health(poison_damage)
        elif rand == 1:
            self.damage_torso_health(poison_damage)
        elif rand == 2:
            self.damage_right_arm_health(poison_damage)
        elif rand == 3:
            self.damage_left_arm_health(poison_damage)
        elif rand == 4:
            self.damage_legs_health(poison_damage)
        elif rand == 5:
            self.damage_legs_health(poison_damage)  # modeling the two legs on a person

    @staticmethod
    def choose_damage(damage_amount, body_segment=-1):
        """
        Creates the damage list
        :param damage_amount: Amount damage inflicted. Must be negative.
        :param body_segment: The body segment where the damage will be applied.
        :return: A list of int and boolean values
        """
        damage = [0, 0, 0, 0, 0, False]

        if body_segment == -1:  # if random
            r = random.randint(0, 6)
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
        if choose == 5:
            damage[5] = True
        return damage

    def reset_critical(self):
        """
        Sets the internal critical list back to default
        """
        self.__critical = [False, False, False, False, False]

    def reset_broken(self):
        """
        Sets the internal broken list back to default
        """
        self.__broken = [False, False, False, False, False]

    def all_hud(self):
        """
        :return: Returns four lists containing the colored images for the body segments of the heads up display
        """
        green = [self.head_green, self.torso_green, self.right_arm_green, self.left_arm_green, self.legs_green]
        orange = [self.head_orange, self.torso_orange, self.right_arm_orange, self.left_arm_orange, self.legs_orange]
        yellow = [self.head_yellow, self.torso_yellow, self.right_arm_yellow, self.left_arm_yellow, self.legs_yellow]
        red = [self.head_red, self.torso_red, self.right_arm_red, self.left_arm_red, self.legs_red]
        return green, orange, yellow, red

    def create_hud(self):
        """
        Contains the logic to determine which HUD color to display for each body segment.
        :return: Three lists of integers that vary in length depending on which color other than green should be shown
        """

        orange = []
        yellow = []
        red = []

        if self.get_head_health() < self.__low_health:
            orange.append(0)
        if self.get_torso_health() < self.__low_health:
            orange.append(1)
        if self.get_right_arm_health() < self.__low_health:
            orange.append(2)
        if self.get_left_arm_health() < self.__low_health:
            orange.append(3)
        if self.get_legs_health() < self.__low_health:
            orange.append(4)

        if self.get_critical() != [False, False, False, False, False]:
            if self.get_critical()[0] is True and self.get_broken()[0] is False:
                yellow.append(0)
            if self.get_critical()[1] is True and self.get_broken()[1] is False:
                yellow.append(1)
            if self.get_critical()[2] is True and self.get_broken()[2] is False:
                yellow.append(2)
            if self.get_critical()[3] is True and self.get_broken()[3] is False:
                yellow.append(3)
            if self.get_critical()[4] is True and self.get_broken()[4] is False:
                yellow.append(4)

        if self.get_broken() != [False, False, False, False, False]:
            if self.get_broken()[0] is True:
                red.append(0)
            if self.get_broken()[1] is True:
                red.append(1)
            if self.get_broken()[2] is True:
                red.append(2)
            if self.get_broken()[3] is True:
                red.append(3)
            if self.get_broken()[4] is True:
                red.append(4)
        return orange, yellow, red

    def set_low_health(self, low):
        """
        Sets the threshold for the low health HUD to display
        :param low: must be a positive nonzero number below the maximum health allowed
        """
        if 0 < low < self.__max_health:
            self.__low_health = low

    def __str__(self):
        """
        :return: A string providing the named integer values for the health of each body segment
        """
        spacer = '   '
        r = 'Head: ' + str(self.get_head_health())
        r += spacer + 'Torso: ' + str(self.get_torso_health()) + spacer
        r += 'Right Arm: ' + str(self.get_right_arm_health())
        r += spacer + 'Left Arm: ' + str(self.get_left_arm_health()) + spacer + 'Legs: ' + str(self.get_legs_health())
        return r


class Background(pygame.sprite.Sprite):
    """moves the background on the screen """
    def __init__(self, image_file):
        """
        Initializes the background sprite
        """
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image(image_file)  # load_image('big_grass.png')
        self.__position = [0, 0]  # initial position is actually set by the main function

    def get_position(self):
        """
        :return: The internal x, y coordinates of the current position of the top left corner of the background
        """
        return self.__position

    def set_position(self, pos):
        """
        Sets the internal x, y coordinates of the current position of the top left corner of the background
        """
        self.__position = pos

    def update(self, pos):
        """
        This function is meant to be called every second/60 in the main function
        :param pos: sets the internal x, y coordinates and updates the position of the background's top left corner
        """
        self.set_position(pos)
        self.rect.topleft = self.get_position()


class HUD(pygame.sprite.Sprite):
    """
    The heads up display
    """
    def __init__(self, image_file, position):
        """
        Initializes the heads up display
        :param image_file: path to the image file
        :param position: sets the x, y coordinates of the sprite's top left corner
        """
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image, self.rect = load_image(image_file, -1)
        self.__position = position
        self.set_position(position)

    def get_position(self):
        """
        :return: the x, y coordinates of the sprite's top left corner
        """
        return self.__position

    def set_position(self, pos):
        """
        Sets the x, y coordinates of the sprite's top left corner
        """
        self.__position = pos
        self.rect.topleft = self.get_position()
