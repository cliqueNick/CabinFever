__author__ = 'ElectroNick'


import pygame
import math
import random
import MyGame_objects as Things
import MyGame_game_play as GPlay
import MyGame_intro as Intro
import sqlite3 as sql


def rand_position(view, background, amount=1):
    """
    Returns a random position within the view and background borders
    :param view: View object
    :param background: Background object
    :param amount: The number of positions generated inside a list. Starts counting at 1 not 0
    :return: List of the specified amount of random x,y value pair lists that fall within the view and background area
    """
    if amount >= 1:
        rand_p = []
        for s in range(amount):
            x = random.randint(0 + view.get_border(), background.rect.w - view.get_border())
            y = random.randint(0 + view.get_border(), background.rect.h - view.get_border())
            rand_p.append([x, y])
        return rand_p


def special_damage_effects(critical, broken):
    """
    Sets the special effects of damage to each body segment
    :param critical: A list of body segments that are in critical condition
    :param broken: A list of body segments that are broken and unusable
    :return: A list of booleans
    """
    # if critical or broken on body segment do effect
    slow = False
    blind = False
    numb_r = False
    numb_l = False
    if critical[0] or broken[0]:
        blind = True
    if critical[1]:
        slow = True
    if critical[2] or broken[2]:
        numb_r = True
    if critical[3] or broken[3]:
        numb_l = True
    if critical[4] or broken[4]:
        slow = True
    return [blind, slow, numb_r, numb_l, slow]


# The main loop
def main():
    """
    This function is called when the program starts.
    It initializes everything it needs, then runs the game in
    a loop until the function returns meaning the game ends.
    """

# set up variables
    # movement buttons
    buttons = GPlay.Buttons()
    buttons.set_move_buttons()  # use to set the buttons the player uses to move the main character
    keys = [False, False, False, False]  # initialize a list of the keyboard keys used for direction

    # screen parameters
    normal_border = 30 * 2  # border: minimum of 30 for MC.
    screen_width = 1000  # both must be a multiple of 200 pixels which is the grass
    screen_height = 600
    view = GPlay.Viewer(screen_width, screen_height, border=normal_border)

    pygame.mixer.init()
    music_file = """data\\Dvorak Symphony No.9 III Scherzo - Molto vivace (online-audio-converter.com).wav"""
    music = pygame.mixer.Sound(music_file)
    # freely available from: http://imslp.org/wiki/Symphony_No.9,_Op.95_%28Dvo%C5%99%C3%A1k,_Anton%C3%ADn%29
    music.set_volume(0.5)  # 0.0 - 1.0

# Initialize the game
    pygame.init()
    pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Cabin Fever')
    pygame.mouse.set_visible(0)  # do not show mouse

    # Background
    background = GPlay.Background('background\\large_grass.png')  # grassX4, 'test_map.png')
    map_pos_x = 0  # the inverted initial starting position of the main character
    map_pos_y = 0  # starts the main character at the top left corner of the map
    world = pygame.sprite.RenderPlain(background)


# Prepare Game Objects
    clock = pygame.time.Clock()
    eat = Things.Eating()

    # plants
    plants = Things.Group()
    number_plants = 10  # important for balancing the healing
    rand_pos = rand_position(view, background, amount=11)
    # puts item in a random place on the background
    for p in range(number_plants):  # in order of increasing size for proper overlapping
        plants.add(Things.Food('grain1', eat.kinds_of_food()[2], 'plants\\grain1.png', rand_pos[6], deviation=50))
    for p in range(number_plants):
        plants.add(Things.Food('grain2', eat.kinds_of_food()[2], 'plants\\grain2.png', rand_pos[7], deviation=50))
    for p in range(number_plants):
        plants.add(Things.Food('flower1', eat.kinds_of_food()[1], 'plants\\flower1.png', rand_pos[0], deviation=80))
    for p in range(number_plants):
        plants.add(Things.Food('flower2', eat.kinds_of_food()[1], 'plants\\flower2.png', rand_pos[1], deviation=80))
    for p in range(number_plants):
        plants.add(Things.Food('vine1', eat.kinds_of_food()[3], 'plants\\vine1.png', rand_pos[4], deviation=150))
    for p in range(number_plants):
        plants.add(Things.Food('vine2', eat.kinds_of_food()[3], 'plants\\vine2.png', rand_pos[5], deviation=150))
    for p in range(number_plants):
        plants.add(Things.Food('fruit1', eat.kinds_of_food()[0], 'plants\\fruit1.png', rand_pos[2], deviation=200))
    for p in range(number_plants):
        plants.add(Things.Food('fruit2', eat.kinds_of_food()[0], 'plants\\fruit2.png', rand_pos[3], deviation=200))

    # start the player in the center of the view
    mc_images = {"up": "main_character\\guy_up.png", "right": "main_character\\guy_right.png",
                 "left": "main_character\\guy_left.png", "down": "main_character\\guy_down.png"}

    mc = Things.MainCharacter(mc_images, start_pos=[screen_width / 2, screen_height / 2], speed=3)
    character = pygame.sprite.GroupSingle()  # only holds one sprite at a time or none
    character.add(mc)
    barrier = False
    run = False
    full_r = False
    full_l = False

    # foes
    wolves = Things.Group()
    birds = Things.Group()
    spiders = Things.Group()

    animal_images = {"up": "animals\\animal_up.png", "right": "animals\\animal_right.png",
                     "left": "animals\\animal_left.png", "down": "animals\\animal_down.png"}
    bird_images = {"up": "animals\\bird_up.png", "right": "animals\\bird_right.png",
                   "left": "animals\\bird_left.png", "down": "animals\\bird_down.png"}
    spider_images = {"up": "animals\\spider_up.png", "right": "animals\\spider_right.png",
                     "left": "animals\\spider_left.png", "down": "animals\\spider_down.png"}

    number_foes = 7
    rand_foe_pos = rand_position(view, background, amount=number_foes*3)
    for pace in range(number_foes):
        birds.add(Things.Foe(bird_images, start_pos=rand_foe_pos[pace]))
    for pace in range(number_foes):
        wolves.add(Things.Foe(animal_images, start_pos=rand_foe_pos[pace + number_foes]))
    for pace in range(number_foes):
        spiders.add(Things.Foe(spider_images, start_pos=rand_foe_pos[pace + number_foes * 2]))

    rand_pace = []
    for n in range(number_foes * 3):
        r = random.randint(10, 1000)
        rand_pace.append(r)
    foes = Things.Group()
    foes.add(wolves, birds, spiders)

    bird_damage = False
    wolf_damage = False
    spider_damage = False
    poisoned = False

    # balancing
    poison_time = 5  # number of seconds the poison acts
    p_strength = 55  # strength of the spider's poison

    # obstacles
    muddy = Things.Group()
    puddle = Things.Group()
    rand_mud_pos = rand_position(view, background, amount=3)
    for m in range(3):
        muddy.add(Things.Item("mud", "background\\mud.png", rand_mud_pos[m]))

    # house
    house_hold = Things.Group()
    my_house = Things.Item('house', "background\\house.png", [400, 100])
    house = Things.Group()
    house.add(my_house)

    # fire
    fires = Things.Group()
    fire_spread = 40
    progress(4, fires, puddle, fire_spread, view, background)

    ending = Things.Group()
    success = GPlay.HUD("background\\success.png", [0, 30])
    failure = GPlay.HUD("background\\failure.png", [0, 30])
    died = GPlay.HUD("background\\you_died.png", [0, 330])
    burned = GPlay.HUD("background\\house_burned_down.png", [0, 230])

    # inventory
    hold_right = pygame.sprite.GroupSingle()  # only holds one sprite at a time or None
    hold_left = pygame.sprite.GroupSingle()
    eat_right = pygame.sprite.GroupSingle()
    eat_left = pygame.sprite.GroupSingle()

    # The health bar
    damage = [0, 0, 0, 0, 0, False]
    healing = [0, 0, 0, 0, 0]
    poison_strength = 1
    green, orange, yellow, red = mc.health.all_hud()
    health_meter_green = pygame.sprite.RenderPlain(green)  # green is always on

    health_head_meter_orange = pygame.sprite.RenderPlain(orange[0])
    health_torso_meter_orange = pygame.sprite.RenderPlain(orange[1])
    health_r_arm_meter_orange = pygame.sprite.RenderPlain(orange[2])
    health_l_arm_meter_orange = pygame.sprite.RenderPlain(orange[3])
    health_legs_meter_orange = pygame.sprite.RenderPlain(orange[4])

    health_head_meter_yellow = pygame.sprite.RenderPlain(yellow[0])
    health_torso_meter_yellow = pygame.sprite.RenderPlain(yellow[1])
    health_r_arm_meter_yellow = pygame.sprite.RenderPlain(yellow[2])
    health_l_arm_meter_yellow = pygame.sprite.RenderPlain(yellow[3])
    health_legs_meter_yellow = pygame.sprite.RenderPlain(yellow[4])

    health_head_meter_red = pygame.sprite.RenderPlain(red[0])
    health_torso_meter_red = pygame.sprite.RenderPlain(red[1])
    health_r_arm_meter_red = pygame.sprite.RenderPlain(red[2])
    health_l_arm_meter_red = pygame.sprite.RenderPlain(red[3])
    health_legs_meter_red = pygame.sprite.RenderPlain(red[4])

    # holding pictures
    holding_r = GPlay.HUD('health_bar/holding_object.png', [19 * 2 + 26 - 10 + 2, 18 + 2 + 3])
    holding_l = GPlay.HUD('health_bar/holding_object.png', [19 - 19, 18 + 2 + 3])

    hold_r = pygame.sprite.RenderPlain(holding_r)
    hold_l = pygame.sprite.RenderPlain(holding_l)

    # text
    text_hud = pygame.Surface((600, 20))
    text_fill = (33, 177, 76)  # the background green color
    text_hud.fill(text_fill)
    text_hud.set_colorkey(text_fill)
    text_hud = text_hud.convert()
    text_position = (80, 10)

    progress_hud = pygame.Surface((600, 20))
    progress_position = (text_position[0], text_position[1] * 2 + 10)
    progress_hud.fill(text_fill)
    progress_hud.set_colorkey(text_fill)

    status_hud = pygame.Surface((600, 20))
    status_position = (text_position[0] - 5, text_position[1] * 3 + 10 * 2)
    status_hud.fill(text_fill)
    status_hud.set_colorkey(text_fill)

    pygame.font.init()
    font = pygame.font.Font(None, 22, bold=False)

    # clocks
    fire_timer = 0
    poison_counter = 0
    ouch_counter = 0
    ouch_flash_timer = 0
    run_timer = 0
    s = 0
    m = 0

    # introductory text screen
    q = Intro.intro()
    music.play(loops=-1)
    screen = pygame.display.set_mode((screen_width, screen_height))

    # delays the beginning of the game so the music starts when the picture does
    delay = True
    d_count = 0
    while delay:
        clock.tick(60)
        d_count += 1
        if d_count >= 60 * 2.5:  # 2.5 seconds
            delay = False
        if q == 'q':  # exits the program entirely if esc is pressed or window is closed
            return


# Main Loop
    while mc.health.get_alive():  # while True
        clock.tick(60)

        s += 1
        if s >= 60:  # cycles every second
            s = 0
        if s == 0:
            m += 1
        if m >= 60:  # cycles every minute
            m = 0

        # special effects
        status = ''
        special = special_damage_effects(mc.health.get_critical(), mc.health.get_broken())

        # Handle Input Events
        for event in pygame.event.get():
            # end the game
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            # get key presses
            if event.type == pygame.KEYDOWN:  # if a key is pressed down
                if event.key == buttons.get_up():  # up
                    keys[0] = True    # changes the first element of the keys list to true when the w button is pressed
                elif event.key == buttons.get_left():  # left
                    keys[1] = True
                elif event.key == buttons.get_down():  # down
                    keys[2] = True
                elif event.key == buttons.get_right():  # right
                    keys[3] = True
                elif event.key == buttons.get_run():
                    run = True

                # pick up item
                elif event.key == buttons.get_pickup_right():
                    # pick up item unless numb arm but can still eat what was already picked up
                    if special[2] is False and full_r is False:
                        chomp_r = pygame.sprite.groupcollide(plants, character,  True, False)  # pick up items
                        hold_right.add(chomp_r)  # adds first sprite in dictionary to inventory: plants
                        for spr in hold_right.sprites():
                            if str(spr).split()[0] not in eat.kinds_of_food():
                                full_r = True  # the hand is full
                elif event.key == buttons.get_pickup_left():
                    # pick up item unless numb arm but can still eat what was already picked up
                    if special[3] is False and full_l is False:
                        chomp_l = pygame.sprite.groupcollide(plants, character,  True, False)  # pick up items
                        hold_left.add(chomp_l)  # adds first sprite in dictionary to inventory: plants
                        for spr in hold_left.sprites():
                            if str(spr).split()[0] not in eat.kinds_of_food():
                                full_l = True  # the hand is full

                # eating
                if event.key == buttons.get_eat_right():  # picking up and eating could be the same button
                    for spr in hold_right.sprites():
                        if str(spr).split()[0] in eat.kinds_of_food():
                            eat_right.add(spr)
                            hold_right.empty()
                        elif str(spr).split()[0] not in eat.kinds_of_food():
                            if pygame.sprite.groupcollide(character, house, False, False):
                                # if touching the ship can place container in the ship
                                house_hold.add(spr)
                                hold_right.empty()
                                house_hold.empty()
                                full_r = False  # open hand
                                # remove fire
                                count_fire = 0
                                for f in fires:
                                    if count_fire >= 1:  # remove one at at time
                                        break
                                    else:
                                        fires.remove(f)
                                    count_fire += 1
                if event.key == buttons.get_eat_left():
                    for spr in hold_left.sprites():
                        if str(spr).split()[0] in eat.kinds_of_food():
                            eat_left.add(spr)
                            hold_left.empty()
                        elif str(spr).split()[0] not in eat.kinds_of_food():
                            if pygame.sprite.groupcollide(character, house, False, False):
                                house_hold.add(spr)
                                hold_left.empty()
                                house_hold.empty()
                                full_l = False  # open hand
                                # remove fire
                                count_fire = 0
                                for f in fires:
                                    if count_fire >= 1:
                                        break
                                    else:
                                        fires.remove(f)
                                    count_fire += 1
                # save
                elif event.key == buttons.get_save():
                    save_game_database(mc.health, map_pos_x, map_pos_y, mc.get_position(), len(fires.sprites()))
                    pass
                # open
                elif event.key == buttons.get_open():
                    th, map_pos_x, map_pos_y, place, f = open_game_database()
                    mc.health.reset_critical()
                    mc.health.reset_broken()
                    mc.health.open_health(th, 1135*5)
                    mc.set_position(place[0], place[1])

                    fires.empty()
                    puddle.empty()
                    for p in plants:
                        n = str(p).split()
                        if n[0] == 'puddle':
                            plants.remove(p)
                    progress(f, fires, puddle, fire_spread, view, background)
                    plants.add(puddle)
                    pass

                elif event.key == buttons.get_volume_down():
                    if music.get_volume() >= 0:
                        music.set_volume(music.get_volume() - 0.1)
                elif event.key == buttons.get_volume_up():
                    if music.get_volume() <= 1:
                        music.set_volume(music.get_volume() + 0.1)

            if event.type == pygame.KEYUP:  # When keys are not pressed down
                if event.key == buttons.get_up():  # up
                    keys[0] = False            # resets the keys list when the button is not pressed
                elif event.key == buttons.get_left():  # left
                    keys[1] = False
                elif event.key == buttons.get_down():  # down
                    keys[2] = False
                elif event.key == buttons.get_right():  # right
                    keys[3] = False

        # move background
        # prevent from moving off the screen, and move the background while limiting to the size of the background image
        # keeps the player in the boundaries of the background image
        if mc.get_position()[0] <= 0 + view.get_border():  # left
            # if negative then move (because opposite movement of MC), if positive do nothing
            keys[1] = False  # prevents from moving past border
            if background.get_position()[0] < 0:  # if edge of background is off the screen
                map_pos_x = background.get_position()[0] + mc.get_speed()
                # move background in equal and opposite direction as player
        if mc.get_position()[1] <= 0 + view.get_border():  # top
            keys[0] = False
            if map_pos_y < 0:
                map_pos_y = background.get_position()[1] + mc.get_speed()
        if mc.get_position()[0] >= view.get_screen_size()[0] - view.get_border():   # right
            keys[3] = False
            if math.fabs(map_pos_x) <= background.rect.w - view.get_screen_size()[0] - mc.get_speed():
                map_pos_x = background.get_position()[0] - mc.get_speed()
        if mc.get_position()[1] >= view.get_screen_size()[1] - view.get_border():  # bottom
            keys[2] = False
            if math.fabs(map_pos_y) <= background.rect.h - view.get_screen_size()[1] - mc.get_speed():
                map_pos_y = background.get_position()[1] - mc.get_speed()

        # Update locations
        pos = [map_pos_x, map_pos_y]
        world.update(pos)  # moves with the background
        plants.add(puddle)
        plants.update(pos)
        muddy.update(pos)
        puddle.update(pos)
        my_house.update(pos)
        fires.update(pos)

        # colliding
        stop = Things.Group()
        stop.add(pygame.sprite.groupcollide(character, muddy, False, False))
        for spr in stop.sprites():
            if 'Main Character' in str(spr):
                special[4] = True
        stop.empty()

        # running
        if run is True:  # the timer
            status += ' Running. '
            view.set_border(200)
            run_timer += 1
            if run_timer >= 60 * 2:  # 2 second
                run = False
                run_timer = 0
        if run is False:
            view.set_border(normal_border)

        # damage
        if pygame.sprite.groupcollide(character, birds, False, False):
            ouch_counter += 1
            if ouch_counter > 2:  # requires 2 consecutive hurtful seconds/60 in a row so not hurt when the game starts
                ouch_counter = 0
                bird_damage = True

        if pygame.sprite.groupcollide(character, wolves, False, False):
            ouch_counter += 1
            if ouch_counter > 2:  # so not hurt when the game starts
                ouch_counter = 0
                wolf_damage = True

        if pygame.sprite.groupcollide(character, spiders, False, False):
            ouch_counter += 1
            if ouch_counter > 3:  # so not hurt when the game starts
                ouch_counter = 0
                barrier = True
                spider_damage = True

        # Note: can't use the Timer class because need to reset critical inside what would be the internal code of Timer
        if delay is True:  # the timer
            ouch_flash_timer += 1
            if ouch_flash_timer >= 20:  # 1/3 of a second
                mc.health.reset_critical()  # reset the HUD
                delay = False
                ouch_flash_timer = 0

        if special[4] or special[1]:  # crippled: can't run
            run = False
            status += ' Crippled. '
        if special[2]:
            status += ' Left Arm Numb. '
        if special[3]:
            status += ' Right Arm Numb. '
        if poisoned:
            status += ' Poisoned. '

        # Time synced: damage, healing, eating
        if s == 1:  # every second
            # damage  # remember, damage is negative!
            if bird_damage:
                for b in birds:
                    damage = b.damage_high_accurate(damage, 0)
                bird_damage = False  # resets so only turned on once
            if wolf_damage:
                for w in wolves:
                    damage = [0, 0, 0, 0, 0, False]  # resets so only damages one body segment at a time
                    damage = w.damage_high_random(damage)
                wolf_damage = False
            if spider_damage:
                for sp in spiders:
                    damage, poison_strength, ouch_counter = sp.poison_damage(strength=p_strength)
                    poisoned = True

            if poisoned:
                poison_counter += 1
            if poison_counter >= poison_time:
                poison_counter = 0
                spider_damage = False
                poisoned = False

            if damage != [0, 0, 0, 0, 0, False]:  # start the timer
                ouch_flash_timer = 0
                delay = True

            # updating health
            mc.health.update(damage, healing, poison_strength=poison_strength)
            damage = [0, 0, 0, 0, 0, False]  # resets so only does damage when it is first initiated
            healing = [0, 0, 0, 0, 0]

            # eating food
            foods = ['']
            for f in eat_right.sprites():
                foods = str(f).split()
            for f in eat_left.sprites():
                foods = str(f).split()

            if foods[0] == eat.kinds_of_food()[0]:
                eat.fruit(mc)
            if foods[0] == eat.kinds_of_food()[1]:
                eat.root(mc)
            if foods[0] == eat.kinds_of_food()[2]:
                eat.grain(mc)
            if foods[0] == eat.kinds_of_food()[3]:
                eat.vegetable(mc)
            if foods[0] == eat.kinds_of_food()[4]:
                eat.meat(mc)

            eat_right.empty()  # resets the lists
            eat_left.empty()

        # Update MC and health
        mc.update(keys, stopped=barrier, running=run)  # tell the main character to move with the keys
        barrier = False  # resets the variable

        # increase fire
        if m == 1 and s == 1:  # once a minute
            fire_timer += 1
            if fire_timer >= 2:  # every 2 minutes
                progress(1, fires, puddle, fire_spread, view, background)
                fire_timer == 0

        # foe movement
        pace = 0
        for e in wolves:
            e.shape_pace_horizontal(pos, sec=rand_pace[pace])
            pace += 1
        for e in birds:
            e.shape_diamond(pos, sec=rand_pace[pace])
            pace += 1
        for e in spiders:
            e.shape_square(pos, sec=rand_pace[pace])
            pace += 1

        # Draw Everything
        world.draw(screen)
        plants.draw(screen)
        muddy.draw(screen)
        puddle.draw(screen)
        if special[0] is False:  # makes blind
            foes.draw(screen)
            character.draw(screen)
        else:
            status += ' Blind. '
        house.draw(screen)
        fires.draw(screen)

        text = str(mc.health)
        fires_text = 'Fires: ' + str(len(fires.sprites()))

        display_text = font.render(text, 1, (10, 10, 10))  # with anti-aliasing in a dark gray color
        display_progress = font.render(fires_text, 1, (10, 10, 10))
        display_status = font.render(status, 1, (10, 10, 10))

        text_hud.blit(display_text, display_text.get_rect())
        progress_hud.blit(display_progress, display_progress.get_rect())
        status_hud.blit(display_status, display_status.get_rect())

        screen.blit(text_hud, text_position)
        screen.blit(progress_hud, progress_position)
        screen.blit(status_hud, status_position)

        text_hud.fill(text_fill)
        progress_hud.fill(text_fill)
        status_hud.fill(text_fill)

        # Draw the health bar
        health_meter_green.draw(screen)
        o, y, r = mc.health.create_hud()

        if 0 in o:
            health_head_meter_orange.draw(screen)
        if 1 in o:
            health_torso_meter_orange.draw(screen)
        if 2 in o:
            health_r_arm_meter_orange.draw(screen)
        if 3 in o:
            health_l_arm_meter_orange.draw(screen)
        if 4 in o:
            health_legs_meter_orange.draw(screen)

        if 0 in y:
            health_head_meter_yellow.draw(screen)
        if 1 in y:
            health_torso_meter_yellow.draw(screen)
        if 2 in y:
            health_r_arm_meter_yellow.draw(screen)
        if 3 in y:
            health_l_arm_meter_yellow.draw(screen)
        if 4 in y:
            health_legs_meter_yellow.draw(screen)

        if 0 in r:
            health_head_meter_red.draw(screen)
        if 1 in r:
            health_torso_meter_red.draw(screen)
        if 2 in r:
            health_r_arm_meter_red.draw(screen)
        if 3 in r:
            health_l_arm_meter_red.draw(screen)
        if 4 in r:
            health_legs_meter_red.draw(screen)

        if hold_right:
            hold_r.draw(screen)
        if hold_left:
            hold_l.draw(screen)

        # ending
        if len(fires.sprites()) == 0:
            foes.empty()
            character.empty()
            ending.add(success)
            d_count = 0
            while True:
                clock.tick(60)
                ending.draw(screen)
                pygame.display.flip()
                d_count += 1
                if d_count >= 60 * 5:  # 5 seconds
                    return
                for event in pygame.event.get():  # closes the window earlier than the timer
                    if event.type == pygame.QUIT:
                        return
        elif len(fires.sprites()) >= 7:  # (7 - 4) * 2 = ends after 6 to 12 minutes of no progress
                ending.add(failure)
                ending.add(burned)
        elif mc.health.get_alive() is False:
                ending.add(failure)
                ending.add(died)
        if len(ending.sprites()) != 0:
                d_count = 0
                while True:
                    clock.tick(60)
                    ending.draw(screen)
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                    d_count += 1
                    if d_count >= 60 * 5:  # 5 seconds
                        return
                        # end of game

        # send everything to the screen

        pygame.display.flip()


def progress(number, fires, puddle, fire_spread, view, background):
    """
    Creates the fires and the puddles
    :param number: Amount of fires and puddles to be created
    :param fires: group to put fires into
    :param puddle: group to put puddles into
    :param fire_spread: The standard deviation for the random placement of the fire objects
    :param view: Boundary for the puddle objects
    :param background: Boundary for the puddle objects
    """
    for f in range(number):
        rx = random.normalvariate(400, fire_spread)
        ry = random.normalvariate(100, fire_spread)
        rand_fire = [rx, ry]
        fires.add(Things.Item('fire', "background\\fire4.png", rand_fire))
        # add puddle
        puddle.add(Things.Item("puddle", "background\\puddle.png", rand_position(view, background, amount=1)[0]))


def save_game_database(health, map_x, map_y, player_pos, containers):
    """
    Saves the game as a simple SQLite database with one row
    :param health: list of 5 integers
    :param map_x: integer
    :param map_y: integer
    :param player_pos: list of 2 integers
    """
    head = health.get_head_health()
    torso = health.get_torso_health()
    r_arm = health.get_right_arm_health()
    l_arm = health.get_left_arm_health()
    legs = health.get_legs_health()
    player_x = player_pos[0]
    player_y = player_pos[1]

    with open("data\\save.sqlite", 'w'):
        # makes it recreate the file each time so the state can be saved many times while running
        conn = sql.connect("data\\save.sqlite")
        curs = conn.cursor()
        initialize = """ CREATE TABLE if not EXISTS save_game (health_head int, health_torso int, health_r_arm int,"""
        initialize += """health_l_arm int, health_legs int, map_x int, map_y int, player_x int, """
        initialize += """player_y int, containers int)"""
        curs.execute(initialize)

        something = """ INSERT into save_game (health_head, health_torso, health_r_arm, health_l_arm, health_legs, """
        something += """map_x, map_y, player_x, player_y, containers) VALUES (?,?,?,?,?,?,?,?,?,?)"""
        curs.execute(something, (head, torso, r_arm, l_arm, legs, map_x, map_y, player_x, player_y, containers))
        conn.commit()
        curs.close()
        conn.close()


def open_game_database():
    """
    Opens the saved game from a simple SQLite database and returns values to restore the game to that level of progress,
    though the position of objects will be recreated randomly.
    :return:
    health: list of 5 integers to set the player's health
    map_x: integer to set the background position
    map_y: integer to set the background position
    player_pos: list of 2 integers to set the player position
    num_fires: integer used to randomly make fires
    """
    conn = sql.connect("data\\save.sqlite")
    curs = conn.cursor()
    curs.execute(""" SELECT * FROM save_game""")
    fetch = curs.fetchone()
    curs.close()
    conn.close()

    health = list(fetch[:5])
    map_x = fetch[5]
    map_y = fetch[6]

    player_x = fetch[7]
    player_y = fetch[8]
    player_pos = [player_x, player_y]
    num_fires = fetch[9]

    return health, map_x, map_y, player_pos, num_fires


# Game Over


# Required to run as a program not import
if __name__ == '__main__':
    main()