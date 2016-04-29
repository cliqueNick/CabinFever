__author__ = 'ElectroNick'
import pygame


def intro():
    """
    Displays an introduction screen with text from a file.
    :return: if returns a string 'q' then the user has requested the entire program be ended immediately
    """
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption('Cabin Fever')
    pygame.mouse.set_visible(0)

# Create bhe background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

# Put Text On The Background
    title = pygame.font.Font(None, 36)
    text = title.render("Cabin Fever", 1, (10, 10, 10))  # with anti-aliasing in a dark gray color
    background.blit(text, text.get_rect(centerx=background.get_width()/2))
    paragraph = pygame.font.Font(None, 24)

    with open('data\\introduction.txt', mode='r') as intr:
        data = intr.readlines()

        # remove the new line characters
        da = []
        for d in data:
            ds = d.strip()
            da.append(ds)
        data = da

        # display the text on different lines
        i = 0
        for t in data:
            n_text = paragraph.render(t, 1, (10, 10, 10))  # with anti-aliasing in a dark gray color
            background.blit(n_text, n_text.get_rect(centery=20 * i + 40, left=30))
            i += 1

# Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Display until exit
    while True:
        for event in pygame.event.get():
            # exit the introduction
            if event.type == pygame.QUIT:  # if the window is closed
                return 'q'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # exits the program entirely if esc is pressed
                    return 'q'
                elif event.key == pygame.K_RETURN:
                    # play the game
                    return
                # TODO allow player to press buttons to change game settings here?