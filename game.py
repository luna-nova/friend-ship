# BattleShip game

# Importing required modules

from random import randint
from getch import getch, pause
import string, re, time, sys, os, subprocess

# grab the windows width
win_width = int(subprocess.check_output(['stty', 'size']).split()[1])

# Starting variables
dimensions = 0
game_grid = []
letters = "ABCDEFGHI"
ships = []
icons = {
    "checkmark": u'\u2713',
    "fill_square": u'\u2588',
}

pon = {
    "neutral": u'[\u25E6_\u25E6]',
    "unsure": u'[\u25E6~\u25E6]',
    "talk": u'[\u25E6\u25B4\u25E6]',
    "loud": u'[\u25E6\u2596\u25E6]',
    "areyoukidding": u'[\u2256_\u2256]',
    "on_to_you": u'[\u2256\u203F\u2256]',
    "reflect": u'[\u00B0-\u00B0]',
}

tee = {
    "smile": u'(\u02DA\u203F\u02DA)',
    "talk": u'(\u02DA\u25BF\u02DA)',
    "tinysmile": u'(\u02DA\u25E1\u02DA)',
    "wah": u'(\u02DA<\u02DA)',
    "yell": u'(\u02DA\u25B1 \u02DA)',
    "sad": u'(\u02DA\u2313 \u02DA)',
    "oh": u'(\u02DA\u25AB\u02DA)',
    "gasp": u'(\u02DA\u25C7\u02DA)',
    "dotdotdot": u'(\u02DA\u23BB\u02DA)',
}

# for face in tee:
#     print tee[face]
#
# print "\n"
#
# for face in pon:
#     print pon[face]

"""""""""""""""
GAME FUNCTIONS

"""""""""""""""

# main function for handling typing text and speech on screen
def text_typer(who, emotion, talkspeed, text, textspeed, delay, newline):
    time.sleep(delay)
    if newline == True:
        print "\n"
    if type(who) == str:
        if who == "Princess" and newline == True:
            sys.stdout.write(tee[emotion] + " ")
        elif who == "Kathy" and newline == True:
            sys.stdout.write(pon[emotion] + " ")
        subprocess.Popen('say -v %s -r %s %s' % (who, talkspeed, text), shell=True)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(textspeed)

# function to build the battlefield
def grid_setup(grid_dimensions):
    grid = []
    letter_setup = [" "]

    for x in xrange(grid_dimensions):
        letter_setup.append(letters[x])
        grid.append([str(x + 1)] + (["O"] * grid_dimensions))

    grid.insert(0, letter_setup)
    return grid

# prints out the current battlefield's status
def show_grid(grid):
    print "Current battlefield:\n"
    for row in grid:
        print " ".join(row)
    print "\n"

# clear the screen function
def clear_screen():
    os.system('clear')
    print "=" * win_width

# checks if the input recieved matches a ship coordinate/duplicate checking
def hit_check(coord_input):
    for ship in ships:
        for xy in ship["coords"]:
            if coord_input == xy:
                return True

# function to check if the input is valid
def coord_check(coord):
    if re.match(r"^[A-I][1-9]$", coord, flags=0):
        return True
    else:
        return False

def ship_generator(board_size):
    number_of_ships = board_size - 3
    alignments = ["left", "right", "up", "down"]

    while number_of_ships > 0:
        # if a generation iteration (lol) didn't work then reset variables and try again
        ship_length = randint(2, 4)
        align = 0
        ship_coords = []
        x_y = [randint(1, board_size), randint(1, board_size)]

        # is this number already a coordinate in the ships array?
        if hit_check(x_y) == True:
            continue

        # if not, continue!
        ship_coords.append(x_y)

        if x_y[0] - (ship_length - 1) < 1:
            alignments.remove("left")
        if x_y[0] + (ship_length - 1) > board_size:
            alignments.remove("right")
        if x_y[1] - (ship_length - 1) < 1:
            alignments.remove("up")
        if x_y[1] + (ship_length - 1) > board_size:
            alignments.remove("down")

        # if in the rare case that its 5x5 and a 4-length ship is generated in C3
        if len(alignments) == 0:
            alignments = ["left", "right", "up", "down"]
            continue

        align = alignments[randint(0, len(alignments) - 1)]

        for x in xrange(ship_length - 1):
            if align == "up":
                x_y = [ship_coords[x][0], ship_coords[x][1] - 1]
                if hit_check(x_y) == True:
                    break
            elif align == "right":
                x_y = [ship_coords[x][0] + 1, ship_coords[x][1]]
                if hit_check(x_y) == True:
                    break
            elif align == "down":
                x_y = [ship_coords[x][0], ship_coords[x][1] + 1]
                if hit_check(x_y) == True:
                    break
            elif align == "left":
                x_y = [ship_coords[x][0] - 1, ship_coords[x][1]]
                if hit_check(x_y) == True:
                    break
            ship_coords.append(x_y)

        if hit_check(x_y) == True:
            alignments = ["left", "right", "up", "down"]
            continue

        ships.append({"length": ship_length, "coords": ship_coords})
        if len(alignments) < 4:
            alignments = ["left", "right", "up", "down"]
        number_of_ships -= 1

    # just cause I like to see the ship coordinates
    print ships

def ship_hitting():
    guess = None
    guess_coord = None
    while 1:
        guess = raw_input("Enter an attack: ")
        if coord_check(guess) == False:
            print "That's not a valid attack! Try A4 or something."
            continue
        break
    guess_coord = [(letters.find(guess[0]) + 1), int(guess[1])]
    print guess_coord
    print guess
    if hit_check(guess_coord) == True:
        print "It's a hit!"
    else:
        print "It's a miss..."

# initializing function to start the game, asking for input
def start_game():
    clear_screen()
    board_dimensions = 0
    text_typer("Princess", "yell", 250, "WELCOME TO BATTLESHIP!", 0.06, 0, True)
    text_typer("Kathy", "talk", 150, "We are like... ", 0.09, 0, True)
    text_typer("Kathy", None, 180, "so glad to have you here. ", 0.07, 1, False)
    text_typer("Kathy", "loud", 180, "You can call me Pon.", 0.075, 0, True)
    text_typer("Princess", "talk", 220, "And my name is Tee!", 0.05, 0, True)
    print "\n"

    # continuous loop until user inputs a valid grid size
    while 1:
        try:
            board_dimensions = int(raw_input("> Enter board dimensions: "))
        except ValueError:
            print "> Please input a valid integer.\n"
            continue

        if board_dimensions < 5:
            print "The battlefield will be too small! Try bigger.\n"
            continue
        elif board_dimensions > 9:
            print "The battlefield will be too big... Try smaller.\n"
            continue

        dimensions = board_dimensions
        break

    game_grid = grid_setup(dimensions)
    text_typer(None, None, None, "Let's begin!", 0.1, 0, True)
    clear_screen()

    show_grid(game_grid)
    ship_generator(dimensions)
    print "Make your guesses like so: A1"
    print "You have 5 guesses for now."
    for x in xrange(5):
        ship_hitting()


"""""""""""""""
-----START-----
-----GAME!-----
"""""""""""""""

# clear the screen before starting
clear_screen()

try:
    start_game()

except KeyboardInterrupt:
    os.system('clear')
    subprocess.Popen('say -v Princess "Byeee! We\'ll see you later!"', shell=True)
    time.sleep(2.2)
    subprocess.call('say -v Kathy "Finally."', shell=True)
    sys.exit()
